""" The SlackBot class is defined here """

import os
import json
import time

from slackclient import SlackClient

from slackru import get_db
from slackru.config import config
import slackru.util as util

slack_client = SlackClient(os.environ['SLACK_API_KEY'])
BOTID = config.botID
AT_BOTID = "<@" + BOTID + ">"


class SlackBot:
    def __init__(self):
        self.stayAlive = True

    def run(self):
        READ_WEBSOCKET_DELAY = 1  # 1 second delay between reading from firehose
        if slack_client.rtm_connect():
            util.ifDebugThen(print, "SlackRU connected and running!")
            while self.stayAlive:
                command, channel, userid, username = self.parse_slack_output(slack_client.rtm_read())
                if command and channel:
                    self.handle_command(command, channel, userid, username)
                time.sleep(READ_WEBSOCKET_DELAY)
        else:
            util.ifDebugThen(print, "Connection failed. Invalid Slack token or bot ID?")

    def stop(self):
        self.stayAlive = False

    def parse_slack_output(self, slack_rtm_output):
        """
            The Slack Real Time Messaging API is an events firehose.
            this parsing function returns None unless a message is
            directed at the Bot, based on its ID.
        """
        output_list = slack_rtm_output
        if output_list and len(output_list) > 0:
            for output in output_list:
                if output and 'text' in output and AT_BOTID in output['text']:
                    util.ifDebugThen(print, output['channel'])
                    user_name = util.slack.id_to_username(output['user'])
                    return (output['text'].split(AT_BOTID)[1].strip(),
                            output['channel'],
                            output['user'],
                            user_name)

        return None, None, "", ""

    def handle_command(self, command, channel, userid, username):
        """
            Receives commands directed at the bot and determines if they
            are valid commands. If so, then acts on the commands. If not,
            prompts user for more information.
        """
        util.ifDebugThen(print, username + ": " + userid + ": " + channel + ": " + command)
        dividedCommand = command.split()
        cmd = dividedCommand[0]
        cmd = cmd.lower()

        if cmd == 'mentors':
            util.ifDebugThen(print, len(dividedCommand))
            if len(dividedCommand) == 1:
                resp = util.slack.sendMessage(userid, "Please input a question")
                return resp['ok']
            else:
                question = ' '.join(dividedCommand[1:])
                return Commands.mentors(question, username, userid)
        elif cmd == 'help':
            return Commands.help(userid, username)


class Commands:
    db = get_db()

    @classmethod
    def mentors(cls, question, username, userid):
        util.slack.sendMessage(userid, "Trying to find a mentor")

        matched = cls._matchMentors(question)

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

        return "done"

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
    def _matchMentors(cls, question):
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
