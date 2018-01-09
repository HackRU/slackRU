from threading import Thread

import pytest


@pytest.mark.parametrize('command', ["mentors Python Rules!", "mentors"])
def test_mentors_cmd(client, handle_cmd, command):
    if command == "mentors":
        assert handle_cmd(command) is True
    else:
        assert handle_cmd(command) == 'done'


def test_help_cmd(client, handle_cmd):
    resp = handle_cmd("help")
    assert resp is True


@pytest.mark.parametrize('questionIndex, mentorIndexes', [(0, [0]), (1, [1]), (2, [0, 1])])
def test_matchMentors(data, questionIndex, mentorIndexes):
    from slackru.slackbot import Commands
    matched = Commands._matchMentors(data['question'][questionIndex])
    assert matched == [data['mentorid'][i] for i in mentorIndexes]


@pytest.fixture(scope='module')
def handle_cmd(bot, data):
    return lambda cmd: bot.handle_command(cmd, data['channel'], data['userid'], data['username'])


@pytest.fixture(scope='module')
def bot():
    from slackru.slackbot import SlackBot
    bot = SlackBot()
    Thread(target=bot.run).start()

    yield bot

    bot.stop()
