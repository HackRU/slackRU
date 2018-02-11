""" Tests slackbot Package """

from unittest.mock import patch, MagicMock

from slackru.tests import TestBase, params, reset_mock, data
from slackru.tests import slack_mock


class MockResp:
    status_code = 200


class TestSlackBot(TestBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        from slackru.bot.slackbot import SlackBot
        cls.bot = SlackBot()

    @params(("mentors", []), ("mentors My Java code is not working", [1]),
            ("mentors I like python.", [0]), ("mentors Anyone know java?", [1]))
    def test_mentors_cmd(self, command, mentorIndexes):
        if command == 'mentors':
            self.assertEqual(self.handle_cmd(command), 500)
        else:
            with patch('slackru.bot.actions.requests.post', MagicMock(return_value=MockResp)) as post_mock:
                self.assertEqual(self.handle_cmd(command), 200)
                self.assertEqual(1, post_mock.call_count)

    @reset_mock
    def test_help_cmd(self):
        self.handle_cmd("help")
        self.assertEqual(slack_mock.method_calls[0][1], ('chat.postMessage',))

    def handle_cmd(self, cmd):
        return self.bot.handle_command(cmd, data['channel'][0], data['userid'][0])
