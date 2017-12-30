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

    message = "{0} has requested to be assisted by a mentor. " \
              "Can you answer this question?\n>_\"{1}\"_\n" \
              "<{2}answer/{4}/1/{3}|ACCEPT> " \
              "or <{2}answer/{4}/0/{3}|DECLINE>".format(postData['username'],
                                                        postData['question'],
                                                        app.conf.serverurl,
                                                        questionId,
                                                        "{0}")

    for userid in matchedMentors:
        channel = util.getDirectMessageChannel(userid)
        util.message(channel, message.format(userid))

    return flask.jsonify(matchedMentors)


@main.route("/answer/<userid>/<accept>/<questionId>")
def answer(userid, accept, questionId):
    answerQuestion(app.db.get_db(), userid, int(questionId), accept=accept)
    return "done"
