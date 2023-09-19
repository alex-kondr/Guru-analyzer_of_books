from pathlib import Path
from typing import Union

from langchain.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import SKLearnVectorStore
from langchain import HuggingFaceHub
from langchain.chains import RetrievalQA

from src.conf import constants

EMBEDDINGS = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")


async def convert_doc_to_vector_db(file_path: Union[str, Path], vector_db: Union[str, Path],
                                   content_type: str) -> None:

    if content_type == constants.FILE_CONTENT_TYPE_PDF:
        loader = PyPDFLoader(str(file_path))
    elif content_type == constants.FILE_CONTENT_TYPE_TEXT:
        loader = TextLoader(str(file_path))
    else:
        loader = Docx2txtLoader(str(file_path))

    pages = loader.load_and_split()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1024,
        chunk_overlap=64,
        separators=['\n\n', '\n', '(?=>\. )', ' ', '']
    )

    # Split the pages into texts as defined above
    texts = text_splitter.split_documents(pages)

    # Create/update the vector store
    vector_db = SKLearnVectorStore.from_documents(
        texts,
        embedding=EMBEDDINGS,
        persist_path=str(vector_db),
        serializer="parquet"
    )
    # persist the store
    vector_db.persist()


async def load_vector_db(vector_db_path: str):
    return SKLearnVectorStore(
        embedding=EMBEDDINGS,
        persist_path=vector_db_path,
        serializer="parquet"
    )


async def answer_generate(vector_db_path: str, question: str):
    vector_db = await load_vector_db(vector_db_path)
    llm = HuggingFaceHub(repo_id="tiiuae/falcon-7b-instruct",
                         model_kwargs={"temperature": 0.5,
                                       "max_length": 512,
                                       "max_new_tokens": 200
                                       })

    qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff",
                                     retriever=vector_db.as_retriever(search_kwargs={"k": 2}),
                                     return_source_documents=True,
                                     verbose=False,
                                     )

    results = qa({"query": question})
    return results['result']
