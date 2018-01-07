import json

import pytest


pyQuestion = "I am having some trouble with Python. Something is not working right."


@pytest.fixture
def inserts(db, data):
    db.drop_table('questions')
    db.create_questions()
    db.insertQuestion(pyQuestion, data.username, data.userid, json.dumps([data.userid]))


@pytest.mark.parametrize('question', [pyQuestion, "What is 2+2?"])
def test_pairMentor(data, inserts, client, question):
    from slackru.config import config
    postData = {'question': question,
                'username': data.username,
                'userid': data.userid}

    resp = client.post(config.serverurl + 'pairmentor', data=postData)
    assert 200 == resp.status_code


@pytest.mark.parametrize('value, callback', zip(["yes", "no", "yes"],
                                                ["mentorResponse_1", "mentorResponse_1", "INVALID"]))
def test_message_action(data, inserts, client, value, callback):
    from slackru.config import config
    payload = {"actions": [{"name": "answer",
                            "value": value,
                            "type": "button"}],
               "callback_id": callback,
               "user": {'id': data.mentorid,
                        'name': data.mentorname},
               'message_ts': '111111111111',
               'channel': {'id': 'D86QQ6P2P',
                           'name': 'general'}}
    postData = {'payload': json.dumps(payload)}
    resp = client.post(config.serverurl + 'message_action', data=postData)
    assert 200 == resp.status_code
