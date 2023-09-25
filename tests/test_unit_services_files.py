import unittest
import requests
from unittest.mock import MagicMock
from src.services.files import check_url_exists


class TestCheckServicesFiles(unittest.TestCase):

    def test_url_exists(self):
        mock_get = MagicMock()
        mock_get.return_value.status_code = 200
        with unittest.mock.patch('requests.get', mock_get):
            url = 'https://www.example.com'
            result = check_url_exists(url)
            self.assertTrue(result)

    def test_url_does_not_exist(self):
        mock_get = MagicMock()
        mock_get.side_effect = requests.exceptions.RequestException('Connection Error')
        with unittest.mock.patch('requests.get', mock_get):
            url = 'https://www.nonexistenturl.com'
            result = check_url_exists(url)
            self.assertFalse(result)

    def test_invalid_url_format(self):
        url = 'invalid_url'
        result = check_url_exists(url)
        self.assertFalse(result)

    def test_url_return404(self):
        mock_get = MagicMock()
        mock_get.return_value.status_code = 404
        with unittest.mock.patch('requests.get', mock_get):
            url = 'https://www.nonexistenturl.com'
            result = check_url_exists(url)
            self.assertFalse(result)
