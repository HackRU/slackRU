import requests

import slackru.util as util
import slackru.messages as M
from slackru.config import config


class Commands:
    """ SlackBot Commands

    ========== Help Documentation ==========
    READ THIS BEFORE MAKING CHANGES TO THIS CLASS!

    The method docstrings of this class are used to feed the 'help' command.
    This means that if you make any changes to the methods in this class, you
    MUST update the docstrings accordingly. Try to keep any new docstrings as
    consistent with the current method docstrings as possible.

    ----- Format Variables -----
    The 'help' command uses format variables to generalize the docstrings as
    much as possible. Use the following format variables in the method
    docstrings wherever applicable:

    {name}:   The name of the method (which should be the same as the name of the
              command!).

    {precmd}: The sentinal value that the SlackBot searches for. Right now it
              is '@<BotName> ', but it may change in the future. This variable
              should be used in each command's usage description.

    {argbar}: The title bar used before the description of the command's
              arguments.

    ----- Protected Commands -----
    Not all commands should be displayed in the general purpose 'help' message.
    The 'register' command, for example, registers a mentor with the SlackBot.
    So hackers should not be aware of this command. "Protected" commands should
    be represented by "protected" methods. In Python, you can declare a method
    to be protected by starting the method name with a SINGLE underscore.  The
    'help' command will display the documentation of protected methods ONLY
    when it is explicitly requested to do so (e.g. 'help register' will display
    the 'register' command's documentation).
    """
    @classmethod
    def help(cls, userid: str, command: str=None, error=False):
        """ Use the `{name}` command to display my documentation.

        usage:
            `{precmd}{name}`
            `{precmd}{name} <command>`
            `{precmd}<command> -h`

        {argbar}
        `<command>`: one of my available commands (e.g. `mentors` or `help`)
        """
        ARGBAR = '_***** Parameter Details *****_'

        def appendDoc(docs: str, name: str, obj: '<method>') -> str:
            if obj.__doc__:
                docstr = obj.__doc__.lstrip()
            else:
                return docs

            titled_docstr = '\n\n*========== ' + name.upper() + ' ==========*\n' + docstr
            new_doc = docs + titled_docstr.format(name=name, precmd='@hackbot ', argbar=ARGBAR)
            return new_doc

        channel = util.slack.getDirectMessageChannel(userid)

        if command:
            try:
                obj = getattr(cls, command)
            except AttributeError as e:
                obj = getattr(cls, '_' + command)

            doc = appendDoc('', command, obj)
            help_msg = M.help_msg(doc, one=True, error=error)
        else:
            cmd_docs = ''
            for name in cls.__dict__:
                obj = getattr(cls, name)

                if name[0] != '_':
                    cmd_docs = appendDoc(cmd_docs, name, obj)

            help_msg = M.help_msg(cmd_docs, error=error)

        util.slack.sendMessage(channel, help_msg)

    @classmethod
    def mentors(cls, question: str, userid: str) -> int:
        """ Use the `{name}` command to request assistance from a mentor.

        usage:
            `{precmd}{name} <question>`

        {argbar}
        `<question>`: hacker's question

        NOTE: Make sure that your `<question>` is as detailed as possible. I will try my
              best to match you with the mentor best fit to help with your specific problem,
              but I can only work with what you give me.
        """
        util.slack.sendMessage(userid, "Trying to find a mentor")

        if not question:
            return 500

        postData = {'question': question,
                    'userid': userid}

        resp = requests.post(config.serverurl + 'pair_mentor', data=postData)

        return resp.status_code

    @classmethod
    def _register(cls, mentor_data: 'fullname | phone_number | keywords', userid: str, username: str):
        """ Use the `{name}` command to register as a mentor.

        usage:
            `{precmd}{name} <fullname> | <phone_number> | <keywords>`

        {argbar}
        `<fullname>`: The mentor's first and last name, seperated by a space.
        `<phone_number>`: The mentor's phone number. No spaces, dashes, or parentheses (e.g. 5555555555).
        `<keywords>`: These represent skills (programming languages, framewords, etc.) that you feel
                    you are particularly well suited to mentor others in. This should be a comma
                    seperated list (e.g. Python,Java,Haskell)

        NOTE: Regardless of the keywords that you choose, you will potentially be notified of any
              inquiry (question, request for help, etc.) that a hacker makes. You will, however,
              be prioritized when a hacker inquiry matches one of your listed keywords (i.e. the
              SlackBot will attempt to reach out to you before other mentors if the hacker has a
              question that contains one of your keywords).

        NOTE: If you make a mistake/typo, you can always run this command
              again. If you have already registered, I will just overwrite your
              previous records with the new ones that you provide.

        WARNING: You must use '|' to seperate each option! Keywords should be seperated using commas!
                 You must register using this command or you will NOT be notified when hackers reach
                 out for help!
        """
        try:
            fullname, phone_number, keywords = [field.strip() for field in mentor_data.split('|')]
            keywords = keywords.replace(' ', '')
        except ValueError as e:
            return 500

        if not fullname:
            return 501

        postData = {'fullname': fullname,
                    'phone_number': phone_number,
                    'keywords': keywords,
                    'userid': userid,
                    'username': username}

        resp = requests.post(config.serverurl + 'register_mentor', data=postData)
        return resp.status_code
