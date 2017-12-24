from slackru.DB import DB
from flask import Flask
from flask import Blueprint

main = Blueprint('main', __name__)


def create_app(config):
    app = Flask(__name__)
    app.debug = config.debug
    app.register_blueprint(main)
    app.db = DB(config.dbpath)  # Initializes Database

    return app


import slackru.views
