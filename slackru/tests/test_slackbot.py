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

    @params(("mentors", []), ("mentors My Java code is not working", [1]),
            ("mentors I like python.", [0]), ("mentors Anyone know java?", [1]))
    @reset_mock
    def test_mentors_cmd(self, command, mentorIndexes):
        if command == 'mentors':
            self.assertEqual(self.handle_cmd(command), 500)
        else:
            try:
                self.handle_cmd(command)
                self.assertEqual(1, post_mock.call_count)
            except requests.exceptions.ConnectionError as e:
                # This exception is expected to be thrown when 'runtests.py' is run with the
                # '--no-mock' option.
                pass

    @reset_mock
    def test_help_cmd(self):
        self.handle_cmd("help")
        self.assertEqual(slack_mock.method_calls[0][1], ('chat.postMessage',))

    def handle_cmd(self, cmd):
        return self.bot.handle_command(cmd, data['channel'][0], data['userid'][0])
