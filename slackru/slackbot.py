""" The SlackBot class is defined here """
import os
import time
import requests

from slackclient import SlackClient

import slackru.util as util
from slackru.config import config

# List Of Waiting Hacker -> Hackers who are currently waiting for a mentor to respond to them!
# List Of Active Channels -> Active channels created from the mentor chat.
slack_client = SlackClient(os.environ['SLACK_API_KEY'])
BOTID = config.botID
AT_BOTID = "<@" + BOTID + ">"


class SlackBot:
    def run(self):
        READ_WEBSOCKET_DELAY = 1  # 1 second delay between reading from firehose
        if slack_client.rtm_connect():
            util.ifDebug(print, "SlackRU connected and running!")
            while True:
                command, channel, userid, username = self.parse_slack_output(slack_client.rtm_read())
                if command and channel:
                    self.handle_command(command, channel, userid, username)
                    # check busy status of all users, their last time busy and if they have been busy for more than 35 minutes
                time.sleep(READ_WEBSOCKET_DELAY)
                # This function will check on all the active channels and if the latest response was an hour ago from the current time
                # The bot will message the channel and let them know it will be stop being monitored and give them insturctions
                # For certain scenarios.
        else:
            util.ifDebug(print, "Connection failed. Invalid Slack token or bot ID?")

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
                    util.ifDebug(print, output['channel'])
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
            returns back what it needs for clarification.
            :param command:str the command to parse
            :param channel:str the channel id
            :param userid:str the user id
            :param:str the username
            """
        util.ifDebug(print, username + ": " + userid + ": " + channel + ": " + command)
        dividedCommand = command.split()
        cmd = dividedCommand[0]
        cmd = cmd.lower()

        if cmd == 'mentors':
            util.ifDebug(print, len(dividedCommand))
            if len(dividedCommand) == 1:
                util.slack.sendMessage(userid, "Please input a question")
            else:
                self.pairMentor(command[8:], username, userid)
        elif cmd == 'help':
            help(userid, username)
            # call the findAvailMentorCommand

    def pairMentor(self, question, username, userid):
        """
            Makes a post request to the server and passes the pairing to he mentee
            :param command:str the parsedcommand
            :param username:str the username
        """
        postData = {}
        postData['question'] = question
        postData['username'] = username
        postData['userid'] = userid
        util.slack.sendMessage(userid, "Trying to find a mentor")
        req = requests.post(config.serverurl + 'pairmentor', data=postData)
        return req.text

    def help(self, userid, username):
        util.slack.sendMessage(userid, "Hello! You requested the help command, here are a list of commands you can use delimeted by |'s:")
        util.slack.sendMessage(userid, "All commands will begin with <AT character>slackru")
        util.slack.sendMessage(userid, """Hacker:\n| mentors <keywords> | -> This command takes keywords and attempts to set you up with a mentor
                        \n| help  | -> Wait what?
                        \n | announcements | -> returns next 5 events \n  | hours | -> returns hours left in the hackathon
                        \nMentor:\n| shortenList <password> <hacker id> | -> Used to help a hackers whose keywords could not be found.
                       \n | unbusy | makes your busy status 0, so you can help more people!
                       \n | busy | -> opposite of the guy above, used when you want to afk I guess""")
