from slackclient import SlackClient

counter = 0
def channel_info(channel_id):
        channel_info = slack.api_call("channels.info", channel=channel_id)
        if channel_info:
             return channel_info['channel']
             return None
def list_channels():
     channels_call = slack.api_call("channels.list")
     if channels_call.get('ok'):
         return channels_call['channels']
channels = list_channels()

#sends message to a channel
if(slack.rtm_connect()):
        while True:
             mes = slack.rtm_read()
             for message in mes:
                 print (message.get("user"))
                 print ( message)
                 if(message.get("text") is None):
                     print("NONE")
                 
                
