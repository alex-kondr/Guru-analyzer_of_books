from typing import List

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException

from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User
from src.services.auth import auth_service
from src.schemas.chats import ChatHistoryResponse, ChatResponse, ChatModel
from src.repository import chats as repository_chats
from src.repository import files as repository_files

router = APIRouter(prefix="/chats", tags=["chats"])


@router.get("/", name="Return all chat history for document"
 , response_model=List[ChatHistoryResponse])
async def read_chat_by_document_id(document_id: int, db: Session = Depends(get_db),
                                   current_user: User = Depends(auth_service.get_current_user)):
    return await repository_chats.get_chat_by_document_id(document_id, current_user.id, db)


@router.post("/", name="Ask a question to file", response_model=ChatResponse)
async def ask_question(document_id: int, question: str, db: Session = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user)):
    document = await repository_files.get_document_by_id(document_id, db)
    if document is None:
        raise HTTPException(status_code=404)
    if document.user_id != current_user.id:
        raise HTTPException(status_code=403)
    return await repository_chats.ask_question(document_id, question, current_user.id, db)

