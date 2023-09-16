from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings, HuggingFaceInferenceAPIEmbeddings
from langchain.vectorstores import SKLearnVectorStore
from langchain.chains.question_answering import load_qa_chain
from langchain import HuggingFaceHub
from langchain.chains import RetrievalQA

import pandas as pd
from PyPDF2 import PdfReader
import io


# Load the PDF file. English or French only
# pdf_doc_path = ''
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
vector_db_path = "document_vector_db.parquet"


async def load_pdf_file(pdf_file):
    # loader = PyPDFLoader(io.BytesIO(initial_bytes=pdf_file))
    # pages = loader.load_and_split()
    pdf_doc = PdfReader(stream=io.BytesIO(initial_bytes=pdf_file))
    pages = [page.extract_text() for page in pdf_doc.pages]
    # pages = pdf_doc.pages

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1024,
        chunk_overlap=64,
        separators=['\n\n', '\n', '(?=>\. )', ' ', ''])

    # Split the pages into texts as defined above
    texts = text_splitter.split_documents(pages)


    # Set the persisted vector store
    # vector_db_path = "document_vector_db.parquet"
    # Create/update the vector store
    vector_db = SKLearnVectorStore.from_documents(
        texts,
        embedding=embeddings,
        persist_path=vector_db_path,
        serializer="parquet"
    )
    # persist the store
    vector_db.persist()
    # df = pd.read_parquet(vector_db_path)
    # df = df.drop_duplicates(subset="texts")
    # vector_db = df.to_parquet(vector_db_path)
    # return vector_db


async def load_vector_db():
    return SKLearnVectorStore(
        embedding=embeddings,
        persist_path=vector_db_path,
        serializer="parquet"
    )


def qa_generate(question: str, vector_db):
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
