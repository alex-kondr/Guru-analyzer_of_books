from sqlalchemy import Column, Integer, String, func
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import DateTime


Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    username = Column(String(30), nullable=False, unique=True, index=True)
    email = Column(String(60), nullable=False, unique=True, index=True)
    password = Column(String(255), nullable=False)
    refresh_token = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class Document(Base):
    __tablename__ = 'documents'
    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    name = Column(String, nullable=False)
    vector_db_name = Column(String, nullable=False, unique=True, index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class ChatHistory(Base):
    __tablename__ = 'chathistory'
    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    document_id = Column(ForeignKey('documents.id', ondelete='CASCADE'), nullable=False)
    question = Column(String, nullable=False)
    answer = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
