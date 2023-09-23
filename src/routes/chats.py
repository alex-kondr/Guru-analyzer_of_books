from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User
from src.services.auth import auth_service
from src.schemas.chats import ChatHistoryResponse, ChatResponse, ChatQuestion
from src.repository import chats as repository_chats
from src.repository import files as repository_files
from src.model.model import answer_generate, chathistory_summary_generate
from src.conf import messages


router = APIRouter(prefix="/chats", tags=["chats"])


@router.get("/", name="Return all chat history for document", response_model=List[ChatHistoryResponse])
async def read_chat_by_document_id(document_id: int,
                                   last_question_count: int = 20,
                                   db: Session = Depends(get_db),
                                   current_user: User = Depends(auth_service.get_current_user)):

    document = await repository_files.get_document_by_id(document_id=document_id,
                                                         user_id=current_user.id,
                                                         db=db)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.DOCUMENT_NOT_FOUND)

    return await repository_chats.get_chat_by_document_id(document_id=document_id,
                                                          user_id=current_user.id,
                                                          last_question_count=last_question_count,
                                                          db=db)


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


@router.post("/summary", name="Make last answers summary", response_model=ChatResponse)
async def make_chathistory_summary_by_document_id(last_question_count: int = None,
                                                  sentences_count: int = 5,
                                                  db: Session = Depends(get_db),
                                                  current_user: User = Depends(auth_service.get_current_user)):

    last_document_id = await repository_files.get_last_user_document_id(user_id=current_user.id,
                                                                        db=db)
    if last_document_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.DOCUMENT_NOT_FOUND)

    document = await repository_files.get_document_by_id(document_id=last_document_id,
                                                         user_id=current_user.id,
                                                         db=db)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.DOCUMENT_NOT_FOUND)

    chat_history = await repository_chats.get_chat_by_document_id(document_id=last_document_id,
                                                                  user_id=current_user.id,
                                                                  last_question_count=last_question_count,
                                                                  db=db)

    history_answers = [chat.answer for chat in chat_history]

    answers_for_make_summary = ' '.join(history_answers)

    answer = await chathistory_summary_generate(document_id=last_document_id,
                                                chathistory=answers_for_make_summary,
                                                sentences_count=sentences_count)

    return {"answer": answer}
