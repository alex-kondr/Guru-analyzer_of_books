import unittest
from unittest.mock import MagicMock, AsyncMock

from sqlalchemy.orm import Session

from src.database.models import User
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.schemas.users import UserModel, UserUpdateModel


class TestUser(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)

    async def test_get_user_by_id(self):
        user = User(id=1, username="test")
        self.session.query().filter().first.return_value = user
        result = await repository_users.get_user_by_id(user_id=user.id, db=self.session)
        self.assertEqual(result.id, user.id)
        self.assertEqual(result.username, user.username)

    async def test_get_user_by_email(self):
        user = User(id=1, email="test")
        self.session.query().filter().first.return_value = user
        result = await repository_users.get_user_by_email(email=user.email, db=self.session)
        self.assertEqual(result.id, user.id)
        self.assertEqual(result.email, user.email)

    async def test_create_user(self):
        body = UserModel(username="username", email="test@mail.com", password="123456")
        result = await repository_users.create_user(body, db=self.session)
        self.assertEqual(result.username, body.username)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.password, body.password)
        self.assertTrue(hasattr(result, "id"))

    async def test_update_token(self):
        user = User(id=1)
        token = "token"
        result = await repository_users.update_token(user=user, token=token, db=self.session)
        self.assertIsNone(result)

    async def test_check_unique_username_False(self):
        user_2 = User(id=5)
        self.session.query().filter().first().return_value = user_2
        result = await repository_users.check_unique_username(username='username', user_id=2, db=self.session)
        self.assertFalse(result)

    async def test_check_unique_username_True(self):
        user_2 = User(id=5)
        self.session.query().filter().first().return_value = user_2
        result = await repository_users.check_unique_username(username='username', user_id=5, db=self.session)
        self.assertTrue(result)


    async def test_update_current_user(self):
        body = UserUpdateModel(
            first_name="first_name",
            last_name="last_name",
            username="username"
        )
        user = User(id=1)
        count = 1
        self.session.query().filter().first.return_value = user
        self.session.query().filter().update.return_value = count
        result = await repository_users.update_current_user(body=body, user=user, db=self.session)
        self.assertEqual(result, user)

    async def test_delete_current_user_None(self):
        user = User(id=1)
        result = await repository_users.delete_current_user(user=user, db=self.session)
        self.assertTrue(hasattr(result, "result"))
