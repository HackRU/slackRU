from slackclient import SlackClient 
import os
import config
import time
import sqlite3
#creat the table
BOT_NAME = 'helperbot'
slack_client = SlackClient(config.apiT)
slack_web_client = SlackClient(config.oauthT)
BOTID = config.botID
AT_BOT = "<@" + BOTID + ">"
def channel_info(channel_id):
        channel_info = slack_client.api_call("channels.info", channel=channel_id)
        if channel_info:
             return channel_info['channel']
             return None

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
    return None, None, "", ""

#userid, mentorid
def create_channel_pair(userid, mentorid, username, mentorname):
	newGroup = slack_web_client.api_call(

		"mpim.open",
                token = config.oauthT,
                users = mentorid +','+ userid
		)
	if not newGroup.get('ok'):
		print "Error!"
		print newGroup
		return

        print (newGroup)

def handle_command(command, channel,userid,username):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    print(userid)
    create_channel_pair(userid, "U44AZ0GP6", username, "Srihari")
    slack_client.api_call("chat.postMessage", channel=channel,
                          text=command, as_user=True)
def list_channels():
     channels_call = slack_client.api_call("channels.list")
     if channels_call.get('ok'):
         return channels_call['channels']
#sends message to a channel
if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        while True:
            command, channel, userid,username = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel,userid,username)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?") 





