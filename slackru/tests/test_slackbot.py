""" Tests slackbot Package """

import requests

from slackru.tests import TestBase, params, reset_mock, data
from slackru.tests import slack_mock, post_mock


class TestSlackBot(TestBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        from slackru.bot.slackbot import SlackBot
        cls.bot = SlackBot()

    @params("mentors", "mentors My Java code is not working", "mentors I like python.", "mentors Anyone know java?")
    def test_mentors_cmd(self, command):
        if command == 'mentors':
            self.assertEqual(self.handle_cmd(command), 500)
        else:
            self.handle_post_cmd(command)

    @reset_mock
    def test_help_cmd(self):
        self.handle_cmd("help")
        self.assertEqual(slack_mock.method_calls[0][1], ('chat.postMessage',))

    @params("register", "register Bryan Bugyi | 6095007081 | Python, Haskell")
    def test_register_cmd(self, command):
        if command == 'register':
            self.assertEqual(self.handle_cmd(command), 500)
        elif "register ;" in command:
            self.assertEqual(self.handle_cmd(command), 501)
        else:
            self.handle_post_cmd(command)

    @reset_mock
    def handle_post_cmd(self, command):
        try:
            self.handle_cmd(command)
            self.assertEqual(1, post_mock.call_count)
        except requests.exceptions.ConnectionError as e:
            # This exception is expected to be thrown when 'runtests.py' is run with the
            # '--no-mock' option.
            pass

    def handle_cmd(self, cmd):
        return self.bot.handle_command(cmd, data['channel'][0], data['userid'][0], data['username'][0])
