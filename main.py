import sys
import os

os.environ['SLACK_CONFIG'] = 'development'
from slackru.config import config


def server():
    from slackru import create_app
    app = create_app(config)
    app.run()


def slackbot():
    from slackru.slackbot import SlackBot
    bot = SlackBot()
    bot.run()


options = dict.fromkeys(['-s', '--server'], server)
options.update(dict.fromkeys(['-b', '--slackbot'], slackbot))

if __name__ == '__main__':
    options[sys.argv[1]]()
