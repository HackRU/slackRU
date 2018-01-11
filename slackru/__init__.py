from flask import Flask, Blueprint

from slackru.DB import DB

main = Blueprint('main', __name__)
slackru_db = None


def create_app():
    from slackru.config import config

    app = Flask(__name__)
    app.config.from_object(config)
    app.register_blueprint(main)

    return app


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    from slackru.config import config
    global slackru_db
    if not slackru_db:
        slackru_db = DB(config.dbpath)
    return slackru_db


import slackru.views
