import io
import os
from pathlib import Path

from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import SKLearnVectorStore
from langchain import HuggingFaceHub
from langchain.chains import RetrievalQA
from PyPDF2 import PdfReader, PdfWriter


EMBEDDINGS = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
WORK_PATH = Path(__file__).parent / "vector_db"
WORK_PATH.mkdir(exist_ok=True)
VECTOR_DB_PATH = WORK_PATH / "document_vector_db.parquet"


async def save_pdf_file(file:  bytes, user_id: int) -> None:
    temp_file = WORK_PATH / f"{user_id}_temp.pdf"
    pdf_doc = PdfReader(stream=io.BytesIO(initial_bytes=file))
    writer = PdfWriter()
    [writer.add_page(page) for page in pdf_doc.pages]
    with open(temp_file, "wb") as fh:
        writer.write(fh)
    loader = PyPDFLoader(str(temp_file))
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
        persist_path=f"{VECTOR_DB_PATH}_{user_id}",
        serializer="parquet"
    )
    # persist the store
    vector_db.persist()
    os.remove(temp_file)


async def load_vector_db(user_id: int):
    return SKLearnVectorStore(
        embedding=EMBEDDINGS,
        persist_path=f"{VECTOR_DB_PATH}_{user_id}",
        serializer="parquet"
    )


async def answer_generate(question: str, vector_db):
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
