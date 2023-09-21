from typing import Type

from sqlalchemy import desc
from sqlalchemy.orm import Session

from src.database.models import ChatHistory


async def get_chat_by_document_id(document_id: int, user_id: int, last_question_count: int,
                                  db: Session) -> list[Type[ChatHistory]]:

    query = db.query(ChatHistory).filter(ChatHistory.document_id == document_id,
                                         ChatHistory.user_id == user_id).order_by(desc(ChatHistory.id))

    if last_question_count is None:
        chat_results = query.all()
    else:
        chat_results = query.limit(last_question_count).all()

    results = sorted(chat_results, key=lambda x: x.id)
    return results


async def save_chat(document_id: int,
                    question: str,
                    answer: str,
                    user_id: int,
                    db: Session) -> None:

    chat = ChatHistory(
        document_id=document_id,
        user_id=user_id,
        question=question, answer=answer
    )

    db.add(chat)
    db.commit()
