from slackru import main
from flask import request


@main.route("/pairmentor", methods=['POST'])
def pairMentor():
    """
        Route that client sends the question to
    """
    from flask import current_app as app
    postData = request.form.to_dict()
    data = postData['data']
    user = postData['user']
    userid = postData['userid']
    return postData
