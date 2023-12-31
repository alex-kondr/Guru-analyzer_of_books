from datetime import datetime
import re

from pydantic import BaseModel, Field, EmailStr, EmailError, validator

from src.conf.constants import EMAIL_MAX__LEN, EMAIL_MIN_LEN, USERNAME_MIN_LEN, USERNAME_MAX_LEN, PASSWORD_MIN_LEN, PASSWORD_MAX_LEN


class UserModel(BaseModel):
    first_name: str = None
    last_name: str = None
    username: str = Field(..., min_length=USERNAME_MIN_LEN, max_length=USERNAME_MAX_LEN-1) #'@jay_b'
    email: str = Field(..., min_length=EMAIL_MIN_LEN, max_length=EMAIL_MAX__LEN) #'jay_b@example.com'
    password: str = Field(min_length=PASSWORD_MIN_LEN, max_length=PASSWORD_MAX_LEN)

    @validator("username")
    def validate_username(cls, username: str):
        try:
            if re.search(r"^[a-zA-Z0-9 _]+$", username):
                return '@' + username.strip().lower().replace(' ', '_')
            else:
                raise ValueError()
        except ValueError:
            raise ValueError(f"\"{username}\" - is not a valid username")

    @validator("email")
    def check_email_value(cls, email_str):
        try:
            return EmailStr().validate(email_str)
        except EmailError:
            raise ValueError(f"\"{email_str}\" - is not a valid email address")


class UserDb(BaseModel):
    id: int
    first_name: str = None
    last_name: str = None
    username: str
    email: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class UserResponse(BaseModel):
    user: UserDb
    detail: str = "User successfully created"


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserUpdateModel(BaseModel):
    first_name: str = None
    last_name: str = None
    username: str

    @validator("username")
    def validate_username(cls, username: str):
        try:
            if re.search(r"^[a-zA-Z0-9 _]+$", username):
                return '@' + username.strip().lower().replace(' ', '_')
            else:
                raise ValueError()
        except ValueError:
            raise ValueError(f"\"{username}\" - is not a valid username")