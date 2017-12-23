import sqlite3
import os


class Base:
    """ Initializes Database """
    def __init__(self, dbpath):
        if not os.path.isfile(dbpath):
            tablesExist = False
        else:
            tablesExist = True

        self.conn = sqlite3.connect(dbpath)
        self.c = self.conn.cursor()

        if not tablesExist:
            self.initMentors()
            self.initShifts()
            self.initActiveQuestions()

    def initMentors(self):
        self.c.execute("CREATE TABLE mentors "
                       "(name VARCHAR(255), "
                       "keywords VARCHAR(1000), "
                       "phone VARCHAR(1000) PRIMARY KEY);")
        self.conn.commit()

    def initShifts(self):
        self.c.execute("CREATE TABLE shifts "
                       "(phoneno VARCHAR(300), "
                       "fromtime TEXT, "
                       "totime TEXT, "
                       "FOREIGN KEY(phoneno) REFERENCES mentors(phone));")
        self.conn.commit()

    def initActiveQuestions(self):
        self.c.execute("CREATE TABLE activequestions "
                       "(id INTEGER PRIMARY KEY, "
                       "answered INTEGER, "
                       "username INTEGER, "
                       "userid INTEGER, "
                       "timestamp INTEGER, "
                       "phones BLOB, "
                       "peoplewhoans BLOB, "
                       "assignedmentor VARCHAR(255));")
        self.conn.commit()


class DB(Base):
    def __init__(self, dbpath):
        Base.__init__(self, dbpath)
