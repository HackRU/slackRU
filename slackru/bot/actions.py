""" SlackBot Actions

Utility Functions and Classes used by the SlackBot
"""

import json

import slackru.util as util
import slackru.bot.messages as M

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

        attachments = M.mentors_attachments(questionId)
        text = M.mentors_text(userid, question)
        for mentorid in selectedMentorIDs:
            channel = util.slack.getDirectMessageChannel(mentorid)
            timestamp = util.slack.sendMessage(channel, text, attachments)
            cls.db.insertPost(questionId, mentorid, channel, timestamp)

        return selectedMentorIDs

    @classmethod
    def help(cls, userid):
        util.slack.sendMessage(userid, M.HELP)

    @classmethod
    def _getMatchedMentorIDs(cls, question: 'str', mentorsOnDuty: '[{str: ??}]'):
        """ Matches Mentors based on 'question' and what mentors currently have shifts scheduled """
        import string

        translator = question.maketrans(dict.fromkeys(string.punctuation))

        temp = question.translate(translator)
        temp = [word.lower() for word in temp.split()]

        question_keywords = temp

        for mentor in mentorsOnDuty:
            keywords = [word.lower() for word in mentor['keywords'].split(',')]
            for word in question_keywords:
                if word in keywords:
                    yield mentor['userid']
                    break
