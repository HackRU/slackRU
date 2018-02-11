""" SlackBot Actions

Utility Functions and Classes used by the SlackBot
"""

import requests

import slackru.util as util
import slackru.messages as M
from slackru import get_db
from slackru.config import config


class Scanner:
    def scheduleScans(self):
        pass


class Commands:
    """ SlackBot Commands """
    db = get_db()

    @classmethod
    def mentors(cls, question: str, userid: str) -> int:
        """ 'mentors' command: Matches mentor with hacker.

        @question: hacker's question
        @userid: hacker's userid
        """
        util.slack.sendMessage(userid, "Trying to find a mentor")

        if not question:
            return 500

        postData = {'question': question,
                    'userid': userid}

        resp = requests.post(config.serverurl + 'pair_mentor', data=postData)

        return resp.status_code

    @classmethod
    def help(cls, userid):
        util.slack.sendMessage(userid, M.HELP)
