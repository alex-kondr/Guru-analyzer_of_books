from typing import Type

from sqlalchemy.orm import Session

from src.database.models import ChatHistory


async def get_chat_by_document_id(document_id: int, user_id: int, db: Session) -> list[Type[ChatHistory]]:
    return db.query(ChatHistory).filter(ChatHistory.document_id == document_id,
                                        ChatHistory.user_id == user_id).all()


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
