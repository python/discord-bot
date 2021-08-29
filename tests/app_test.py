import sys
import os


import unittest
from unittest import mock
import app

class AsyncMock(mock.MagicMock):
    async def __call__(self, *args, **kwargs):
        return super().__call__(*args, **kwargs)

class TestSmoketest(unittest.TestCase):
    
    def test_smoke(self):
        self.assertTrue(True)

class TestApp(unittest.TestCase):

    def test_import(self):
        self.assertTrue(hasattr(app, "ping"))
