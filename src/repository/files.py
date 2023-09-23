import os
import shutil
from typing import Type, List

from sqlalchemy import desc
from sqlalchemy.orm import Session
from fastapi import UploadFile

from src.database.models import Document
from src.database.models import ChatHistory
from src.model.model import convert_document_to_vector_db, delete_vector_db
from src.conf import constants


async def get_document_by_id(document_id: int, user_id: int, db: Session) -> Document | None:
    return db.query(Document).filter(Document.id == document_id, Document.user_id == user_id).first()


async def get_document_by_name(name: str, user_id: int, db: Session) -> Document | None:
    return db.query(Document).filter(Document.name == name, Document.user_id == user_id).first()


async def create_document(file: UploadFile, user_id: int, db: Session) -> Document:

    temp_path = constants.VECTOR_DB_PATH / "temp"
    temp_path.mkdir(exist_ok=True)

    document = await get_document_by_name(file.filename, user_id, db)
    if not document:

        file_path = temp_path / file.filename
        with open(file_path, "wb") as fh:
            shutil.copyfileobj(file.file, fh)

        document = Document(user_id=user_id, name=file.filename)
        db.add(document)
        db.commit()
        db.refresh(document)

        await convert_document_to_vector_db(file_path=file_path, document_id=document.id)
        os.remove(file_path)

    return document


async def create_document_by_url(url: str, user_id: int, db: Session) -> Document:
    document = await get_document_by_name(url, user_id, db)

    if not document:
        document = Document(user_id=user_id, name=url)
        db.add(document)
        db.commit()
        db.refresh(document)
        await convert_document_to_vector_db(file_path=url, document_id=document.id)

    return document


async def delete_document_by_id(document_id: int, user_id: int, db: Session):
    await delete_vector_db(document_id=document_id)
    document = await get_document_by_id(document_id, user_id, db)
    db.delete(document)
    db.commit()
    return {"result": "Done"}


async def get_user_documents(search_str: str, user_id: int, db: Session) -> List[Type[Document]]:
    query = db.query(Document).filter(Document.user_id == user_id)

    if search_str:
        search_str_fmt = "%" + search_str + "%"
        query = query.filter(Document.name.ilike(search_str_fmt))

    query = query.order_by(desc(Document.id))

    return query.all()


async def get_last_user_document_id(user_id: int, db: Session) -> int | None:

    last_chathistory = (db.query(ChatHistory)
                        .filter(ChatHistory.user_id == user_id)
                        .order_by(desc(ChatHistory.id))
                        .limit(1).first()
                        )
    return last_chathistory.document_id if last_chathistory else None


async def delete_user_documents(user_id: int, db: Session) -> None:

    query = db.query(Document).filter(Document.user_id == user_id)

    documents = query.all()

    for document in documents:
        await delete_document_by_id(document_id=document.id, user_id=user_id, db=db)

