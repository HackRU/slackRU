import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument('runtype')
parser.add_argument('-c', '--config', dest='config', default='development')
args = parser.parse_args()

os.environ['SLACK_CONFIG'] = args.config
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


if __name__ == "__main__":
    {'server': server, 'slackbot': slackbot}[args.runtype]()
