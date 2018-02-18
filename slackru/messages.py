import re


HELP = """
Hello hacker! My name is HackBot!

I currently support the following commands:

{commands}

Remember, I'm here to help! And unless I become self-aware at some point during this
hackathon (keep your fingers crossed!), I'll be here all night! So don't be a stranger!  :robot_face:
"""


def help_msg(cmd_docs, one=False):
    block_docs = re.sub('(^|\n)', '\\1>', cmd_docs.lstrip())

    if one:
        return block_docs

    msg = HELP.lstrip().format(commands=block_docs)
    return msg


def register_success(**kwargs):
    return ("You have successfully registered to be a mentor!:\n"
        ">fullname = {fullname}\n>username = {username}\n>userid = {userid}\n"
        ">phone number = {phone_number}\n>keywords = {keywords}".format(**kwargs))


def mentors_attachments(questionId):
    return [{'text': '',
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


def mentors_text(userid, question):
    textFmt = ("*A HACKER NEEDS YOUR HELP!!!*\n"
            "<@{0}> has requested to be assisted by a mentor.\n"
            "They provided the following statement:\n"
            ">_\"{1}\"_\nCan you help this hacker?\n")

    return textFmt.format(userid, question)
