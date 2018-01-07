import requests
from threading import Thread

import pytest


@pytest.fixture
def bot():
    from slackru.slackbot import SlackBot
    bot = SlackBot()
    Thread(target=bot.start).start()

    yield bot

    bot.stop()


@pytest.fixture
def handle_cmd(bot, data):
    return lambda cmd: bot.handle_command(cmd, data.channel, data.userid, data.username)


@pytest.mark.parametrize('command', ["mentors Python Rules!", "mentors"])
def test_mentors_cmd(client, handle_cmd, command):
    if command == "mentors":
        assert handle_cmd(command) is True
    else:
        with pytest.raises(requests.exceptions.ConnectionError):
            handle_cmd(command)


def test_help_cmd(client, handle_cmd):
    resp = handle_cmd("help")
    assert resp is True
