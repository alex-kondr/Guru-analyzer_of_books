import logging
import os
from pathlib import Path
from typing import Union, Dict

from fastapi import HTTPException, status
from langchain.chains.question_answering import load_qa_chain
from langchain.document_loaders import PyPDFLoader
from langchain.document_loaders import TextLoader
from langchain.document_loaders import SeleniumURLLoader
from langchain.memory import ConversationBufferMemory
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain import HuggingFaceHub
from langchain.chains import RetrievalQA
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
import spacy
from spacy.lang.en.stop_words import STOP_WORDS as spacy_SW
from string import punctuation as punct
from heapq import nlargest
from docx import Document

from src.conf.logger import get_logger
from src.conf.config import settings
from src.conf import constants
from src.conf import messages

EMBEDDINGS = OpenAIEmbeddings(openai_api_key=settings.openai_api_key)


async def convert_document_to_vector_db(file_path: Union[str, Path], document_id: int) -> HTTPException | None:
    file_path = str(file_path)
    if file_path.lower().endswith(".pdf"):
        print("choice pdf method")
        loader = PyPDFLoader(file_path)
        pages = loader.load_and_split()

    elif file_path.lower().endswith(".docx") or file_path.lower().endswith(".doc"):
        word_doc = Document(file_path)
        passages = [p.text for p in word_doc.paragraphs]
        content = "\n".join(passages)
        file_txt_path = constants.VECTOR_DB_PATH / "temp/temp.txt"

        with open(file_txt_path, "w") as f:
            f.write(content)

        loader = TextLoader(file_txt_path)
        pages = loader.load()
        os.remove(file_txt_path)

    elif file_path.lower().endswith(".txt"):
        loader = TextLoader(file_path)
        pages = loader.load()

    elif "http:" in file_path.lower() or "https:" in file_path.lower() or "www." in file_path.lower():
        loader = SeleniumURLLoader([file_path])
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
    print("saved vector db")


async def load_vector_db(document_id: int):
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

    llm = HuggingFaceHub(repo_id="tiiuae/falcon-7b",
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


async def document_summary_generate(document_id: int, sentences_count: int = 5):
    vector_db = await load_vector_db(document_id)
    docs = vector_db.similarity_search_with_score('', k=10000)
    text_load = ''
    for i in range(len(docs) - 1):
        text_load += docs[i][0].page_content

    sp_stopwords = list(spacy_SW)
    punctuation = punct
    punctuation = punctuation + '\n'

    try:
        nlp = spacy.load("en_core_web_sm")
    except IOError:
        os.system("python3 -m spacy download en_core_web_sm")
        nlp = spacy.load("en_core_web_sm")

    doc = nlp(text_load)

    word_frequencies = {}
    for word in doc:
        if word.text.lower() not in sp_stopwords:
            if word.text.lower() not in punctuation:
                if word.text not in word_frequencies.keys():
                    word_frequencies[word.text] = 1
                else:
                    word_frequencies[word.text] += 1

    max_frequency = max(word_frequencies.values())
    for word in word_frequencies.keys():
        word_frequencies[word] = word_frequencies[word] / max_frequency

    sentence_tokens = list(doc.sents)
    sentence_score = {}
    for sent in sentence_tokens:
        for word in sent:
            if word.text.lower() in word_frequencies.keys():
                if sent not in sentence_score.keys():
                    sentence_score[sent] = word_frequencies[word.text.lower()]
                else:
                    sentence_score[sent] += word_frequencies[word.text.lower()]

    summary = nlargest(sentences_count, sentence_score, key=sentence_score.get)
    summary = [summ.text for summ in summary]
    return "\n".join(summary)


async def chathistory_summary_generate(document_id: int, chathistory: str, sentences_count: int):
    vector_db = await load_vector_db(document_id)
    # TODO реалізувати формування самарі по chathistory

    result = chathistory  # + "\n" + "--- answer will be soon --- " * sentences_count
    return result
