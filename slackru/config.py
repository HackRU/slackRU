class TestConfig:
    debug = True
    botID = "U86U670N8"
    dbpath = 'var/mentors-test.db'
    serverurl = 'http://127.0.0.1:5000/'


class DevelopmentConfig(TestConfig):
    dbpath = 'var/mentors-dev.db'


class ProductionConfig:
    debug = False
    botID = ""
    dbpath = "var/mentors.db"
    serverurl = ""


getConfig = {'development': DevelopmentConfig,
             'testing': TestConfig,
             'production': ProductionConfig}
