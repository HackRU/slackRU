from slackru.DB import DB
from flask import Flask
from flask import Blueprint

main = Blueprint('main', __name__)


def create_app():
    from slackru.config import config
    config.setup()

    app = Flask(__name__)
    app.debug = config.debug
    app.register_blueprint(main)
    app.db = DB(config.dbpath)  # Initializes Database
    app.conf = config

    return app


def ifDebug(func, *args, inverted=False, **kwargs):
    """ Higher-Order Debug Function

    Calls function only if debugging is enabled.
    """
    from slackru.config import config
    if config.debug ^ inverted:  # Bitwise XOR operator
        func(*args, **kwargs)


def ifNotDebug(func, *args, **kwargs):
    ifDebug(func, *args, inverted=True, **kwargs)


import slackru.views
