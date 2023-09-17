from datetime import datetime

from pydantic import BaseModel


class DocumentModel(BaseModel):
    id: int
    user_id: int
    name: str
    vector_db_name: str


class DocumentsList(BaseModel):
    id: int
    name: str
    vector_db_name: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
