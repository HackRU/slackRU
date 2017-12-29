import os


class TestConfig:
    debug = True
    dbpath = 'var/mentors-test.db'
    serverurl = 'http://127.0.0.1:5000/'
    botID = "U86U670N8"


class DevelopmentConfig(TestConfig):
    dbpath = 'var/mentors-dev.db'


class ProductionConfig:
    debug = False
    dbpath = "var/mentors.db"
    serverurl = ""
    botID = ""


config = {'development': DevelopmentConfig,
          'testing': TestConfig,
          'production': ProductionConfig}[os.environ['SLACK_CONFIG']]
