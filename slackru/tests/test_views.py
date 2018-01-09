import json

import pytest


@pytest.mark.parametrize('value, callback', zip(["yes", "no", "yes"],
                                                ["mentorResponse_1", "mentorResponse_1", "INVALID"]))
def test_message_action(data, inserts, client, value, callback):
    """ message_action Interface Test """
    from slackru.config import config
    payload = {"actions": [{"name": "answer",
                            "value": value,
                            "type": "button"}],
               "callback_id": callback,
               "user": {'id': data['mentorid'][0],
                        'name': data['mentorname'][0]},
               'message_ts': '111111111111',
               'channel': {'id': 'D86QQ6P2P',
                           'name': 'general'}}
    postData = {'payload': json.dumps(payload)}
    resp = client.post(config.serverurl + 'message_action', data=postData)
    assert 200 == resp.status_code


@pytest.fixture
def inserts(db, data):
    db.drop_table('questions')
    db.create_questions()
    db.insertQuestion(data['question'][0], data['username'], data['userid'], json.dumps([data['userid']]))
