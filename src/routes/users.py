from typing import Annotated

from fastapi import APIRouter, Depends, File

from src.database.models import User
from src.services.auth import auth_service
from src.schemas.users import UserDb
from src.model.model import save_pdf_file, load_vector_db, answer_generate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserDb)
async def read_user_by_id(user: User = Depends(auth_service.get_current_user)):
    return user


@router.post("/files/")
async def load_file(file: Annotated[bytes, File()],
                    user: User = Depends(auth_service.get_current_user)):
    await save_pdf_file(file=file, user_id=user.id)
    return {"info": "File saved in db"}


@router.post("/chat/")
async def chat(question: str,
               user: User = Depends(auth_service.get_current_user)):
    vector_db = await load_vector_db(user_id=user.id)
    result = await answer_generate(question, vector_db)
    return {"result": result}
