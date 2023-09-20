from datetime import datetime

from pydantic import BaseModel


class DocumentModel(BaseModel):
    id: int
    user_id: int
    name: str


class Document(BaseModel):
    id: int
    name: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
