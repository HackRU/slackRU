from slackclient import SlackClient 
import os
import config
import time
BOT_NAME = 'helperbot'
print(config.apiT)
slack_client = SlackClient(config.apiT)
BOTID = config.botID
AT_BOT = "<@" + BOTID + ">"
def channel_info(channel_id):
        channel_info = slack_client.api_call("channels.info", channel=channel_id)
        if channel_info:
             return channel_info['channel']
             return None

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
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel']
    return None, None

def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    response = "Not sure what you mean. Use the  "\
               "* command with numbers, delimited by spaces."
    if command.startswith("KEK"):
        response = "Sure...write some more code then I can do that!"
    slack_client.api_call("chat.postMessage", channel=channel,
                          text=command, as_user=True)
def list_channels():
     channels_call = slack_client.api_call("channels.list")
     if channels_call.get('ok'):
         return channels_call['channels']
channels = list_channels()
#sends message to a channel
if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?") 



