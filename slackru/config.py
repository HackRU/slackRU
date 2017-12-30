import os


class Base:
    botID = "U86U670N8"
    debug = True
    serverurl = 'http://127.0.0.1:5000/'

    @classmethod
    def setup(cls):
        db_dir = os.path.dirname(cls.dbpath)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)


class TestConfig(Base):
    dbpath = 'var/mentors-test.db'


class DevelopmentConfig(Base):
    dbpath = 'var/mentors-dev.db'


class ProductionConfig(Base):
    debug = False
    serverurl = "http://slackru.pythonanywhere.com/"
    dbpath = "/home/slackru/SlackRU/var/mentors.db"


config = {'development': DevelopmentConfig,
          'testing': TestConfig,
          'production': ProductionConfig}[os.environ['SLACK_CONFIG']]
