import flask
import json
import time
import slackru.util as util
from threading import Thread
from slackru import main, ifNotDebug
from flask import current_app as app
from flask.views import View


class PairMentorView(View):
    methods = ['POST']

    def __init__(self):
        self.postData = flask.request.form.to_dict()
        self.db = app.db.open()

    def matchMentors(self):
        query = "SELECT mentors.* FROM shifts " \
                "JOIN mentors ON mentors.userid = shifts.userid " \
                "WHERE datetime('now', 'localtime') >= datetime(shifts.start) " \
                "AND datetime('now', 'localtime') < datetime(shifts.end)"

        matched = []
        query_results = self.db.runQuery(query)
        for mentor in query_results:
            keywords = [word.lower() for word in mentor['keywords'].split(',')]
            for word in self.postData['question'].split():
                if word.lower() in keywords:
                    matched.append(mentor['userid'])
                    break

        if matched == []:
            for mentor in query_results:
                matched.append(mentor['userid'])

        questionId = self.db.insertQuestion(self.postData['question'],
                                self.postData['username'],
                                self.postData['userid'],
                                json.dumps(matched))

        return (questionId, matched)

    def dispatch_request(self):
        """ Route that client sends the question to """

        questionId, matched = self.matchMentors()

        fmt = "*A HACKER NEEDS YOUR HELP!!!*\n" \
              "<@{0}> has requested to be assisted by a mentor.\n" \
              "They provided the following statement:\n" \
              ">_\"{1}\"_\nCan you help this hacker?\n"

        text = fmt.format(self.postData['userid'], self.postData['question'])

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
            self.db.insertPost(questionId, userid, channel, timestamp)

        return "done"


class MessageActionView(View):
    methods = ['POST']

    def __init__(self):
        self.db = app.db.open()

        payload = flask.request.form.to_dict()['payload']
        self.postData = json.loads(payload)

        if 'mentorResponse' in self.postData['callback_id']:
            self.answer = self.postData['actions'][0]['value']
            self.mentorid = self.postData['user']['id']
            self.questionId = self.postData['callback_id'].split('_')[1]

            # Sets View Function
            self.dispatch_request = self.DR_mentorResponse
        else:
            self.dispatch_request = lambda: "done"

    def mentorAccept(self):
        self.db.markAnswered(self.mentorid, self.questionId)
        query = "SELECT channel,timestamp FROM posts " \
                "WHERE questionId=? AND userid!=?"
        for post in self.db.runQuery(query, [self.questionId, self.mentorid]):
            util.deleteDirectMessages(post['channel'], post['timestamp'])

        hackerid, question = self.db.runQuery('SELECT userid,question FROM questions WHERE id=?',
                                         [self.questionId],
                                         one=True).values()

        resp = {'text': 'That\'s the spirit! Connecting you to <@{0}>...'.format(hackerid)}

        def startGroupMessage():
            ifNotDebug(time.sleep, 3)
            channel = util.getDirectMessageChannel(hackerid + ',' + self.mentorid)
            fmt = "Hello <@{0}>. Your request for a mentor with regards to the following question has been processed:\n" \
                  ">{2}\n" \
                  "You have been matched with <@{1}>. Take it away <@{1}>! :grinning:"
            util.sendMessage(channel, fmt.format(hackerid, self.mentorid, question))

        Thread(target=startGroupMessage).start()
        return flask.jsonify(resp)

    def mentorDecline(self):
        resp = {'text': 'No problem! Thanks for responding anyway! :grinning:'}

        def delayedDeleteMessage():
            ifNotDebug(time.sleep, 3)
            util.deleteDirectMessages(self.postData['channel']['id'], self.postData['message_ts'])

        Thread(target=delayedDeleteMessage).start()
        return flask.jsonify(resp)

    def DR_mentorResponse(self):
        """ Slack Action Request URL """
        return {'yes': self.mentorAccept,
                'no': self.mentorDecline}[self.answer]()


# These are equivalent to the '@main.route' function decorators
main.add_url_rule('/pairmentor', view_func=PairMentorView.as_view('pairMentor'))
main.add_url_rule('/message_action', view_func=MessageActionView.as_view('message_action'))
