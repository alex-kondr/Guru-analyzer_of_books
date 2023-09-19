from pathlib import Path
from typing import Union

from langchain.document_loaders import PyPDFLoader
from langchain.document_loaders import TextLoader
from langchain.document_loaders import SeleniumURLLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain import HuggingFaceHub
from langchain.chains import RetrievalQA
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from docx import Document


EMBEDDINGS = OpenAIEmbeddings(openai_api_key="")


async def convert_pdf_to_vector_db(file_path: Union[str, Path], vector_db_path: Union[str, Path]) -> None:
    if file_path.lower().endswith(".pdf"):
        loader = PyPDFLoader(str(file_path))
        pages = loader.load_and_split()

    elif file_path.lower().endswith(".docx"):
        word_doc = Document(file_path)
        passages = [p.text for p in word_doc.paragraphs]
        content = "\n".join(passages)
        file_txt_path = "./file.txt"

        with open(file_txt_path, "w") as f:
            f.write(content)

        loader = TextLoader(file_txt_path)
        pages = loader.load()

    elif file_path.lower().endswith(".txt"):
        loader = TextLoader(file_path)
        pages = loader.load()

    elif "http:" in file_path.lower() or "www." in file_path.lower():
        loader = SeleniumURLLoader([file_path])
        pages = loader.load()

    else:
        return

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1024,
        chunk_overlap=64,
        separators=['\n\n', '\n', '(?=>\. )', ' ', '']
    )

    # Split the pages into texts as defined above
    texts = text_splitter.split_documents(pages)

    # Create/update the vector store
    vector_db = FAISS.from_documents(texts, EMBEDDINGS)
    vector_db.save_local(str(vector_db_path), index_name=("wiki_rmse"))


async def load_vector_db(vector_db_path: str):
    return FAISS.load_local(folder_path=vector_db_path,
                            index_name='wiki_rmse',
                            embeddings=EMBEDDINGS
                            )


async def answer_generate(vector_db_path: str, question: str):
    vector_db = await load_vector_db(vector_db_path)

    llm = HuggingFaceHub(huggingfacehub_api_token="",
                         repo_id="tiiuae/falcon-7b-instruct",
                         model_kwargs={"temperature": 0.5,
                                       "max_length": 512,
                                       "max_new_tokens": 200
                                       })

    qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff",
                                     retriever=vector_db.as_retriever(search_kwargs={"k": 2}),
                                     return_source_documents=True,
                                     verbose=False
                                     )

    results = qa({"query": question})
    return results['result']
