import unittest
from unittest.mock import MagicMock, AsyncMock, patch

from sqlalchemy.orm import Session

from src.repository import files as repository_files
from src.database.models import Document
from starlette.datastructures import UploadFile


class TestChat(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user_id = 5

    async def test_get_document_by_id(self):
        self.session.query().filter().first().return_value = 15
        result = await repository_files.get_document_by_id(15, self.user_id, db=self.session)
        self.assertTrue(hasattr(result, 'id'))

    async def test_get_document_by_name(self):
        self.session.query().filter().first().return_value = 15
        result = await repository_files.get_document_by_name('15', self.user_id, db=self.session)
        self.assertTrue(hasattr(result, 'id'))

    async def test_get_last_user_document_id(self):
        document = Document(id=5, user_id=123, name="test.txt")
        self.session.query().filter().order_by().limit().first().return_value = document
        result = await repository_files.get_last_user_document_id(self.user_id, db=self.session)
        self.assertEqual(result, 5)

    async def test_get_last_user_document_id_None(self):
        self.session.query().filter().order_by().limit().first().return_value = None
        result = await repository_files.get_last_user_document_id(10, db=self.session)
        self.assertIsNone(result)

    async def test_create_document(self):
        user_id = 123
        fake_file = UploadFile(filename="test.txt", file=None)
        document = Document(id=1, user_id=user_id, name="test.txt")
        repository_files.get_document_by_name_mock = MagicMock(return_value=None)
        result = await repository_files.create_document(fake_file, user_id, self.session)
        self.assertTrue(hasattr(result, 'id'))

    async def test_create_document_by_url(self):
        user_id = 123
        url = "htts:\\test.com8989898"
        document = Document(id=1, user_id=user_id, name=url)
        result = await repository_files.create_document_by_url(url, user_id, self.session)
        self.assertTrue(hasattr(result, 'id'))

    async def test_get_user_documents(self):
        search_str = None #"example"
        user_id = 123
        fake_documents = [
            Document(id=1, user_id=user_id, name="example_document.txt"),
            Document(id=2, user_id=user_id, name="another_example.txt"),
        ]
        self.session.query().all().return_value = fake_documents

        results = await repository_files.get_user_documents(search_str, user_id, self.session)
        self.assertEqual(len(results), len(fake_documents))

    async def test_delete_document_by_id(self):
        document_id = 10
        user_id = 123
        document = Document(id=document_id, user_id=user_id, name="test.txt")
        get_document_by_id = MagicMock(return_value=document)
        result = await repository_files.delete_document_by_id(document_id, user_id, self.session)
        self.assertEqual(result, {'result': 'Done'})

