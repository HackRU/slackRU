""" The SlackBot class is defined here """

import os
import time
import logging

from slackclient import SlackClient

from slackru.config import config
from slackru.bot.actions import Commands, Scanner
import slackru.util as util

slack_client = SlackClient(os.environ['SLACK_API_KEY'])
BOTID = config.botID
AT_BOTID = "<@" + BOTID + ">"


class SlackBot:
    """ Main SlackBot Class

    Runs SlackBot and monitors Slack workspace
    """
    def __init__(self):
        self.isAlive = False
        self.stayAlive = True
        self.scanner = Scanner()

    def run(self):
        """ Run SlackBot """
        self.scanner.scheduleScans()
        READ_WEBSOCKET_DELAY = 1  # 1 second delay between reading from firehose
        if slack_client.rtm_connect():
            logging.info("SlackRU connected and running!")
            self.isAlive = True
            while self.stayAlive:
                command, channel, userid = self.parse_slack_output(slack_client.rtm_read())
                if command and channel:
                    self.handle_command(command, channel, userid)
                time.sleep(READ_WEBSOCKET_DELAY)
        else:
            logging.info("Connection failed. Invalid Slack token or bot ID?")

    def stop(self):
        """ Stop SlackBot """
        self.stayAlive = False

    def parse_slack_output(self, slack_rtm_output: '{str: str}|None') -> '(str, str, str)|(None,None,None)':
        """
            The Slack Real Time Messaging API is an events firehose.
            this parsing function returns None unless a message is
            directed at the Bot, based on its ID.
        """
        output_list = slack_rtm_output
        if output_list and len(output_list) > 0:
            for output in output_list:
                if output and 'text' in output and AT_BOTID in output['text']:
                    return (output['text'].split(AT_BOTID)[1].strip(),
                            output['channel'],
                            output['user'])

        return None, None, None

    def handle_command(self, command: 'str', channel: 'str', userid: 'str'):
        """
            Receives commands directed at the bot and determines if they
            are valid commands. If so, then acts on the commands. If not,
            prompts user for more information.
        """
        logging.debug(userid + ": " + channel + ": " + command)
        dividedCommand = command.split()
        cmd = dividedCommand[0]
        cmd = cmd.lower()

        if cmd == 'mentors':
            if len(dividedCommand) == 1:
                resp = util.slack.sendMessage(userid, "Please input a question")
                return resp['ok']
            else:
                question = ' '.join(dividedCommand[1:])
                return Commands.mentors(question, userid)
        elif cmd == 'help':
            return Commands.help(userid)
