import sys
import os

os.environ['SLACK_CONFIG'] = 'development'
if sys.argv[1] == '--prodbot':
    os.environ['SLACK_CONFIG'] = 'production'

from slackru.config import config


def server():
    from slackru import create_app
    config.setup()
    app = create_app(config)
    app.run()


def slackbot():
    from slackru.slackbot import SlackBot
    bot = SlackBot()
    bot.run()


options = dict.fromkeys(['-s', '--server'], server)
options.update(dict.fromkeys(['-b', '--slackbot', '--prodbot'], slackbot))

if __name__ == '__main__':
    options[sys.argv[1]]()
