import os

from slackru import create_app
from slackru.bot.slackbot import SlackBot


pid = os.fork()
if not pid:
    bot = SlackBot()
    bot.run()

application = create_app()
