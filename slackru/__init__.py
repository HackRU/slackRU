from flask import Flask, Blueprint

from slackru.DB import DB

main = Blueprint('main', __name__)


def create_app() -> 'Flask(...)':
    """ Initialize Flask App """
    from slackru.config import config

    app = Flask(__name__)
    app.config.from_object(config)
    app.register_blueprint(main)

    return app


def get_db() -> DB:
    """ Return a new database connection if one does not already exist.
    Otherwise return the already opened database.
    """
    from slackru.config import config
    if not get_db.database:
        get_db.database = DB(config.dbpath)
    return get_db.database


get_db.database = None

import slackru.views
