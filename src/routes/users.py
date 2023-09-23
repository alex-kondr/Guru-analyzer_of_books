from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User
from src.services.auth import auth_service
from src.schemas.users import UserDb, UserUpdateModel
from src.repository import users as repository_users
from src.conf import messages

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserDb)
async def read_user(user: User = Depends(auth_service.get_current_user)):
    return user


@router.put('/', name="Edit current user's info", response_model=UserDb)
async def edit_current_user(body: UserUpdateModel,
                    current_user: User = Depends(auth_service.get_current_user),
                    db: Session = Depends(get_db)):
    if await repository_users.check_unique_username(username=body.username, user_id=current_user.id, db=db):
        return await repository_users.update_current_user(body, current_user, db)
    else:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=messages.USERNAME_IS_USED.format(username=body.username))


@router.delete("/", name="Delete current user", status_code=status.HTTP_204_NO_CONTENT)
async def delete_current_user(db: Session = Depends(get_db),
                              current_user: User = Depends(auth_service.get_current_user)):
    return await repository_users.delete_current_user(user=current_user, db=db)
