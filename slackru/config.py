""" Configuration Classes

NOTE: The configuration class variables in all caps represent builtin Flask
      configuration values
"""

import os
import logging


class Config:
    """ Base Configuration Class """
    botID = "U86U670N8"
    TESTING = False

    @classmethod
    def setup(cls):
        db_dir = os.path.dirname(cls.dbpath)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)

        logLevel = {True: logging.DEBUG,
                    False: logging.ERROR}[cls.DEBUG]
        logging.basicConfig(level=logLevel,
                            format='%(asctime)s [%(levelname)s]: %(message)s',
                            datefmt='(%m/%d/%Y %H:%M:%S)')


class DevelopmentConfig(Config):
    """ Development Configuration Class """
    DEBUG = True
    slack_api_key = os.environ['TEST_SLACK_API_KEY']
    serverurl = 'http://127.0.0.1:5000/'
    dbpath = 'var/slackru-dev.db'


class TestingConfig(DevelopmentConfig):
    """ Configuration Class used for Tests """
    TESTING = True
    DEBUG = False


class ProductionConfig(Config):
    """ Production Configuration Class """
    DEBUG = False
    botID = "U9DFNJMHR"
    slack_api_key = os.environ['SLACK_API_KEY']
    serverurl = "http://slackru.bkdhwfwsv2.us-east-1.elasticbeanstalk.com/"
    dbpath = "var/slackru.db"


config = {'development': DevelopmentConfig,
          'testing': TestingConfig,
          'production': ProductionConfig}[os.environ['SLACK_CONFIG']]

# This should run once--when this module is first imported
config.setup()
