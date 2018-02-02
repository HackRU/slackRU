""" Tests slackbot Package """

from slackru.tests import TestBase, params, slack_client, data


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
            self.assertIsNotNone(self.handle_cmd(command))
        else:
            self.assertEqual(self.handle_cmd(command), [data['mentorid'][i] for i in mentorIndexes])

    def test_help_cmd(self):
        self.handle_cmd("help")
        slack_client.api_call.assert_called_once()

    def handle_cmd(self, cmd):
        return self.bot.handle_command(cmd, data['channel'][0], data['userid'][0])
