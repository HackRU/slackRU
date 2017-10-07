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
    command = dividedCommand[0]
    command = command.lower()
    if command == 'mentors':
        findMentor(command,username)
    elif command == 'help':
        help(userid,username)
        #call the findAvailMentorCommand


def findMentor(command:str,username:str) -> str:
    """
        Makes a post request to the server and passes the pairing to he mentee
        :param command:str the parsedcommand
        :param username:str the username
    """
    postData = {}
    postData[username] = command
    req = requests.post(config.serverurl +'pairmentor',data = postData)
    return req.text
    



     

def help(userid, username):
    message(userid,"Hello! You requested the help command, here are a list of commands you can use delimeted by |'s:")
    message(userid,"All commands will begin with <AT character>slackru")
    message(userid,"""Hacker:\n| mentors <keywords> | -> This command takes keywords and attempts to set you up with a mentor
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

def message(channelid, message):
    slack_client.api_call("chat.postMessage", channel=channelid,
    text=message, as_user=True)
def list_channels():
    channels_call = slack_client.api_call("groups.list")
    if channels_call.get('ok'):
        return channels_call['groups']
def shortenlist(mentorID, mentorName, commandOptions):
    if(commandOptions[1] != config.mpass):
        message(mentorID, "The password inserted was incorrect, please try again. If you need the password message Architect Sam or Architect Sri.")
        return
    hackerID = commandOptions[2].upper()
    found = 0
    messageL = ""
    #look for the hacker on the list...
    for i in LOWH:
        if(i.h == hackerID):
            found = 1
            continue
    #Isn't on the list? two things possible -> the mentor typed it in wrong or they hacker already found another mentor
    #Either way, the entire list of hackers on the list are printed to the mentor so they can see the id
    if(found == 0):
        message(mentorID, "I couldn't seem to find the hacker you tried to look for, please look back at the messages sent to the mentor chat and make sure you got the right thing! If you are sure you put in the right ID, then the hacker probably found another mentor. Here is the current list of hackers who are waiting for help...")
        listOfHackers = ""
        for i in LOWH:
            message(mentorID, i.h+"\t"+i.r+"\n")
        print("This is the hackerID: "+hackerID)
    else:
        #remove them from the waiting list
        for i in LOWH:
            if(i.h == hackerID):
                messageL = i.r
                LOWH.remove(i)
            #create channel pair
        userInfo = slack_client.api_call("user.info", user=hackerID, as_user=True)
        print("Trying to pair from list...")
        create_channel_pair(hackerID, mentorID,util.grab_user(hackerID), mentorName,messageL)

def findAvaliableMentor(hackerName,userid ,keywords):
    #This is used later on if we have to put this user in the list of waiting hackers
    saveKeywords = keywords;
    strKeywords = ""
    for i in saveKeywords:
        if i == "mentors":
            continue
        strKeywords += i
        strKeywords += " "
    print("These are the keywords: "+strKeywords)
    goodMentors = [];
    #Join the keywords for an easier way to search for keywords
    conn = sqlite3.connect("main.db")
    #Find an unbusy mentor
    count = 0
    found = [0,"dummy"]
    listOfUnBusyMentors = conn.execute("select mentorid from mentors where busy=0")
    #This entire process below is for finding a mentor that is currently not busy and contains
    #0 - several keywords that the user's request has
    for i in listOfUnBusyMentors:
        Mentorid = i[0];
        listOfKeywords = conn.execute("select keywords from mentors where mentorid = ?",[Mentorid])
        for j in listOfKeywords:
            Keywords = j[0].split(",")
            for k in Keywords:
                k = k.lower()
                for z in keywords:
                    z = z.lower()
                    if k == z:
                        count = count+1

        #Everytime the count is larger than the currently largest count, swap a new found
        if count > found[0]:
            found[0] = count
            found[1] = Mentorid

        if count > 0:
            goodMentors.append(Mentorid)

        count = 0
    #If the dummy value is still valid, then we know no keywords were found :(

    if(found[1] == "dummy"):
        print("Could not find suitable mentor!")
        #This method below should be uncommented once we have the mentors channel set up and we have the mentor channel id
        slack_client.api_call("chat.postMessage", channel='G53T6D0A2',
            text="There is currently a hacker with the ID: "+str(userid)+" Who is having trouble with: "+strKeywords+". Please use the command <AT>slackru shortenlist <password> <userid>  in order to help them with this if you can! The password is mentors2017", as_user=True)
        message(userid,"We could not find a mentor with the paramters you gave us, we have placed your request on a list. If a mentor believes they can help you with this issue they will respond to you! You are more than welcome to use the mentors command again with new keywords!")
        f = 0
        strKeywords = ""
        for i in LOWH:
            if i.h == userid:
                f = 1
        #If they are currently not in the waiting list, put them on it
        if(f == 0):
            i = 1
            while(i < len(saveKeywords)):
                strKeywords += (saveKeywords[i])
                strKeywords += " ";
                i+=1
            newWaitingHacker = wHacker(userid,strKeywords)
            LOWH.append(newWaitingHacker)

    else:
        if found[0] < 3:
            randomMentor = randint(0,len(goodMentors)-1);
            found[1] = goodMentors[randomMentor]
        for i in LOWH:
            if(i.h == userid):
                LOWH.remove(i)
        print("Suitable mentor found!\n"+found[1]+"!")
        conn.execute("update mentors set busy = 1 where mentorid = ?",[found[1]])

        #create a channel between the two
        create_channel_pair(userid,found[1],util.grab_user(userid),util.grab_user(found[1]),strKeywords)
        conn.commit()

    conn.close()

#This is for management of the database woot woot
#This function has a lot of functionality (no pun intended) the dbcommand paramter
#Is a list of different strings which represent different options
#Below each if statemenet are the paramters that the command needs in order to continue the action on the database
def dbManage(mentorid,channelid, dbcommand):
    conn = sqlite3.connect('main.db')
        #params: dbmanager <password> <command> <options>
    #delimit and tokenize the command, first part is pass
    if(dbcommand[1] != config.dbpass):
        slack_client.api_call("chat.postMessage", channel=channel,text="Incorrect Password.", as_user=True)
        return
        #delimit and tokenize the command for the second part for the command
    elif(dbcommand[2] == "delete" or dbcommand[2] == "d"):
        print("Attempting to delete...")
                #Option Params: mentorid
        #Cannot really delete a user so we will make them permanently busy
        if len(command) != 3:
            print("Incorrect arguments got: "+str(len(dbcommand))+" need 3")
        print("Deleting...")
        conn.execute("update mentors set busy = 1 where mentor=?",[dbcommand[3]])
        print(conn.execute("select * from mentor"))

    elif(dbcommand[2] == "addmentor" or dbcommand[2] == "am"):
                #Option Params::: name busy keywords mentorid
        print("Adding new Mentor")
        if len(dbcommand) != 9:
            print("Incorrect arguments got: "+str(len(dbcommand))+" arguments instead of 7")
            return
        conn.execute("insert into mentors values (?,?,?,?,?)",[dbcommand[4]+" "+dbcommand[5],dbcommand[6],dbcommand[7],mentorid,dbcommand[8]])
        print(conn.execute("select * from mentors"))

    elif(dbcommand[2] == "busystat" or dbcommand[2] == "bs"):
                #Option Params: mentorid <0,1> 0 for unbusy 1 for busy
        print("Changing busy status...")
        if dbcommand[4] == 0:
            match = conn.execute("select mentorid from mentors where mentorid=?",[dbcommand[3]])
            if list(match) ==  []:
                message(mentorid, "I tried tried to change your status in the database, but could not, please contact Architect Sam or Shrihari!")
            else:
                conn.execute("update mentors set busy = 0 where mentorid =?",[dbcommand[3]])
                message(mentorid,"All good buddy, set you to unbusy!")
        if dbcommand[4] == 1:
            match = conn.execute("select mentorid from mentors where mentorid=?",[dbcommand[3]])
            if list(match) ==  []:
                message(mentorid, "I tried tried to change your status in the database, but could not, please contact Architect Sam or Shrihari!")
            else:
                conn.execute("update mentors set busy = 1 where mentorid =?",[dbcommand[3]])
                message(mentorid,"All good buddy, set you to busy!")

    elif(dbcommand[2] == 'setinactive'):
        match = conn.execute("select mentorid from mentors where mentorid=?",[dbcommand[3]])
        if list(match) ==  []:
            message(mentorid, "I tried tried to change your status in the database, but could not, please contact Architect Sam or Shrihari!")
        else:
            conn.execute("update mentors set inactive = 1 where mentorid =?",[dbcommand[3]])
            conn.execute("update mentors set busy = 1 where mentorid=?",[dbcommand[3]])
            message(mentorid,"Made you inactive!!")

    elif(dbcommand[2] == 'setactive'):
        match = conn.execute("select mentorid from mentors where mentorid=?",[dbcommand[3]])
        if list(match) ==  []:
            message(mentorid, "I tried tried to change your status in the database, but could not, please contact Architect Sam or Shrihari!")
        else:
            conn.execute("update mentors set inactive = 0 where mentorid =?",[dbcommand[3]])
            conn.execute("update mentors set busy = 0 where mentorid =?",[dbcommand[3]])
            message(mentorid,"Made you active!!")


    elif(dbcommand[2] == 'listactivity'):
        match1 = conn.execute("select name from mentors where inactive=1")

        c = list(match1.fetchall())
        if list(c) == []:
            message(mentorid,"List contains no inactive mentors!")
        else:
            message(mentorid,"Current Inactive Mentors\n________________________")
            for i in c:
                message(mentorid,str(i[0]).upper() + '\n')

        match2 = conn.execute("select name from mentors where inactive=0")
        c =  list(match2.fetchall())

        if list(match2.fetchall()) == None:
            message(mentorid,"List contains no active mentors!")
        else:
            message(mentorid,"Current Active Mentors\n______________________")
            for i in c:
                message(mentorid,i[0].upper()+"\n")

    conn.commit()
    conn.close()



def checkOnChannels():
    for i in LOAC:
        channelINFO = slack_web_client.api_call("mpim.history", channel = i)
        currentTS = int(time.time())
        #If the latest message on the chat was an hour ago, ask the chat if everything is ok once
        if(currentTS > int(float(channelINFO['messages'][0]['ts']))+(3600*2)):
            message(i,"The last message sent on this channel is an hour long! Just making sure everything is alright!")
            message(i, "For Mentors:")
            message(i,"If you are finished with the issue make sure to run @slackru <password> unbusy if you haven't already")
            message(i,"(message Architects Sam or Srihari for that!)")
            message(i,"For Hackers:")
            message(i,"If your mentor is not responding, you can run the command for a mentor again")
            message(i,"This channel will stop being monitored by slackru.")
            LOAC.remove(i)



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
            checkOnChannels()
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
