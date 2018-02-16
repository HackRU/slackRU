""" SlackBot Actions

Utility Functions and Classes used by the SlackBot
"""

import requests

import slackru.util as util
import slackru.messages as M
from slackru.config import config


class Scanner:
    def scheduleScans(self):
        pass


class Commands:
    """ SlackBot Commands """
    @classmethod
    def mentors(cls, question: str, userid: str) -> int:
        """ mentors: Matches mentor with hacker.

        usage:
            {bot} mentors <question>

        <question>: hacker's question
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

    @classmethod
    def register(cls, mentor_data: 'fullname | phone_number | keywords', userid: str, username: str):
        """ *register: Adds mentor to database

        usage:
            {bot} register <fullname> | <phone_number> | <keywords>

        <fullname>: The hacker's first and last name, seperated by a space.
        <phone_number>: The hacker's phone number. No spaces, dashes, or parentheses (e.g. 5555555555).
        <keywords>: These represent skills (programming languages, framewords, etc.) that you feel
                    you are particularly well suited to mentor others in. This should be a comma
                    seperated list (e.g. Python,Java,Haskell)

        NOTE: Regardless of the keywords that you choose, you will potentially be notified of any
              inquiry (question, request for help, etc.) that a hacker makes. You will, however,
              be prioritized when a hacker inquiry matches one of your listed keywords (i.e. the
              SlackBot will attempt to reach out to you before other mentors if the hacker has a
              question that contains one of your keywords).

        WARNING: You must use '|' to seperate each option! Keywords should be seperated using commas!
        """
        try:
            fullname, phone_number, keywords = [field.strip() for field in mentor_data.split('|')]
            keywords = keywords.replace(' ', '')
        except ValueError as e:
            return 500

        if not fullname:
            return 501

        postData = {'fullname': fullname,
                    'phone_number': phone_number,
                    'keywords': keywords,
                    'userid': userid,
                    'username': username}

        resp = requests.post(config.serverurl + 'register_mentor', data=postData)
        return resp.status_code
