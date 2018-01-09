""" The SlackBot class is defined here """

import os
import time

from slackclient import SlackClient

from slackru.config import config
from slackru.bot.actions import Commands, Scanner
import slackru.util as util

slack_client = SlackClient(os.environ['SLACK_API_KEY'])
BOTID = config.botID
AT_BOTID = "<@" + BOTID + ">"


class SlackBot:
    def __init__(self):
        self.stayAlive = True
        self.scanner = Scanner()

    def run(self):
        self.scanner.scheduleScans()
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
