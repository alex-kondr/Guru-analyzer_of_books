import logging
import os
import shutil
from datetime import datetime
from typing import Type, List

from sqlalchemy import desc, func
from sqlalchemy.orm import Session
from fastapi import UploadFile

from src.conf.logger import get_logger
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

        tokens = await convert_document_to_vector_db(file_path=file_path, document_id=document.id)
        document.tokens_count = tokens['1K/tokens']
        db.commit()
        db.refresh(document)

        os.remove(file_path)

    return document


async def create_document_by_url(url: str, user_id: int, db: Session) -> Document:
    document = Document(user_id=user_id, name=url)
    db.add(document)
    db.commit()
    db.refresh(document)

    logger = get_logger("test")
    logger.log(level=logging.DEBUG, msg="end save db")

    tokens = await convert_document_to_vector_db(file_path=url, document_id=document.id)
    document.tokens_count = tokens['1K/tokens']
    db.commit()
    db.refresh(document)

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


async def get_remaining_user_token_limit(user_id: int, db: Session) -> int:
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    used_tokens = db.query(func.sum(Document.tokens_count)).filter(Document.created_at >= today_start,
                                                                   Document.user_id == user_id).scalar()
    if used_tokens:
        return constants.USER_TOKENS_COUNT_LIMIT - used_tokens
    return constants.USER_TOKENS_COUNT_LIMIT


async def get_last_user_document_id(user_id: int, db: Session) -> int | None:
    last_chat_history = (db.query(ChatHistory)
                         .filter(ChatHistory.user_id == user_id)
                         .order_by(desc(ChatHistory.id))
                         .limit(1).first()
                         )
    return last_chat_history.document_id if last_chat_history else None


async def delete_user_documents(user_id: int, db: Session) -> None:
    query = db.query(Document).filter(Document.user_id == user_id)

    documents = query.all()

    for document in documents:
        await delete_document_by_id(document_id=document.id, user_id=user_id, db=db)
