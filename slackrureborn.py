"""
    The new main file for the slack bot
"""
from slackclient import SlackClient
from oauth2client.service_account import ServiceAccountCredentials
from random import randint
import os
import config
import time
import sqlite3
import httplib2
import datetime
import dateutil.parser
import util
import requests
class wHacker:
    def __init__(self,hackerID,request):
        self.h = hackerID
        self.r = request


class eventObj:
    def __init__(self,startime,summary):
        self.s = startime
        self.sum = summary
#List Of Waiting Hacker -> Hackers who are currently waiting for a mentor to respond to them!
#List Of Active Channels -> Active channels created from the mentor chat.
BOT_NAME = 'slackru'
slack_client = SlackClient(config.apiT)
slack_web_client = SlackClient(config.oauthT)
BOTID = config.botID
AT_BOT = "<@" + BOTID + ">"
BOT_CHANNEl = "D4GSK3HG9"
#authorize google calender stuff
#def get_messages():
#    events_obj =  []
#    scopes = ['https://www.googleapis.com/auth/calendar']
#    credentials = ServiceAccountCredentials.from_json_keyfile_name(
#'creds.json', scopes=scopes)
#    http_auth = credentials.authorize(httplib2.Http())
#    service = build('calendar', 'v3', http=http_auth)
#    page_token = None
#
#
#    now = datetime.datetime.utcnow().isoformat() + 'Z'
#    eventsResult = service.events().list(
#            calendarId='hl4bsn6030jr76nql68cen2jto@group.calendar.google.com', timeMin=now, maxResults=5, singleEvents=True,
#            orderBy='startTime').execute()
#    events = eventsResult.get('items', [])
#
#    if not events:
#        print('No upcoming events found.')
#    for event in events:
#        start = event['start'].get('dateTime', event['start'].get('date'))
#        end = event['end'].get('dateTime',event['end'].get('date'))
#        dte = dateutil.parser.parse(end)
#
#        dt =  dateutil.parser.parse(start)
#        dte = dte.strftime('%H:%M')
#        dt = dt.strftime('%H:%M')
#        rn = str(dt) + " - " + str(dte)
#        e = eventObj(rn,event['summary'])
#        events_obj.append(e)
#    return events_obj
#get_messages()
def hours_left():
    epoch_of_end_hack_ru = 1492970400
    curr_epoch_time = int(time.time())
    return (epoch_of_end_hack_ru/3600 - curr_epoch_time/3600)
def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                print(output['text'])
                user_name =  util.grab_user(output['user'])
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel'], \
                       output['user'], \
                       user_name

    return None, None, "", ""

#userid, mentorid
#opens a multiparty im with some users

def create_channel_pair(userid, mentorid, username, mentorname, question):
    userlist = []
    userlist.append(config.botID)
    userlist.append(mentorid)
    print ("This is the question: "+question)
    print ("MENTOR ID    "  + mentorid)
    print ("USERID  " + userid)
    newGroup = slack_web_client.api_call(

            "mpim.open",
            token = config.oauthT,
            users = userid + ',' + mentorid + ',' + config.botID
            )
    if not newGroup.get('ok'):
        return

    print (newGroup)
    test = slack_client.api_call("chat.postMessage", channel = newGroup['group']['id'], text = "This channel has been created to resolve the issue "+mentorname+"'s issue. When the issue has been resolved, mentor please call the @slackru <password> unbusy command. If you do not know the password please contact Architect's Sam or Srihari. Good luck!\nIssue: "+question, as_user = True);
    print (test)
    #Once the active channel is created, put it in the LOAC array so it can be monitored
    #And reminded if things go sour (afk mentor, afk hacker, etc)
    LOAC.append(newGroup['group']['id'])

def handle_command(command:str, channel:str,userid:str,username:str) -> None:
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
        :param command:str the command to parse
        :param channel:str the channel id
        :param userid:str the user id
        :param:str the username 
        """
    print (command)
    dividedCommand = command.split()
    cmd = dividedCommand[0]
    cmd = cmd.lower()
    
    if cmd == 'mentors':
        print (len(dividedCommand)) 
        if len(dividedCommand) == 1:
            util.message(userid,"Please input a question")
        else:
            findMentor(command[8:],username,userid)
    elif cmd == 'help':
        help(userid,username)
        #call the findAvailMentorCommand


def findMentor(command:str,username:str,userid:str) -> str:
    """
        Makes a post request to the server and passes the pairing to he mentee
        :param command:str the parsedcommand
        :param username:str the username
    """
    postData = {}
    postData['data'] = command
    postData['user'] = username
    postData['userid'] = userid
    util.message(userid,"Trying to find a mentor")
    req = requests.post(config.serverurl +'pairmentor',data = postData)
    return req.text
    



     

def help(userid, username):
    util.message(userid,"Hello! You requested the help command, here are a list of commands you can use delimeted by |'s:")
    util.message(userid,"All commands will begin with <AT character>slackru")
    util.message(userid,"""Hacker:\n| mentors <keywords> | -> This command takes keywords and attempts to set you up with a mentor
                    \n| help  | -> Wait what?
                    \n | announcements | -> returns next 5 events \n  | hours | -> returns hours left in the hackathon
                    \nMentor:\n| shortenList <password> <hacker id> | -> Used to help a hackers whose keywords could not be found.
                   \n | unbusy | makes your busy status 0, so you can help more people!
                   \n | busy | -> opposite of the guy above, used when you want to afk I guess""")

def checkTime(channelid):
    ts = time.time()
    timeStuff = slack_web_client.api_call("channels.history", token = config.oauthT,channel = channelid, latest = ts-1850)
    if not timeStuff.get('ok'):
        print("The api call did not work as intended!")
        print(timeStuff)
        return
    latestMessage = timeStuff['messages'][1]['text']
    message(channelid,"This is the latest message: "+latestMessage)
    return


#sends message to a channel
if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("SlackRU connected and running!")
        while True:
            command, channel, userid,username = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel,userid,username)
                #check busy status of all users, their last time busy and if they have been busy for more than 35 minutes
            time.sleep(READ_WEBSOCKET_DELAY)
            #This function will check on all the active channels and if the latest response was an hour ago from the current time
            #The bot will message the channel and let them know it will be stop being monitored and give them insturctions
            #For certain scenarios.
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
