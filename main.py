""" Use this script to manually run the server OR slackbot

    usage:
        python main.py <server|slackbot> [-c <production|development>]
"""

import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('runtype')
parser.add_argument('-c', '--config', dest='config', default='development')
args = parser.parse_args()

os.environ['SLACK_CONFIG'] = args.config


def server():
    from slackru import create_app
    app = create_app()
    app.run()


def slackbot():
    from slackru.slackbot import SlackBot
    bot = SlackBot()
    bot.run()


if __name__ == "__main__":
    {'server': server, 'slackbot': slackbot}[args.runtype]()
