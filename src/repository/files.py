import uuid

from sqlalchemy.orm import Session

from src.database.models import Document
from src.schemas.files import DocumentModel, DocumentsList


async def get_document_by_id(document_id: int, db: Session) -> DocumentModel:
    document = db.query(Document).filter(Document.id == document_id).first()
    return document


async def create_documents(files: list, user_id: int, db: Session):
    for file in files:
        file_name = file.filename
        content_type = file.content_type
        file_content = await file.read()
        #TODO віришити шо робити з файлом
        vector = str(uuid.uuid4())
        document = Document(name=file_name,
                            vector_db_name=vector,
                            user_id=user_id)
        db.add(document)
        db.commit()
    return None


async def delete_document_by_id(document_id: int, user_id: int, db: Session):
    count = db.query(Document).filter(Document.id == document_id, Document.user_id == user_id).delete()
    db.commit()
    return count


async def get_user_documents(user_id: int, db: Session) -> DocumentsList:
    documents = db.query(Document).filter(Document.user_id == user_id).all()
    return documents
