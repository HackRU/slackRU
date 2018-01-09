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


def test_mentorAccept(MAV, client, messageMentors, inserts):
    resp = MAV.mentorAccept()
    assert resp.get('delete_count') == 1


def test_mentorDecline(MAV, client, messageMentors, inserts):
    MAV.mentorDecline()


##############
#  Fixtures  #
##############


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
                   'channel': {'id': 'D86QQ6P2P',
                               'name': 'general'}}

        return {'payload': json.dumps(payload)}

    return payloadFactory


@pytest.fixture
def inserts(db, data):
    db.drop_table('questions')
    db.create_questions()
    db.insertQuestion(data['question'][0], data['username'], data['userid'], json.dumps([data['userid']]))


@pytest.fixture
def messageMentors(data, db):
    for mentorid in data['mentorid']:
        channel = util.slack.getDirectMessageChannel(mentorid)
        timestamp = util.slack.sendMessage(channel, "Test Message")['ts']
        db.insertPost(1, mentorid, channel, timestamp)


@pytest.fixture(name='MAV')
def MessageActionViewInstance(getPostData):
    from slackru.views import MessageActionView
    payload = getPostData("yes", "mentorResponse_1")
    return MessageActionView(payload)
