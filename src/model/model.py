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
from docx import Document

from src.conf.logger import get_logger
from src.conf.config import settings
from src.conf import constants
from src.conf import messages


EMBEDDINGS = OpenAIEmbeddings(openai_api_key=settings.openai_api_key)


async def convert_document_to_vector_db(file_path: Union[str, Path], document_id: int) -> HTTPException | None:
    file_path = str(file_path)
    if file_path.lower().endswith(".pdf"):
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


async def document_summary_generate(document_id: int, sentences_count: int):

    vector_db = await load_vector_db(document_id)
    # TODO реалізувати формування самарі по документу

    result = "--- answer will be soon --- \n" * sentences_count
    return result


async def chathistory_summary_generate(document_id: int, chathistory: str, sentences_count: int):

    vector_db = await load_vector_db(document_id)
    # TODO реалізувати формування самарі по chathistory

    result = chathistory # + "\n" + "--- answer will be soon --- " * sentences_count
    return result
