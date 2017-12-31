import flask
import sqlite3
import urllib
import slackru.util as util
from slackru import main
from flask import current_app as app
from slackru.serverside import askQuestion, answerQuestion


@main.route("/pairmentor", methods=['POST'])
def pairMentor():
    """ Route that client sends the question to """

    postData = flask.request.form.to_dict()
    db = app.db.get_db()

    try:
        questionId, matchedMentors = askQuestion(db, **postData)
    except sqlite3.ProgrammingError as e:
        db.reconnect()
        questionId, matchedMentors = askQuestion(db, **postData)

    fmt = "*A HACKER NEEDS YOUR HELP!!!*\n" \
          "<@{0}> has requested to be assisted by a mentor.\n" \
          "They provided the following statement:\n" \
          ">_\"{1}\"_\nCan you help this hacker?\n"

    text = fmt.format(postData['userid'], postData['question'])

    attachments = [{
        'text': '',
        'attachment_type': 'default',
        'callback_id': 'pairMentor',
        'actions': [
            {
                'name': 'answer',
                'text': 'Yes',
                'type': 'button',
                'value': 'yes'
                },
            {
                'name': 'answer',
                'text': 'No',
                'type': 'button',
                'value': 'no'
                }]
            }]

    for userid in matchedMentors:
        channel = util.getDirectMessageChannel(userid)
        timestamp = util.message(channel, text, attachments)
        db.insertPost(questionId, userid, channel, timestamp)

    return flask.jsonify(matchedMentors)


@main.route("/answer/<userid>/<questionId>")
def answer(userid, questionId):
    answerQuestion(app.db.get_db(), userid, int(questionId))
    return "done"


@main.route("/message_action", methods=['POST'])
def message_action():
    """ Slack Action Request URL """

    postData = flask.request.form.to_dict()
    return flask.jsonify(postData)
