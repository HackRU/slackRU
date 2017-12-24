import flask
from slackru import main


@main.route("/pairmentor", methods=['POST'])
def pairMentor():
    """ Route that client sends the question to """
    from flask import current_app as app
    postData = flask.request.form.to_dict()
    data = postData['data']
    user = postData['user']
    userid = postData['userid']
    return flask.jsonify(postData)
