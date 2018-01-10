import json

import slackru.util as util

from slackru import get_db


class Scanner:
    def scheduleScans(self):
        pass


class Commands:
    db = get_db()

    @classmethod
    def mentors(cls, question, username, userid):
        util.slack.sendMessage(userid, "Trying to find a mentor")

        matched = cls.__matchMentors(question)

        questionId = cls.db.insertQuestion(question,
                                username,
                                userid,
                                json.dumps(matched))

        fmt = ("*A HACKER NEEDS YOUR HELP!!!*\n"
                "<@{0}> has requested to be assisted by a mentor.\n"
                "They provided the following statement:\n"
                ">_\"{1}\"_\nCan you help this hacker?\n")

        text = fmt.format(userid, question)

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

        for mentorid in matched:
            channel = util.slack.getDirectMessageChannel(mentorid)
            timestamp = util.slack.sendMessage(channel, text, attachments)['ts']
            cls.db.insertPost(questionId, mentorid, channel, timestamp)

        return matched

    @classmethod
    def help(cls, userid, username):
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
    def __matchMentors(cls, question):
        query = ("SELECT mentors.* FROM shifts "
                "JOIN mentors ON mentors.userid = shifts.userid "
                "WHERE datetime('now', 'localtime') >= datetime(shifts.start) "
                "AND datetime('now', 'localtime') < datetime(shifts.end)")

        matched = []
        query_results = cls.db.runQuery(query)
        for mentor in query_results:
            keywords = [word.lower() for word in mentor['keywords'].split(',')]
            for word in question.split():
                if word.lower() in keywords:
                    matched.append(mentor['userid'])
                    break

        if matched == []:
            for mentor in query_results:
                matched.append(mentor['userid'])

        return matched
