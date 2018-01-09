from threading import Thread

import pytest


mentors_cmd_params = [("mentors Python Rules!", [0]),
                      ("mentors My Java code is not working", [1]),
                      ("mentors I hate C++", [0, 1]),
                      ("mentors", [])]

mentor_cmd_ids = ['{}, {}'.format(param[0], param[1])
                  for param in mentors_cmd_params]


@pytest.mark.parametrize('command, mentorIndexes', mentors_cmd_params, ids=mentor_cmd_ids)
def test_mentors_cmd(client, data, handle_cmd, command, mentorIndexes):
    if command == 'mentors':
        assert handle_cmd(command) is True
    else:
        assert handle_cmd(command) == [data['mentorid'][i] for i in mentorIndexes]


def test_help_cmd(client, handle_cmd):
    resp = handle_cmd("help")
    assert resp is True


@pytest.fixture(scope='module')
def handle_cmd(bot, data):
    return lambda cmd: bot.handle_command(cmd, data['channel'][0], data['userid'], data['username'])


@pytest.fixture(scope='module')
def bot():
    from slackru.slackbot import SlackBot
    bot = SlackBot()
    Thread(target=bot.run).start()

    yield bot

    bot.stop()
