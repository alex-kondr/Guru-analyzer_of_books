from typing import List

from fastapi import APIRouter, Depends, UploadFile, Path, HTTPException
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User
from src.services.auth import auth_service
from src.repository import files as repository_files
from src.schemas.files import Document
from src.schemas.chats import ChatResponse
from src.model.model import document_summary_generate

router = APIRouter(prefix="/files", tags=["files"])


@router.get("/", name="Return all user's files", response_model=List[Document])
async def get_files(search_str: str = None, db: Session = Depends(get_db),
                    current_user: User = Depends(auth_service.get_current_user)):
    return await repository_files.get_user_documents(search_str=search_str,
                                                     user_id=current_user.id,
                                                     db=db)


@router.post("/doc",
             name="Upload file. The following file types are supported: pdf, docx, doc, txt ",
             response_model=Document)
async def add_file(file: UploadFile,
                   db: Session = Depends(get_db),
                   current_user: User = Depends(auth_service.get_current_user)):
    return await repository_files.create_document(file, current_user.id, db)


@router.post("/url", name="Upload text by url", response_model=Document)
async def add_text_by_url(url: str,
                          db: Session = Depends(get_db),
                          current_user: User = Depends(auth_service.get_current_user)):
    return await repository_files.create_document_by_url(url, current_user.id, db)


@router.delete("/{document_id}", name="Delete document")
async def delete_file(document_id: int = Path(ge=1),
                      db: Session = Depends(get_db),
                      current_user: User = Depends(auth_service.get_current_user)):

    document = await repository_files.get_document_by_id(document_id=document_id,
                                                         user_id=current_user.id,
                                                         db=db)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    return await repository_files.delete_document_by_id(document_id, current_user.id, db)


@router.post("/summary/{document_id}", name="Make document summary", response_model=ChatResponse)
async def make_summary_by_document_id(document_id: int = Path(ge=1),
                                      sentences_count: int = 5,
                                      db: Session = Depends(get_db),
                                      current_user: User = Depends(auth_service.get_current_user)):

    document = await repository_files.get_document_by_id(document_id=document_id,
                                                         user_id=current_user.id,
                                                         db=db)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    answer = await document_summary_generate(document_id, sentences_count)

    return {"answer": answer}
