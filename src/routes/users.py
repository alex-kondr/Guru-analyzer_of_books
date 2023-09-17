from fastapi import APIRouter, Depends

from src.database.models import User
from src.services.auth import auth_service
from src.schemas.users import UserDb


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserDb)
async def read_user(user: User = Depends(auth_service.get_current_user)):
    return user
