""" SlackBot Actions

Utility Functions and Classes used by the SlackBot
"""

import json

import slackru.util as util

from slackru import get_db


class Scanner:
    def scheduleScans(self):
        pass


class Commands:
    """ SlackBot Commands """
    db = get_db()

    @classmethod
    def mentors(cls, question: 'str', userid: 'str') -> '[str]':
        """ 'mentors' command: Matches mentor with hacker.

        @question: hacker's question
        @userid: hacker's userid
        """
        util.slack.sendMessage(userid, "Trying to find a mentor")

        mentorsQuery = ("SELECT mentors.* FROM shifts "
                        "JOIN mentors ON mentors.userid = shifts.userid "
                        "WHERE datetime('now', 'localtime') >= datetime(shifts.start) "
                        "AND datetime('now', 'localtime') < datetime(shifts.end)")

        mentorsOnDuty = cls.db.runQuery(mentorsQuery)
        selectedMentorIDs = list(cls._getMatchedMentorIDs(question, mentorsOnDuty)) \
                             or [mentor['userid'] for mentor in mentorsOnDuty]

        questionId = cls.db.insertQuestion(question,
                                           userid,
                                           json.dumps(selectedMentorIDs))

        attachments = [{'text': '',
                        'attachment_type': 'default',
                        'callback_id': 'mentorResponse_{0:d}'.format(questionId),
                        'actions': [{'name': 'answer',
                                     'text': 'Yes',
                                     'type': 'button',
                                     'value': 'yes'},
                                    {'name': 'answer',
                                     'text': 'No',
                                     'type': 'button',
                                     'value': 'no'}]}]

        textFmt = ("*A HACKER NEEDS YOUR HELP!!!*\n"
                "<@{0}> has requested to be assisted by a mentor.\n"
                "They provided the following statement:\n"
                ">_\"{1}\"_\nCan you help this hacker?\n")

        text = textFmt.format(userid, question)
        for mentorid in selectedMentorIDs:
            channel = util.slack.getDirectMessageChannel(mentorid)
            timestamp = util.slack.sendMessage(channel, text, attachments)['ts']
            cls.db.insertPost(questionId, mentorid, channel, timestamp)

        return selectedMentorIDs

    @classmethod
    def help(cls, userid: 'str'):
        """ 'help' command: Provides list of SlackBot commands

        @userid: hacker's userid
        """
        resps = [None, None, None]
        resps[0] = util.slack.sendMessage(userid, "Hello! You requested the help command, here are a list of commands you can use delimeted by |'s:")
        resps[1] = util.slack.sendMessage(userid, "All commands will begin with <AT character>slackru")
        resps[2] = util.slack.sendMessage(userid, """Hacker:\n| mentors <keywords> | -> This command takes keywords and attempts to set you up with a mentor
                        \n| help  | -> Wait what?
                        \n | announcements | -> returns next 5 events \n  | hours | -> returns hours left in the hackathon
                        \nMentor:\n| shortenList <password> <hacker id> | -> Used to help a hackers whose keywords could not be found.
                       \n | unbusy | makes your busy status 0, so you can help more people!
                       \n | busy | -> opposite of the guy above, used when you want to afk I guess""")
        return all([resp['ok'] for resp in resps])

    @classmethod
    def _getMatchedMentorIDs(cls, question: 'str', mentorsOnDuty: '[{str: ??}]'):
        """ Matches Mentors based on 'question' and what mentors currently have shifts scheduled """
        import string

        translator = question.maketrans(dict.fromkeys(string.punctuation))

        temp = question.translate(translator)
        temp = list(filter(lambda x: x not in string.punctuation, temp.split()))
        temp = [word.lower() for word in temp]

        question_keywords = temp

        for mentor in mentorsOnDuty:
            keywords = [word.lower() for word in mentor['keywords'].split(',')]
            for word in question_keywords:
                if word in keywords:
                    yield mentor['userid']
                    break
