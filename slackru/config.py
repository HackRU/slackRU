""" Configuration Classes

NOTE: The configuration class variables in all caps represent builtin Flask
      configuration values
"""

import os


class Config:
    botID = "U86U670N8"

    @classmethod
    def setup(cls):
        db_dir = os.path.dirname(cls.dbpath)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)


class DevelopmentConfig(Config):
    DEBUG = True
    serverurl = 'http://127.0.0.1:5000/'
    dbpath = 'var/slackbot-dev.db'


class ProductionConfig(Config):
    DEBUG = False
    serverurl = "http://slackru.pythonanywhere.com/"
    dbpath = "/home/slackru/SlackRU/var/slackbot.db"


config = {'development': DevelopmentConfig,
          'production': ProductionConfig}[os.environ['SLACK_CONFIG']]
