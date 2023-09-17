from sqlalchemy.orm import Session

from src.database.models import ChatHistory


async def get_chat_by_document_id(document_id: int, user_id: int, db: Session):
    chats = db.query(ChatHistory).filter(ChatHistory.document_id == document_id,
                                        ChatHistory.user_id == user_id).all()
    return chats


async def ask_question(document_id: int, question: str, user_id: int, db: Session):
    # TODO Замінити на формування відповіді у залежності від документа, до якого надійшов запит та питання
    answer = '---- will be soon -----'
    chat = ChatHistory(document_id=document_id, user_id=user_id, question=question, answer=answer)
    db.add(chat)
    db.commit()
    return {"answer": answer}
