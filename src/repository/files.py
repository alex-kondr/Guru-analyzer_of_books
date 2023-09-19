import os
from typing import Type
import uuid

from sqlalchemy.orm import Session
from fastapi import UploadFile

from src.database.models import Document
from src.schemas.files import DocumentsList
from src.model.model import convert_doc_to_vector_db
from src.conf import constants
from src.conf import messages


async def get_document_by_id(document_id: int, user_id: int, db: Session) -> Type[DocumentsList] | None:
    return db.query(Document).filter(Document.id == document_id, Document.user_id == user_id).first()


async def get_document_by_name(name: str, user_id: int, db: Session) -> Type[DocumentsList] | None:
    return db.query(Document).filter(Document.name == name, Document.user_id == user_id).first()


async def create_documents(files: list[UploadFile], user_id: int, db: Session):
    user_path = constants.WORK_PATH / f"user_{user_id}"
    user_path.mkdir(exist_ok=True)

    for file in files:
        document = await get_document_by_name(file.filename, user_id, db)
        if document:
            continue

        if file.content_type not in constants.FILE_SUPPORTED_CONTENT_TYPE:
            raise ValueError(messages.UNSUPPORTED_CONTENT_TYPE.format(file.content_type))

        vector_db_name = f"{file.filename}.vector_db"

        file_path = constants.WORK_PATH / file.filename
        with open(file_path, "wb") as fh:
            fh.write(file.file.read())

        new_file = Document(user_id=user_id, name=file.filename, vector_db_name=vector_db_name)
        db.add(new_file)
        db.commit()

        await convert_doc_to_vector_db(file_path=file_path, vector_db=user_path / vector_db_name,
                                       content_type=file.content_type)
        os.remove(file_path)


async def delete_document_by_id(document_id: int, user_id: int, db: Session):
    document = await get_document_by_id(document_id, user_id, db)
    os.remove(constants.WORK_PATH / f"user_{user_id}" / document.vector_db_name)
    db.delete(document)
    db.commit()
    return "Done"


async def get_user_documents(user_id: int, db: Session) -> list[Type[DocumentsList]]:
    return db.query(Document).filter(Document.user_id == user_id).all()
