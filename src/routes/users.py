from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from src.database.models import User
from src.database.db import get_db
from src.services.auth import auth_service
from src.schemas.users import UserDb
from src.repository import users as repository_users
from src.model.model import answer_generate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserDb)
async def read_user(user: User = Depends(auth_service.get_current_user)):
    return user


@router.post("/files/")
async def upload_file(file: Annotated[UploadFile, File()],
                      db: Session = Depends(get_db),
                      user: User = Depends(auth_service.get_current_user)):
    await repository_users.upload_file(file=file, user=user, db=db)
    return {"info": "File saved in db"}


@router.post("/chat/")
async def chat(document_id: int,
               question: str,
               db: Session = Depends(get_db),
               user: User = Depends(auth_service.get_current_user)):

    document = await repository_users.get_document_by_id(document_id=document_id, user=user, db=db)
    result = await answer_generate(document.vector_db_name, question)

    return {"result": result}
