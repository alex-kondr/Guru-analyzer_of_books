from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query

from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User
from src.services.auth import auth_service
from src.schemas.chats import ChatHistoryResponse, ChatResponse, ChatQuestion
from src.repository import chats as repository_chats
from src.repository import files as repository_files
from src.model.model import answer_generate, chat_history_summary_generate
from src.conf import messages
from src.conf import constants

router = APIRouter(prefix="/chats", tags=["chats"])


@router.get("/", name="Return all chat history for document", response_model=List[ChatHistoryResponse])
async def read_chat_by_document_id(document_id: int,
                                   last_question_count: int = constants.DEFAULT_LAST_ANSWERS_COUNT,
                                   db: Session = Depends(get_db),
                                   current_user: User = Depends(auth_service.get_current_user)):
    document = await repository_files.get_document_by_id(document_id=document_id,
                                                         user_id=current_user.id,
                                                         db=db)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.DOCUMENT_NOT_FOUND)

    chat_history = await repository_chats.get_chat_by_document_id(document_id=document_id,
                                                                  user_id=current_user.id,
                                                                  db=db,
                                                                  last_question_count=last_question_count)

    if not chat_history:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.DOCUMENT_CHATHISTORY_NOT_FOUND)

    return chat_history


@router.post("/", name="Ask a question to file", response_model=ChatResponse)
async def ask_question(body: ChatQuestion,
                       db: Session = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user)):
    document = await repository_files.get_document_by_id(document_id=body.document_id,
                                                         user_id=current_user.id,
                                                         db=db)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.DOCUMENT_NOT_FOUND)

    result = await answer_generate(body.document_id, body.question)

    await repository_chats.save_chat(
        document_id=body.document_id,
        question=body.question,
        answer=result["answer"],
        user_id=current_user.id,
        db=db
    )

    return {"answer": result["answer"]}


@router.get("/summary", name="Get last answers summary by doc id", response_model=ChatResponse)
async def make_chat_history_summary_by_document_id(document_id: int = Query(ge=1),
                                                   last_answers_count: Optional[int] =
                                                   Query(default=constants.DEFAULT_LAST_ANSWERS_COUNT, ge=1),
                                                   sentences_count: int =
                                                   Query(default=constants.DEFAULT_SUMMARY_SENTENCES_COUNT, ge=1),
                                                   db: Session = Depends(get_db),
                                                   current_user: User = Depends(auth_service.get_current_user)):
    chat_history = await repository_chats.get_chat_by_document_id(document_id=document_id,
                                                                  user_id=current_user.id,
                                                                  db=db,
                                                                  last_question_count=last_answers_count)
    if not chat_history:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.DOCUMENT_NOT_FOUND)

    history_answers = " ".join([chat.answer for chat in chat_history])
    answer = await chat_history_summary_generate(chat_history=history_answers,
                                                 sentences_count=sentences_count)
    return {"answer": answer}