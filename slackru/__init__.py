from flask import Flask, Blueprint, g

from slackru.DB import DB

main = Blueprint('main', __name__)


def create_app():
    from slackru.config import config
    config.setup()

    app = Flask(__name__)
    app.config.from_object(config)
    app.register_blueprint(main)

    return app


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    from slackru.config import config
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = DB(config.dbpath)
    return g.sqlite_db


import slackru.views
