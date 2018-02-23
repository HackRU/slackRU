from flask import Flask, Blueprint
from flask_sqlalchemy import SQLAlchemy

main = Blueprint('main', __name__)

sqlalch_db = None
db = None


def create_app() -> 'Flask(...)':
    """ Initialize Flask App """
    from slackru.config import config

    app = Flask(__name__)
    app.config.from_object(config)
    app.register_blueprint(main)

    global sqlalch_db, db
    sqlalch_db = SQLAlchemy(app)

    from slackru.DB import DB
    db = DB()

    return app


def get_db() -> 'DB(...)':
    return db


import slackru.views
