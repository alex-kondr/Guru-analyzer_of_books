import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.repository.chats import get_chat_by_document_id, save_chat
from src.database.models import ChatHistory, User, Document


class TestChat(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.document_id = 1
        self.user_id = 5

    async def test_save_chat(self):
        question = "What is your name?"
        answer = "My name is Group 4 project"
        result = await save_chat(self.document_id, question, answer, self.user_id, db=self.session)
        self.assertIsNone(result)

    async def test_get_chat_by_document_id(self):
        chat_1 = ChatHistory(id=1, user_id=self.user_id, document_id=self.document_id)
        chat_2 = ChatHistory(id=2, user_id=self.user_id, document_id=self.document_id)
        chat_3 = ChatHistory(id=3, user_id=self.user_id, document_id=self.document_id)
        chat_4 = ChatHistory(id=4, user_id=self.user_id, document_id=self.document_id)
        chat_5 = ChatHistory(id=5, user_id=self.user_id, document_id=self.document_id)
        chat_6 = ChatHistory(id=6, user_id=self.user_id, document_id=self.document_id)
        history = [chat_1, chat_2, chat_3, chat_4, chat_5, chat_6]
        query_mock = MagicMock()
        query_mock.all.return_value = history
        self.session.query.return_value = query_mock
        result = await get_chat_by_document_id(self.document_id, self.user_id, None, db=self.session)
        self.assertTrue(isinstance(result, list))
        self.assertTrue(all(hasattr(chat, 'id') for chat in result))

    async def test_get_chat_by_document_id_limit(self):
        chat_1 = ChatHistory(id=1, user_id=self.user_id, document_id=self.document_id)
        chat_2 = ChatHistory(id=2, user_id=self.user_id, document_id=self.document_id)
        chat_3 = ChatHistory(id=3, user_id=self.user_id, document_id=self.document_id)
        chat_4 = ChatHistory(id=4, user_id=self.user_id, document_id=self.document_id)
        chat_5 = ChatHistory(id=5, user_id=self.user_id, document_id=self.document_id)
        chat_6 = ChatHistory(id=6, user_id=self.user_id, document_id=self.document_id)
        history = [chat_1, chat_2, chat_3, chat_4, chat_5, chat_6]
        query_mock = MagicMock()
        query_mock.limit.all.return_value = history
        self.session.query.return_value = query_mock
        result = await get_chat_by_document_id(self.document_id, self.user_id, 3, db=self.session)
        self.assertTrue(isinstance(result, list))
        self.assertTrue(all(hasattr(chat, 'id') for chat in result))
