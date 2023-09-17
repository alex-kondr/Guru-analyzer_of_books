from typing import Type, Annotated, List
from pathlib import Path

from sqlalchemy.orm import Session
from fastapi import File, UploadFile
from PyPDF2 import PdfReader, PdfWriter

from src.database.models import User, Document
from src.schemas.users import UserModel
from src.model.model import convert_pdf_to_vector_db


WORK_PATH = Path("src/model/files")
WORK_PATH.mkdir(exist_ok=True)
# VECTOR_DB_PATH = WORK_PATH / "document_vector_db.parquet"


async def get_user_by_id(user_id: int, db: Session) -> Type[User] | None:
    return db.query(User).filter(User.id == user_id).first()


async def get_user_by_email(email: str, db: Session) -> User | None:
    return db.query(User).filter(User.email == email).first()


async def create_user(body: UserModel, db: Session) -> User:
    new_user = User(**body.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: Session) -> None:
    user.refresh_token = token
    db.commit()


async def get_document_by_id(document_id: int, user: User, db: Session) -> Type[Document]:
    return db.query(Document).filter_by(id=document_id, user_id=user.id).first()


async def list_of_documents(user: User, db: Session) -> List[Type[Document]]:
    return db.query(Document).filter_by(user_id=user.id).all()


async def upload_file(file: Annotated[UploadFile, File()], user: User, db: Session):
    user_path = WORK_PATH / f"user_{user.id}"
    user_path.mkdir(exist_ok=True)

    books = user_path / "books"
    books.mkdir(exist_ok=True)

    vector_db_path = user_path / "vector_db"
    vector_db_path.mkdir(exist_ok=True)
    vector_db = vector_db_path / f"{file.filename}.vector_db"

    pdf_doc = PdfReader(stream=file.file)
    writer = PdfWriter()
    [writer.add_page(page) for page in pdf_doc.pages]

    file_path = books / file.filename
    with open(file_path, "wb") as fh:
        writer.write(fh)

    new_file = Document(user_id=user.id, name=str(file_path), vector_db_name=str(vector_db))
    db.add(new_file)
    db.commit()
    db.refresh(new_file)

    await convert_pdf_to_vector_db(file_path=file_path, vector_db=vector_db)
