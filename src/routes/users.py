from datetime import datetime, date
from typing import List
from fastapi import APIRouter, Depends, status, UploadFile, File, HTTPException, Query, Path

from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.schemas.users import UserDb, UserUpdateModel
from src.conf import messages


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/{user_id}", response_model=UserDb)
async def read_user_by_id(user_id: int = Path(ge=1),
                     db: Session = Depends(get_db),
                     _: User = Depends(auth_service.get_current_user)):

    user = await repository_users.get_user_by_id(user_id, db)
    if user == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.NOT_FOUND)
    return user
