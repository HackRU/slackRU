#!/usr/bin/env python3

""" Use this script to manually run the server OR slackbot

    usage:
        ./main.py -h
"""

import os
import argparse

from slackclient import SlackClient

import slackru.util
from slackru.util.slackapi import SlackAPI


slackru.util.slack = SlackAPI(SlackClient(os.environ['SLACK_API_KEY']))


def server():
    from slackru import create_app
    app = create_app()
    app.run()


def slackbot():
    from slackru.bot.slackbot import SlackBot
    bot = SlackBot()
    bot.run()


if __name__ == "__main__":
    runtype_opts = {'server': server, 'slackbot': slackbot}

    parser = argparse.ArgumentParser()
    parser.add_argument('runtype', choices=[key for key in runtype_opts.keys()])
    parser.add_argument('-c', '--config', dest='config', choices=['development', 'production'], default='development')
    args = parser.parse_args()

    os.environ['SLACK_CONFIG'] = args.config

    runtype_opts[args.runtype]()
