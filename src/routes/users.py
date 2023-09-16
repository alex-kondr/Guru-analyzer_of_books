from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile, File

from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User
from src.services.auth import auth_service
from src.schemas.users import UserDb
from src.model.model import load_pdf_file, load_vector_db, qa_generate


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserDb)
async def read_user_by_id(user: User = Depends(auth_service.get_current_user)):
    return user


@router.post("/files/")
async def create_file(file: Annotated[bytes, File()]):
                      # _: User = Depends(auth_service.get_current_user)):
    # await load_pdf_file(file)
    with open(file, "rb") as fh:
        fh.sa
    # return {"file_name": len(file.filename)}


@router.post("/qa/")
async def create_file(question: str,):
                      # _: User = Depends(auth_service.get_current_user)):
    vector_db = await load_vector_db()
    result = await qa_generate(question, vector_db)
    return {"result": result}
