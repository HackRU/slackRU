import flask
import sqlite3
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
          ">_\"{1}\"_\nDo you think you are a good match for this? If so, click " \
          "<{2}answer/{4}/{3}|ACCEPT>."

    message = fmt.format(postData['userid'], postData['question'], app.conf.serverurl, questionId, "{0}")

    for userid in matchedMentors:
        channel = util.getDirectMessageChannel(userid)
        timestamp = util.message(channel, message.format(userid))
        db.insertPost(questionId, userid, channel, timestamp)

    return flask.jsonify(matchedMentors)


@main.route("/answer/<userid>/<questionId>")
def answer(userid, questionId):
    answerQuestion(app.db.get_db(), userid, int(questionId))
    return "done"
