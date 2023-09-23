from datetime import datetime

from pydantic import BaseModel


class ChatModel(BaseModel):
    document_id: int
    user_id: int
    question: str
    answer: str


class ChatHistoryResponse(BaseModel):
    id: int
    user_id: int
    document_id: int
    question: str
    answer: str
    created_at: datetime

    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda dt: dt.strftime('%d-%m-%Y %H:%M')
        }


class ChatResponse(BaseModel):
    answer: str


class SummaryResponse(BaseModel):
    summary: str


class ChatQuestion(BaseModel):
    document_id: int
    question: str
