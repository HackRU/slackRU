""" Flask View (URL Route) Definitions """

import sys
import json
import time
from threading import Thread

import flask
from flask.views import View

import slackru.util as util
from slackru import main, get_db
import slackru.messages as M


class PostView(View):
    """ Base Class for POST URL Route Classes """
    methods = ['POST']

    def __init__(self, postData=None):
        self.db = get_db()

        if postData:
            self.postData = postData
        else:
            self.postData = flask.request.form.to_dict()


class MessageActionView(PostView):
    """ 'message_action' URL route

    POST requests are sent from Slack to https://<slackru-site>/message_action
    in response to an interactive button press in Slack (e.g. a mentor pressed
    either the 'Accept' button or 'Decline' button).

    More on Slack's "Interactive Message Buttons": https://api.slack.com/docs/message-buttons
    """
    def __init__(self, postData=None):
        super().__init__(postData)

        self.threads = {}
        self.thread_exceptions = {}

        self.payLoad = json.loads(self.postData['payload'])

        if 'mentorResponse' in self.payLoad['callback_id']:
            self.answer = self.payLoad['actions'][0]['value']
            self.mentorid = self.payLoad['user']['id']
            self.questionId = self.payLoad['callback_id'].split('_')[1]

            # Sets View Function
            self.dispatch_request = self.DR_mentorResponse
        else:
            self.dispatch_request = lambda: "done"

    def DR_mentorResponse(self) -> 'flask.Response(...)':
        """ Slack Action Request URL

        Return value is sent to Slack and will replace old Slack message
        """
        return {'yes': self.mentorAccept,
                'no': self.mentorDecline}[self.answer]()

    def mentorAccept(self) -> 'flask.Reponse(...)':
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
            util.ifNotTestingThen(time.sleep, 3)
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

    def mentorDecline(self) -> 'flask.Reponse(...)':
        """ If mentor presses 'Decline':

        - Respond to him/her (replace previous message)
        - Delete reponse after sleep period (reduces clutter)
        """
        resp = {'text': 'No problem! Thanks for responding anyway! :grinning:'}

        def delayedDeleteMessage():
            """ After a delay, delete the Slack message corresponding to this
            button press """
            try:
                util.ifNotTestingThen(time.sleep, 3)
                util.slack.deleteDirectMessages(self.payLoad['channel']['id'], self.payLoad['message_ts'])
            except Exception:
                self.thread_exceptions['decline'] = sys.exc_info()

        t = Thread(target=delayedDeleteMessage)
        self.threads['decline'] = t
        t.start()

        return flask.jsonify(resp)


class PairMentor(PostView):
    """ 'pair_mentor' Flask URL Route

    The SlackBot sends a POST request to this route to request that a hacker be paired
    with a mentor. The SQL database is needed to handle this, which is why the SlackBot
    cannot handle this functionality locally.
    """
    def __init__(self):
        super().__init__()

        self.question = self.postData['question']
        self.userid = self.postData['userid']

    def dispatch_request(self) -> 'flask.Response(...)':
        """ The URL route is linked to this method """
        mentorsQuery = ("SELECT mentors.* FROM shifts "
                        "JOIN mentors ON mentors.userid = shifts.userid "
                        "WHERE datetime('now', 'localtime') >= datetime(shifts.start) "
                        "AND datetime('now', 'localtime') < datetime(shifts.end)")

        mentorsOnDuty = self.db.runQuery(mentorsQuery)
        selectedMentorIDs = list(self._getMatchedMentorIDs(self.question, mentorsOnDuty)) \
                             or [mentor['userid'] for mentor in mentorsOnDuty]

        questionId = self.db.insertQuestion(self.question,
                                           self.userid,
                                           json.dumps(selectedMentorIDs))

        attachments = M.mentors_attachments(questionId)
        text = M.mentors_text(self.userid, self.question)
        for mentorid in selectedMentorIDs:
            channel = util.slack.getDirectMessageChannel(mentorid)
            timestamp = util.slack.sendMessage(channel, text, attachments)
            self.db.insertPost(questionId, mentorid, channel, timestamp)

        return ("done", {'mentorIDs': selectedMentorIDs})

    def _getMatchedMentorIDs(self, question: 'str', mentorsOnDuty: '[{str: ??}]'):
        """ Matches Mentors based on 'question' and what mentors currently have shifts scheduled """
        import string

        translator = question.maketrans(dict.fromkeys(string.punctuation))

        temp = question.translate(translator)
        temp = [word.lower() for word in temp.split()]

        question_keywords = temp

        for mentor in mentorsOnDuty:
            keywords = [word.lower() for word in mentor['keywords'].split(',')]
            for word in question_keywords:
                if word in keywords:
                    yield mentor['userid']
                    break


class RegisterMentor(PostView):
    def __init__(self):
        super().__init__()

    def dispatch_request(self):
        self.db.insertMentor(**self.postData)

        channel = util.slack.getDirectMessageChannel(self.postData['userid'])
        util.slack.sendMessage(channel, M.register_success(**self.postData))

        return "done"


# These are equivalent to the '@main.route' function decorators
main.add_url_rule('/message_action', view_func=MessageActionView.as_view('message_action'))
main.add_url_rule('/pair_mentor', view_func=PairMentor.as_view('pair_mentor'))
main.add_url_rule('/register_mentor', view_func=RegisterMentor.as_view('register_mentor'))
