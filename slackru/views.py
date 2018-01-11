""" Flask View (URL Route) Definitions """

import sys
import json
import time
from threading import Thread

import flask
from flask.views import View

import slackru.util as util
from slackru import main, get_db


class MessageActionView(View):
    methods = ['POST']

    def __init__(self, postData=None):
        self.db = get_db()
        self.threads = {}
        self.thread_exceptions = {}

        if postData:
            self.postData = postData
        else:
            self.postData = flask.request.form.to_dict()

        self.payLoad = json.loads(self.postData['payload'])

        if 'mentorResponse' in self.payLoad['callback_id']:
            self.answer = self.payLoad['actions'][0]['value']
            self.mentorid = self.payLoad['user']['id']
            self.questionId = self.payLoad['callback_id'].split('_')[1]

            # Sets View Function
            self.dispatch_request = self.DR_mentorResponse
        else:
            self.dispatch_request = lambda: "done"

    def DR_mentorResponse(self):
        """ Slack Action Request URL """
        return {'yes': self.mentorAccept,
                'no': self.mentorDecline}[self.answer]()

    def mentorAccept(self):
        self.db.markAnswered(self.mentorid, self.questionId)
        query = "SELECT channel,timestamp FROM posts " \
                "WHERE questionId=? AND userid!=?"

        delete_count = 0
        for post in self.db.runQuery(query, [self.questionId, self.mentorid]):
            delete_count += 1
            util.slack.deleteDirectMessages(post['channel'], post['timestamp'])

        query_result = self.db.runQuery('SELECT userid,question FROM questions WHERE id=?',
                                         [self.questionId],
                                         one=True)

        assert query_result, "No question matches the given question ID!"

        hackerid, question = query_result.values()

        resp = {'text': 'That\'s the spirit! I have setup a direct message between you and <@{0}>. Please reach out to <@{0}> and let them know you are taking ownership of this request. Thanks! :grinning:'.format(hackerid)}

        def startGroupMessage():
            util.ifNotDebugThen(time.sleep, 3)
            channel = util.slack.getDirectMessageChannel(hackerid + ',' + self.mentorid)
            fmt = ("Hello <@{0}>. Your request for a mentor has been processed. "
                    "You have been matched with <@{1}>.\n\n"
                    "The following question/comment is associated with this request:\n>_\"{2}\"_\n"
                    "Take it away <@{1}>! :grinning:")
            util.slack.sendMessage(channel, fmt.format(hackerid, self.mentorid, question))

        t = Thread(target=startGroupMessage)
        self.threads['accept'] = t
        t.start()

        return flask.jsonify(resp)

    def mentorDecline(self):
        resp = {'text': 'No problem! Thanks for responding anyway! :grinning:'}

        def delayedDeleteMessage():
            try:
                util.ifNotDebugThen(time.sleep, 3)
                util.slack.deleteDirectMessages(self.payLoad['channel']['id'], self.payLoad['message_ts'])
            except Exception:
                self.thread_exceptions['decline'] = sys.exc_info()

        t = Thread(target=delayedDeleteMessage)
        self.threads['decline'] = t
        t.start()

        return flask.jsonify(resp)


# These are equivalent to the '@main.route' function decorators
main.add_url_rule('/message_action', view_func=MessageActionView.as_view('message_action'))
