import json

import slackru.util as util
import slackru.bot.messages as M

from slackru import get_db


class Scanner:
    def scheduleScans(self):
        pass


class Commands:
    db = get_db()

    @classmethod
    def mentors(cls, question, userid):
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
    def _getMatchedMentorIDs(cls, question, mentorsOnDuty):
        for mentor in mentorsOnDuty:
            keywords = [word.lower() for word in mentor['keywords'].split(',')]
            for word in question.split():
                if word.lower() in keywords:
                    yield mentor['userid']
                    break
