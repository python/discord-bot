import unittest
from unittest import mock
from bot import app

class SmokeTest(unittest.TestCase):
	
	def smoke_test(self):
		self.assertTrue(True)


class TestCommands(unittest.TestCase):

	@mock.patch('ctx.send')
	def test_ping(self, send_mock):
		app.ping(None)
		mock.assert_called_once_with("pong")	
		
