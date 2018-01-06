import requests
from threading import Thread

from slackru.tests.test_base import TestBase


class TestSlackBot(TestBase):
    @classmethod
    def setUpClass(cls):
        TestBase.setUpClass()

        from slackru.slackbot import SlackBot
        cls.bot = SlackBot()
        Thread(target=cls.bot.start).start()

    @classmethod
    def tearDownClass(cls):
        TestBase.tearDownClass()
        cls.bot.stop()


class TestHandleCommand(TestSlackBot):
    def test_mentors_cmd(self):
        self.assertRaises(requests.exceptions.ConnectionError,
                self.bot.handle_command, "mentors Python Rules!", self.channel, self.userid, self.username)

    def test_help_cmd(self):
        resp = self.bot.handle_command("help", self.channel, self.userid, self.username)
        self.assertEqual(True, resp)
