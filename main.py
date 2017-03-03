from slackclient import SlackClient
import question_similarity as q
BOT_NAME = 'readldonalddrumpf'
slack = SlackClient('xoxb-78269858065-q1mlSuaB2tHz96k6035BS5Qe')

counter = 0
botid = 'U2A7XR8I1'
chan ="C2A7YGWRM"
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
                 
                 if(message.get("text") is not  None and message.get("user") !=  "U2A7XR81X"):
                     if(message.get("channel") == "C2ABDJB6K" and message.get("bot_id") != None):
                         counter = counter + 1
                         print("YAYAYAYAY")
                     
                         if(counter <=5):
                             print(counter)      
                             mes = q.get_answer("TRUMP",'trump_speeches',message.get("text"))
                             slack.api_call("chat.postMessage", as_user="true", channel=message.get("channel"), text=mes)
                         if(counter > 5 ):
                             print("ok")
                         if(counter > 5 and message.get("bot_id") == None):
                             counter = 0
                     else:
                        mes = q.get_answer("TRUMP",'trump_speeches',message.get("text"))
                        slack.api_call("chat.postMessage", as_user="true", channel=message.get("channel"), text=mes)
                
