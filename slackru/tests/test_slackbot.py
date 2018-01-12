""" Tests slackbot Package """

import time
from threading import Thread

from slackru.tests import TestBase, params


class TestSlackBot(TestBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        from slackru.bot.slackbot import SlackBot
        cls.bot = SlackBot()
        t = Thread(target=cls.bot.run)
        t.setDaemon(True)
        t.start()

        while True:
            if cls.bot.isAlive:
                break
            else:
                time.sleep(0.1)
                continue

    @params(("mentors Python Rules!", [0]), ("mentors My Java code is not working", [1]),
            ("mentors I hate C++", [0, 1]), ("mentors", []))
    def test_mentors_cmd(self, command, mentorIndexes):
        if command == 'mentors':
            self.assertTrue(self.handle_cmd(command))
        else:
            self.assertEqual(self.handle_cmd(command), [self.data['mentorid'][i] for i in mentorIndexes])

    def test_help_cmd(self):
        resp = self.handle_cmd("help")
        self.assertTrue(resp)

    def handle_cmd(self, cmd):
        return self.bot.handle_command(cmd, self.data['channel'][0], self.data['userid'], self.data['username'])
