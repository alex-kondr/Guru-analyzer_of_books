from fastapi import APIRouter, Depends, UploadFile, File

from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User
from src.services.auth import auth_service
from src.schemas.users import UserDb


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserDb)
async def read_user_by_id(user: User = Depends(auth_service.get_current_user)):
    return user


@router.post("/files/")
async def create_file(file: UploadFile = File(),
                      _: User = Depends(auth_service.get_current_user)):
    return {"file_size": file.size,
            "file_name": file.filename,
            "file": file.file}
