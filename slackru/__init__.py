from flask import Flask
from flask import Blueprint

from slackru.DB import DB

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


import slackru.views
