import flask
import json
import time
import slackru.util as util
from threading import Thread
from slackru import main
from flask import current_app as app


@main.route("/pairmentor", methods=['POST'])
def pairMentor():
    """ Route that client sends the question to """

    postData = flask.request.form.to_dict()
    db = app.db.get_db()
    db.reconnect()

    def matchMentors():
        query = "SELECT mentors.* FROM shifts " \
                "JOIN mentors ON mentors.userid = shifts.userid " \
                "WHERE datetime('now', 'localtime') >= datetime(shifts.start) " \
                "AND datetime('now', 'localtime') < datetime(shifts.end)"

        matched = []
        query_results = db.query_db(query)
        for mentor in query_results:
            keywords = [word.lower() for word in mentor['keywords'].split(',')]
            for word in postData['question'].split():
                if word.lower() in keywords:
                    matched.append(mentor['userid'])
                    break

        if matched == []:
            for mentor in query_results:
                matched.append(mentor['userid'])

        questionId = db.insertQuestion(postData['question'],
                                postData['username'],
                                postData['userid'],
                                json.dumps(matched))

        return (questionId, matched)

    questionId, matched = matchMentors()

    fmt = "*A HACKER NEEDS YOUR HELP!!!*\n" \
          "<@{0}> has requested to be assisted by a mentor.\n" \
          "They provided the following statement:\n" \
          ">_\"{1}\"_\nCan you help this hacker?\n"

    text = fmt.format(postData['userid'], postData['question'])

    attachments = [{'text': '',
                    'attachment_type': 'default',
                    'callback_id': 'mentorResponse_{0:d}'.format(questionId),
                    'actions': [{'name': 'answer',
                                 'text': 'Yes',
                                 'type': 'button',
                                 'value': 'yes'},
                                {'name': 'answer',
                                 'text': 'No',
                                 'type': 'button',
                                 'value': 'no'}]}]

    for userid in matched:
        channel = util.getDirectMessageChannel(userid)
        timestamp = util.sendMessage(channel, text, attachments)
        db.insertPost(questionId, userid, channel, timestamp)

    return flask.jsonify(matched)


@main.route("/message_action", methods=['POST'])
def message_action():
    """ Slack Action Request URL """

    payload = flask.request.form.to_dict()['payload']
    postData = json.loads(payload)

    db = app.db.get_db()
    db.reconnect()

    if 'mentorResponse' in postData['callback_id']:
        answer = postData['actions'][0]['value']
        mentorid = postData['user']['id']
        questionId = postData['callback_id'].split('_')[1]

        def mentorAccept():
            db.mentorAccept(mentorid, questionId)
            query = "SELECT channel,timestamp FROM posts " \
                    "WHERE questionId=? AND userid!=?"
            for post in db.query_db(query, [questionId, mentorid]):
                util.deleteDirectMessages(post['channel'], post['timestamp'])

            hackerid, question = db.query_db('SELECT userid,question FROM questions WHERE id=?',
                                             [questionId],
                                             one=True).values()

            resp = {'text': 'That\'s the spirit! Connecting you to <@{0}>...'.format(hackerid)}

            def startGroupMessage():
                time.sleep(3)
                channel = util.getDirectMessageChannel(hackerid + ',' + mentorid)
                fmt = "Hello <@{0}>. Your request for a mentor with regards to the following question has been processed:\n" \
                      ">{2}\n" \
                      "You have been matched with <@{1}>. Take it away <@{1}>! :grinning:"
                util.sendMessage(channel, fmt.format(hackerid, mentorid, question))

            Thread(target=startGroupMessage).start()
            return flask.jsonify(resp)

        def mentorDecline():
            resp = {'text': 'No problem! Thanks for responding anyway! :grinning:'}

            def delayedDeleteMessage():
                time.sleep(3)
                util.deleteDirectMessages(postData['channel']['id'], postData['message_ts'])

            Thread(target=delayedDeleteMessage).start()
            return flask.jsonify(resp)

        return {'yes': mentorAccept,
                'no': mentorDecline}[answer]()
