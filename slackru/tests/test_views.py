import json

import pytest

import slackru.util as util


#####################
#  Interface Tests  #
#####################

@pytest.mark.parametrize('value, callback', zip(["yes", "no", "yes"],
                                                ["mentorResponse_1", "mentorResponse_1", "INVALID"]))
def test_message_action(inserts, client, getPostData, value, callback):
    """ message_action Interface Test """
    from slackru.config import config
    postData = getPostData(value, callback)
    resp = client.post(config.serverurl + 'message_action', data=postData)
    assert 200 == resp.status_code


################
#  Unit Tests  #
################


def test_mentorAccept(MAV, data, client, messageData, inserts):
    MAV.mentorAccept()
    resp = util.slack.deleteDirectMessages(messageData[0][0], messageData[0][1])
    assert resp['ok'] is True

    with pytest.raises(util.slack.SlackError) as e:
        util.slack.deleteDirectMessages(messageData[1][0], messageData[1][1])

    assert e.value.args[0] == 'message_not_found'


def test_mentorDecline(MAV, client, messageData):
    MAV.payLoad['message_ts'] = messageData[0][1]
    MAV.mentorDecline()
    MAV.t.join()
    with pytest.raises(IndexError):
        exc_type, exc_obj, exc_trace = MAV.thread_exceptions[0]

    with pytest.raises(util.slack.SlackError) as e:
        util.slack.deleteDirectMessages(messageData[0][0], messageData[0][1])

    assert e.value.args[0] == 'message_not_found'


##############
#  Fixtures  #
##############


@pytest.fixture(name='MAV')
def MessageActionViewInstance(getPostData):
    from slackru.views import MessageActionView
    payload = getPostData("yes", "mentorResponse_1")
    return MessageActionView(payload)


@pytest.fixture
def getPostData(data):
    def payloadFactory(value, callback):
        payload = {"actions": [{"name": "answer",
                                "value": value,
                                "type": "button"}],
                   "callback_id": callback,
                   "user": {'id': data['mentorid'][0],
                            'name': data['mentorname'][0]},
                   'message_ts': '111111111111',
                   'channel': {'id': data['channel'][0],
                               'name': 'general'}}

        return {'payload': json.dumps(payload)}

    return payloadFactory


@pytest.fixture
def inserts(db, data):
    db.drop_table('questions')
    db.create_questions()
    db.insertQuestion(data['question'][0], data['username'], data['userid'], json.dumps([data['userid']]))


@pytest.fixture
def messageData(db, data):
    Mdata = []
    db.drop_table('posts')
    db.create_posts()
    for mentorid in data['mentorid']:
        channel = util.slack.openConversation(mentorid)['channel']['id']
        ts = util.slack.sendMessage(channel, "Test Message")['ts']

        db.insertPost(1, mentorid, channel, ts)

        Mdata.append((channel, ts))

    return Mdata
