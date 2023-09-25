import logging
import os
from heapq import nlargest
from pathlib import Path
from string import punctuation as punct
from typing import Union, Dict
import uuid

import nltk
import tiktoken
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from docx import Document
from fastapi import HTTPException, status
from langchain import HuggingFaceHub
from langchain.chains import RetrievalQA
from langchain.chains.question_answering import load_qa_chain
from langchain.document_loaders import PyPDFLoader, TextLoader, WebBaseLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS

from src.conf.logger import get_logger
from src.conf.config import settings
from src.conf import constants, messages


EMBEDDINGS = OpenAIEmbeddings(openai_api_key=settings.openai_api_key)
nltk.download('punkt')
nltk.download('stopwords')


def get_token_summary(string: str, encoding_name: str = "cl100k_base") -> dict:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))

    price = 0.0001  # 0.0001 USD per 1000 tokens
    token_summary = {
        '1K/tokens': num_tokens / 1000,
        '$price 1K/tokens': price,
        'Total_cost(USD)': num_tokens / 1000 * price
    }
    return token_summary


async def convert_document_to_vector_db(file_path: Union[str, Path], document_id: int) -> HTTPException | Dict:
    file_path = str(file_path)
    if file_path.lower().endswith(".pdf"):
        loader = PyPDFLoader(file_path)
        pages = loader.load_and_split()

    elif file_path.lower().endswith(".docx") or file_path.lower().endswith(".doc"):
        word_doc = Document(file_path)
        passages = [p.text for p in word_doc.paragraphs]
        content = "\n".join(passages)
        file_txt_path = constants.VECTOR_DB_PATH / f"temp/{uuid.uuid4()}.txt"

        with open(file_txt_path, "w") as f:
            f.write(content)

        loader = TextLoader(file_txt_path)
        pages = loader.load()
        os.remove(file_txt_path)

    elif file_path.lower().endswith(".txt"):
        loader = TextLoader(file_path)
        pages = loader.load()

    elif "http:" in file_path.lower() or "https:" in file_path.lower() or "www." in file_path.lower():
        loader = WebBaseLoader(web_path=file_path)
        pages = loader.load()

    else:
        return HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail=messages.FILE_TYPE_IS_NOT_SUPPORTED)

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1024,
        chunk_overlap=64,
        separators=['\n\n', '\n', '(?=>\. )', ' ', '']
    )

    # Split the pages into texts as defined above
    texts = text_splitter.split_documents(pages)

    # Create/update the vector store
    vector_db = FAISS.from_documents(texts, EMBEDDINGS)
    vector_db.save_local(constants.VECTOR_DB_PATH, index_name=(str(document_id)))

    full_text = ""
    for i in range(len(texts) - 1):
        full_text += texts[i].page_content
    return get_token_summary(full_text)


async def load_vector_db(document_id: int):
    if (not Path(f"{constants.VECTOR_DB_PATH}/{document_id}.faiss").exists()
            or not Path(f"{constants.VECTOR_DB_PATH}/{document_id}.pkl").exists()):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.VECTOR_DB_NOT_FOUND)

    return FAISS.load_local(folder_path=constants.VECTOR_DB_PATH,
                            index_name=str(document_id),
                            embeddings=EMBEDDINGS
                            )


async def delete_vector_db(document_id: int):
    try:
        os.remove(constants.VECTOR_DB_PATH / f"{document_id}.faiss")
        os.remove(constants.VECTOR_DB_PATH / f"{document_id}.pkl")
    except FileNotFoundError as err:
        logger = get_logger("Not found")
        logger.log(level=logging.DEBUG, msg=str(err))


async def answer_generate(document_id: int, question: str) -> Dict:
    vector_db = await load_vector_db(document_id)

    llm = HuggingFaceHub(huggingfacehub_api_token=settings.huggingfacehub_api_token,
                         repo_id="tiiuae/falcon-7b",
                         model_kwargs={"temperature": 0.5,
                                       "max_length": 512,
                                       "max_new_tokens": 200
                                       })

    memory = ConversationBufferMemory(memory_key="chat_history")
    qa_chain = load_qa_chain(llm=llm, chain_type="stuff")

    qa = RetrievalQA(combine_documents_chain=qa_chain,
                     retriever=vector_db.as_retriever(),
                     memory=memory)

    results = qa({"query": question})
    return {"answer": results['result'],
            "chat_history": results['chat_history']}


async def get_text_by_document(document_id: int) -> str:
    vector_db = await load_vector_db(document_id)
    docs = vector_db.similarity_search_with_score('', k=10000)
    text_load = ''
    for i in range(len(docs) - 1):
        text_load += docs[i][0].page_content

    return text_load


async def text_summary_generate(text: str, sentences_count: int = constants.DEFAULT_SUMMARY_SENTENCES_COUNT) -> str:
    punctuation = punct
    punctuation = punctuation + '\n'

    nltk_tokens = word_tokenize(text)
    sentences_list = sent_tokenize(text)

    nltk_stop_words = set(stopwords.words('english'))

    nltk_word_frequencies = {}
    for word in nltk_tokens:
        if word.lower() not in nltk_stop_words:
            if word.lower() not in punctuation:
                if word not in nltk_word_frequencies.keys():
                    nltk_word_frequencies[word] = 1
                else:
                    nltk_word_frequencies[word] += 1

    nltk_max_frequency = max(nltk_word_frequencies.values())
    for word in nltk_word_frequencies.keys():
        nltk_word_frequencies[word] = nltk_word_frequencies[word] / nltk_max_frequency

    nltk_sentence_score = {}
    for sent in sentences_list:
        for word in word_tokenize(sent.lower()):
            if word.lower() in nltk_word_frequencies.keys():
                if sent not in nltk_sentence_score.keys():
                    nltk_sentence_score[sent] = nltk_word_frequencies[word.lower()]
                else:
                    nltk_sentence_score[sent] += nltk_word_frequencies[word.lower()]

    summary = nlargest(sentences_count, nltk_sentence_score, key=nltk_sentence_score.get)

    return "\n".join(summary)


async def chat_history_summary_generate(chat_history: str,
                                        sentences_count: int = constants.DEFAULT_SUMMARY_SENTENCES_COUNT) -> str:
    result = await text_summary_generate(text=chat_history, sentences_count=sentences_count)
    return result
