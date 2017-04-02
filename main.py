from slackclient import SlackClient
from sqlalchemy.sql import select
from sqlalchemy import create_engine
import os
import config
import time
import sqlite3

class wHacker:
    def __init__(self,hackerID,request):
        self.h = hackerID
        self.r = request

#List Of Waiting Hacker -> Hackers who are currently waiting for a mentor to respond to them!
LOWH = []
#List Of Active Channels -> Active channels created from the mentor chat.
LOAC = []
BOT_NAME = 'helperbot'
slack_client = SlackClient(config.apiT)
slack_web_client = SlackClient(config.oauthT)
BOTID = config.botID
AT_BOT = "<@" + BOTID + ">"
BOT_CHANNEl = "D4GSK3HG9"
def grab_user(use):
    api =slack_client.api_call('users.list')
    if(api.get('ok')):
            users = api.get('members')
            for user in users:
                if 'name' in user and user.get('id') == use:
                    return user['name'] 
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
                print(output)
                
                user_name =  grab_user(output['user'])
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel'], \
                       output['user'], \
                       user_name

            elif output and 'text' in output and BOT_CHANNEl in output['channel'] and AT_BOT not in output['user']:

                user_name =  grab_user(output['user'])
                return output['text'], \
                       output['channel'], \
                       output['user'], \
                       user_name
    return None, None, "", ""

#userid, mentorid
#opens a multiparty im with some users

def create_channel_pair(userid, mentorid, username, mentorname):
        userlist = []
        userlist.append(config.botID)
        userlist.append(mentorid)
	newGroup = slack_web_client.api_call(

		"mpim.open",
                token = config.oauthT,
                users = userid + ',' + mentorid + ',' + config.botID
		)
	if not newGroup.get('ok'):
		print "Error!"
		print newGroup
		return

        print (newGroup)
        test = slack_client.api_call("chat.postMessage", channel = newGroup['group']['id'], text = "This channel has been created to resolve the issue "+username+"'s issue. When the issue has been resolved, mentor please call the @helperbot <password> unbusy command. If you do not know the password please contact Architect's Sam or Srihari. Good luck!", as_user = True);
        print (test)
        #Once the active channel is created, put it in the LOAC array so it can be monitored
        #And reminded if things go sour (afk mentor, afk hacker, etc)
        LOAC.append(newGroup['group']['id'])

def handle_command(command, channel,userid,username):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
   	"""
    #The command will be divided into several parts, incase a certain command needs paramters
    #For example the dbmanager should take in some options regarding who to delete or add
    #So dividedCommand represent a list of the entire command separated by spaces.
    dividedCommand = command.split()
    print(dividedCommand)
    
    if(dividedCommand[0] == "checkStatus"):
        if(command[1] != config.mpass):
            message(userid,"Incorrect password, Try again or ask Architects Sam or Srihari for the password!")
            return
        conn = sqlite3.connect("main.db")
        Mentor = conn.execute("select busy from mentors where mentorid=?",[userid])
        if(len(Mentor) == 0):
            message(userid, "Couldnt find you in mentor database, contact Sam or Srihari!")
            return
        else:
            message(userid, "Your busy status is currently: "+Mentor[0]+"\nWhere 0 is unbusy and 1 is busy!")
        return
    #This command deals with making a mentor busy or unbusy
    if(dividedCommand[0] == "busy" or dividedCommand[0] == "unbusy"):
        if(command[1] != config.mpass):
            message(userid,"Incorrect password, Try again or ask Sam or Srihari for the password!")
            return
        
        if dividedCommand[0] == "busy":
            dbManage(userid,0,[0,config.dbpass,"BS",userid,1])
        else:
            dbManage(userid,0,[0,config.dbpass,"BS",userid,0])
    
    #This is a troll command, play with it if you wish
    if(dividedCommand[0] == "karlin"):
        slack_client.api_call("chat.postMessage",channel = channel, text = "HE IS THE IMPOSTER SCREW HIM, I am the alpha Karlin!")
        return
    #This command was used to test timestamps on python, delete if you want (delete the function as well)
    if(dividedCommand[0] == "timetest"):
        checkTime(channel)
        return
    
    #Main function for dealing with mentors
    if(dividedCommand[0] == "mentors"):
    	print(userid)
        if(len(dividedCommand) == 1):
    	    slack_client.api_call("chat.postMessage", channel=userid,
		    text="Hello, to better pair you with a mentor, please call the command mentors <keywords>" , as_user=True)
    	    #create_channel_pair(userid, "U44AZ0GP6", username, "Srihari")
            return
        else:
            findAvaliableMentor(username,userid,dividedCommand)
            return
    #help command will give all current commands avliable for BOTH mentor and Hacker (may need to be updated with more commands)
    if(dividedCommand[0] == "help"):
        help(userid,username)
        return
            #Tell the user about all the commands that come with this cool bot!
    
    #command for mentors to take a hacker from the List Of Waiting Hackers (LOWH) and help them out
    if(dividedCommand[0] == "shortenlist"):
        if(len(dividedCommand) != 3):
            message(userid, "I apologize, the shortenList command takes two arguments: <password> and <hackerid>, please try again!")
            return
        else:
            shortenlist(userid, username, dividedCommand)
            return

    slack_client.api_call("chat.postMessage", channel=userid,
	text="I'm sorry I couldn't understand that command, try using the command help for a list of commands you can use!", as_user=True)
		
    return

def help(userid, username):
    message(userid,"Hello! You requested the help command, here are a list of commands you can use delimeted by |'s:")
    message(userid,"All commands will begin with <AT character>karlin!")
    message(userid,"""Hacker:\n| menotors <keywords> | -> This command takes keywords and attempts to set you up with a mentor
                    \n| help  | -> Wait what?
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
     channels_call = slack_client.api_call("channels.list")
     if channels_call.get('ok'):
         return channels_call['channels']

def shortenlist(mentorID, mentorName, commandOptions):
    if(commandOptions[1] != config.mpass):
        message(mentorID, "The password inserted was incorrect, please try again. If you need the password message Architect Sam or Architect Shri.")
        return
    hackerID = commandOptions[2].upper()
    found = 0
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
                LOWH.remove(i)
            #create channel pair
        userInfo = slack_client.api_call("user.info", user=hackerID, as_user=True)
        print("Trying to pair from list...")
        #create_channel_pair(hackerID, mentorID,userInfo['user']['name'], mentorName)

def findAvaliableMentor(hackerName,userid ,keywords):
    #This is used later on if we have to put this user in the list of waiting hackers
    saveKeywords = keywords
    #Join the keywords for an easier way to search for keywords
    keywords = " ".join(keywords)
    conn = sqlite3.connect("main.db")
    #Find an unbusy mentor
    count = 0;
    found = [0,"dummy"];
    listOfUnBusyMentors = conn.execute("select name from mentors where busy=0")
    #This entire process below is for finding a mentor that is currently not busy and contains
    #0 - several keywords that the user's request has
    for i in listOfUnBusyMentors:
        MentorName = i[0];
        listOfKeywords = conn.execute("select keywords from mentors where name = ?",[MentorName])
        for j in listOfKeywords:
            Keywords = j[0].split(",")
            for k in Keywords:
                k = k.lower()
                if k in keywords:
                    count = count+1

        #Everytime the count is larger than the currently largest count, swap a new found            
        if count > found[0]:
            found[0] = count
            found[1] = MentorName
        
        count = 0 
    #If the dummy value is still valid, then we know no keywords were found :(    
    if(found[1] == "dummy"):
        print("Could not find suitable mentor!")
        #This method below should be uncommented once we have the mentors channel set up and we have the mentor channel id
        # slack_client.api_call("chat.postMessage", channel=mentorsChannel,
        #    text="There is currently a hacker by the name of: "+hackerName+"Who is having trouble with: "+keywords+" Please use the command @helperbot shortenList <password> <userid>  in order to help them with this! The password is mentors2017 and this users id is: "+userid+"", as_user=True)
        message(userid,"We could not find a mentor with the paramters you gave us, we have placed your request on a list. If a mentor believes they can help you with this issue they will respond to you! You are more than welcome to use the mentors command again with new keywords!")
        f = 0
        for i in LOWH:
            if i.h == userid:
                f = 1
        #If they are currently not in the waiting list, put them on it
        if(f == 0):
            strKeywords = ""
            i = 1  
            while(i < len(saveKeywords)):
                strKeywords += (saveKeywords[i])
                i+=1
            newWaitingHacker = wHacker(userid,strKeywords)
            LOWH.append(newWaitingHacker)

    else:
        for i in LOWH:
            if(i.h == hackerID):
                LOWH.remove(i)
        print("Suitable mentor found!\n"+found[1]+"!")
        conn.execute("update mentors set busy = 1 where name = ?",[name])
        #create a channel between the two
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
    if(dbcommand[2] == "Delete" or dbcommand[2] == "D"):
        print("Attempting to delete...")
		#Option Params: mentorid
        #Cannot really delete a user so we will make them permanently busy
        if len(command) != 3:
            print("Incorrect arguments got: "+len(command)+" need 3")
            return
        print("Deleting...")
        conn.execute("update mentors set busy = 1 where mentor=?",[command[3]])
        print(conn.execute("select * from mentor"))
        return

	if(dbcommand[2] == "AddMentor" or dbcommand[2] == "AM"):
		#Option Params: name busy keywords mentorid
		print("Adding new Mentor")
        if len(command) != 7:
            print("Incorrect arguments got: "+len(command)+"arguments instead of 7")
            return
        conn.execute("insert into mentors values (?,?,??)",[command[3],command[4],command[5],command[6]])
        print(conn.execute("select * from mentor"))
        return

	if(dbcommand[2] == "BusyStat" or dbcommand[2] == "BS"):
		#Option Params: mentorid <0,1> 0 for unbusy 1 for busy
		print("Changing busy status...")
        if command[3] == 0:
            if len(conn.execute("select name from mentors where mentorid=?",[command[3]])) == 0:
                message(mentorid, "I tried tried to change your status in the database, but could not, please contact Architect Sam or Shrihari!")
                return
            conn.execute("update mentors set busy = 0 where mentorid =?",[command[3]])

        else:
            if len(conn.execute("select name from mentors where mentorid=?",[command[3]])) == 0:
                message(mentorid, "I tried tried to change your status in the database, but could not, please contact Architect Sam or Shrihari!")
                return
            conn.execute("update mentors set busy = 1 where mentorid =?",[command[3]]) 

	conn.commit()
	conn.close()



def checkOnChannels():
    for i in LOAC:
        channelINFO = slack_web_client.api_call("channels.history", channel = i, as_user = True)
        currentTS = time.time()
        #If the latest message on the chat was an hour ago, ask the chat if everything is ok once
        if(currentTS > channelINFO['latest']+3600):
            message(i,"The last message sent on this channel is an hour long! Just making sure everything is alright!")
            message(i, "For Mentors:")
            message(i,"If you are finished with the issue make sure to run @helperbot <password> unbusy if you haven't already")
            message(i,"(message Architects Sam or Shrihari for that!)")
            message(i,"For Hackers:")
            message(i,"If your mentor is not responding, you can run the command for a mentor again")
            message(i,"This channel will stop being monitored by helperbot.")
            LOAC.remove(i)
            
            

#sends message to a channel
if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
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




