""" The SlackBot class is defined here """

import os
import time
import logging

from slackclient import SlackClient

from slackru.config import config
from slackru.util import slack
from slackru.bot.commands import Commands

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

    def run(self):
        """ Run SlackBot """
        READ_WEBSOCKET_DELAY = 1  # 1 second delay between reading from firehose
        if slack_client.rtm_connect():
            logging.info("SlackRU connected and running!")
            self.isAlive = True
            while self.stayAlive:
                command, channel, userid, username = self.parse_slack_output(slack_client.rtm_read())
                if command and channel:
                    self.handle_command(command, channel, userid, username)
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
                            output['user'],
                            slack.id_to_username(output['user']))

        return None, None, None, None

    def handle_command(self, command: str, channel: str, userid: str, username: str):
        """
            Receives commands directed at the bot and determines if they
            are valid commands. If so, then acts on the commands. If not,
            prompts user for more information.
        """
        logging.debug(userid + ": " + channel + ": " + command)
        dividedCommand = command.split()
        cmd = dividedCommand[0]
        cmd = cmd.lower()
        args = dividedCommand[1:]

        if '-h' in args or '--help' in args:
            return Commands.help(userid, command=cmd)

        if cmd == 'mentors':
            question = ' '.join(args)
            return Commands.mentors(question, userid)
        elif cmd == 'help':
            command = None if not args else args[0]
            return Commands.help(userid, command=command)
        elif cmd == 'register':
            mentor_data = ' '.join(args)
            return Commands._register(mentor_data, userid, username)
