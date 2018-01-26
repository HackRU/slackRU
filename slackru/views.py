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
    """ 'message_action' URL route

    POST requests are sent from Slack to https://<slackru-site>/message_action
    in response to an interactive button press in Slack (e.g. a mentor pressed
    either the 'Accept' button or 'Decline' button).

    More on Slack's "Interactive Message Buttons": https://api.slack.com/docs/message-buttons
    """
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
        """ Slack Action Request URL

        Return value is sent to Slack and will replace old Slack message
        """
        return {'yes': self.mentorAccept,
                'no': self.mentorDecline}[self.answer]()

    def mentorAccept(self):
        """ If mentor presses 'Accept':

        - Respond to him/her (replace previous message)
        - Setup group message channel with bot, hacker, and mentor
        - Delete all other Slack messages sent to mentors regarding this question
          from this hacker
        """
        self.db.markAnswered(self.mentorid, self.questionId)
        query = "SELECT channel,timestamp FROM posts " \
                "WHERE questionId=? AND userid!=?"

        for post in self.db.runQuery(query, [self.questionId, self.mentorid]):
            util.slack.deleteDirectMessages(post['channel'], post['timestamp'])

        query_result = self.db.runQuery('SELECT userid,question FROM questions WHERE id=?',
                                         [self.questionId],
                                         one=True)

        assert query_result, "No question matches the given question ID!"

        hackerid, question = query_result.values()

        resp = {'text': 'That\'s the spirit! I have setup a direct message between you and <@{0}>. Please reach out to <@{0}> and let them know you are taking ownership of this request. Thanks! :grinning:'.format(hackerid)}

        def startGroupMessage():
            """ Starts Group Message with hacker and mentor """
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
        """ If mentor presses 'Decline':

        - Respond to him/her (replace previous message)
        - Delete reponse after sleep period (reduces clutter)
        """
        resp = {'text': 'No problem! Thanks for responding anyway! :grinning:'}

        def delayedDeleteMessage():
            """ After a delay, delete the Slack message corresponding to this
            button press """
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
