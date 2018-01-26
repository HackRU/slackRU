""" Configuration Classes

NOTE: The configuration class variables in all caps represent builtin Flask
      configuration values
"""

import os
import logging


class Config:
    botID = "U86U670N8"

    @classmethod
    def setup(cls):
        db_dir = os.path.dirname(cls.dbpath)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)

        logLevel = {True: logging.DEBUG,
                    False: logging.INFO}[cls.DEBUG]
        logging.basicConfig(level=logLevel,
                            format='%(asctime)s [%(levelname)s]: %(message)s',
                            datefmt='(%m/%d/%Y %H:%M:%S)')


class DevelopmentConfig(Config):
    DEBUG = True
    serverurl = 'http://127.0.0.1:5000/'
    dbpath = 'var/slackru-dev.db'


class TestConfig(DevelopmentConfig): pass


class ProductionConfig(Config):
    DEBUG = False
    serverurl = "http://slackru.pythonanywhere.com/"
    dbpath = "/home/slackru/SlackRU/var/slackru.db"


config = {'development': DevelopmentConfig,
          'production': ProductionConfig,
          'testing': TestConfig}[os.environ['SLACK_CONFIG']]

# This should run once--when this module is first imported
config.setup()
