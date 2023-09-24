from typing import Type

from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas.users import UserModel
from src.repository.files import delete_user_documents


async def get_user_by_id(user_id: int, db: Session) -> Type[User] | None:
    return db.query(User).filter(User.id == user_id).first()


async def get_user_by_email(email: str, db: Session) -> User | None:
    return db.query(User).filter(User.email == email).first()


async def check_unique_username(username: str, user_id: int, db: Session) -> True | False:
    other_user = db.query(User).filter(User.username == username, User.id != user_id).first()
    return False if other_user else True


async def create_user(body: UserModel, db: Session) -> User:
    new_user = User(**body.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def delete_current_user(user: User, db: Session) -> None:
    await delete_user_documents(user_id=user.id, db=db)
    delete_user = await get_user_by_id(user_id=user.id, db=db)
    db.delete(delete_user)
    db.commit()
    return {"result": "Done"}


async def update_token(user: User, token: str | None, db: Session) -> None:
    user.refresh_token = token
    db.commit()


async def update_current_user(body: UserModel, user: User, db: Session) -> User:
    user = db.query(User).filter(User.id == user.id).first()
    db.query(User).filter(User.id == user.id).update({
            'first_name': body.first_name,
            'last_name': body.last_name,
            'username': body.username,
        })
    db.commit()
    db.refresh(user)
    return user
