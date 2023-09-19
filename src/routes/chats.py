from typing import List

from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User
from src.conf import constants
from src.services.auth import auth_service
from src.schemas.chats import ChatHistoryResponse, ChatResponse, ChatQuestion
from src.repository import chats as repository_chats
from src.repository import files as repository_files
from src.model.model import answer_generate

router = APIRouter(prefix="/chats", tags=["chats"])


@router.get("/", name="Return all chat history for document", response_model=List[ChatHistoryResponse])
async def read_chat_by_document_id(document_id: int,
                                   db: Session = Depends(get_db),
                                   current_user: User = Depends(auth_service.get_current_user)):
    return await repository_chats.get_chat_by_document_id(document_id, current_user.id, db)


@router.post("/", name="Ask a question to file", response_model=ChatResponse)
async def ask_question(body: ChatQuestion,
                       db: Session = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user)):
    document_id = body.document_id
    question = body.question
    document = await repository_files.get_document_by_id(document_id=document_id,
                                                         user_id=current_user.id,
                                                         db=db)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    vector_db_path = constants.WORK_PATH / f"user_{current_user.id}" / document.vector_db_name
    answer = await answer_generate(str(vector_db_path), question)

    await repository_chats.save_chat(
        document_id=document_id,
        question=question,
        answer=answer,
        user_id=current_user.id,
        db=db
    )

    return {"answer": answer}
