"""
    The new main file for the slack bot
"""
from slackclient import SlackClient

from oauth2client.service_account import ServiceAccountCredentials
from sqlalchemy.sql import select
from sqlalchemy import create_engine
from random import randint
import os
import config
import time
import sqlite3
import httplib2
from apiclient.discovery import build
import datetime
import dateutil.parser
import pygal
import util
import requests
import re
class wHacker:
    def __init__(self,hackerID,request):
        self.h = hackerID
        self.r = request


class eventObj:
    def __init__(self,startime,summary):
        self.s = startime
        self.sum = summary
#List Of Waiting Hacker -> Hackers who are currently waiting for a mentor to respond to them!
LOWH = []
#List Of Active Channels -> Active channels created from the mentor chat.
LOAC = []
BOT_NAME = 'letsmake'
slack_client = SlackClient(config.apiT)
slack_web_client = SlackClient(config.oauthT)
BOTID = config.botID
BOTNAME = "letsmake"
AT_BOT = "@" + BOTNAME
BOT_CHANNEL = "#general"

class Message:
    def __init__(self, botname='', username='', channel='', text='', timestamp='', _type=''):
        self.botname = botname
        self.username = username
        self.channel = channel
        self.text = text
        self.timestamp = timestamp
        self.type = _type

MESSAGE_TYPE = 'desktop_notification'
botID = re.compile('')

def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    messages = []
    output_list = filter(lambda out: 'type' in out and out['type'] == MESSAGE_TYPE and AT_BOT in out['content'],
                         slack_rtm_output)
    for out in output_list:
        print(out)
        channel = out['subtitle']
        username, text = out['content'].split(':')
        timestamp = out['event_ts']
        _type = out['type']
        messages.append(Message(botname, username, channel, text, timestamp, _type))
    return messages

'''
project_type = re.compile('(a|an) .* called')
project_desc = re.compile('(that can|is able to|will) .*\.')
skills_known = re.compile('I know .* (and I am look for people who know|looking for|need help with)')
def process_posting_long(sentences):
    intro_sent = sentences[0]
    proj_type = project_type.search(intro_sent)
    proj_desc = project_desc.search(intro_sent)
    skills_sent = sentences[-1]
    if skills_sent == 'If anyone is interested, pm me.':
        skills_sent = None
'''
def process_posting_short(params):
    print(params.split('--'))

def central_dispatch(msg):
    process_posting_short(msg)
    '''
    firstword = sentences[0].split(' ')[0].strip()
    if firstword == 'a' or firstword == 'an':
        process_posting_long(sentences)
    elif:
        process_posting_short(sentences)'''

#sends message to a channel
if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    LOAC.append("#general")
    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        while True:
            messages = parse_slack_output(slack_client.rtm_read())
            for msg in messages:
                central_dispatch(msg)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
