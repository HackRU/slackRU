import sqlite3


class Base:
    def __init__(self, dbpath):
        self.dbpath = dbpath
        self.conn = None
        self.c = None

        self.reconnect = self.open

    def get_db(self):
        if not self.conn:
            self.open()
        return self

    def open(self):
        self.conn = sqlite3.connect(self.dbpath)

        def make_dicts(cursor, row):
            return dict((cursor.description[idx][0], value)
                        for idx, value in enumerate(row))

        self.conn.row_factory = make_dicts
        self.c = self.conn.cursor()

    def close(self):
        self.conn.close()


class Init(Base):
    def __init__(self, dbpath):
        Base.__init__(self, dbpath)

        self.open()

        if self.isEmpty():
            self.initAll()

    def isEmpty(self):
        self.c.execute('SELECT name FROM sqlite_master WHERE type="table";')
        return self.c.fetchall() == []

    def initAll(self):
        self.initMentors()
        self.initShifts()
        self.initQuestions()

    def initMentors(self):
        self.c.execute("CREATE TABLE mentors "
                       "(userid TEXT PRIMARY KEY, "
                       "name TEXT, "
                       "username, "
                       "keywords VARCHAR(1000))")
        self.conn.commit()

    def initShifts(self):
        self.c.execute("CREATE TABLE shifts "
                       "(userid TEXT, "
                       "start TEXT, "
                       "end TEXT, "
                       "FOREIGN KEY(userid) REFERENCES mentors(userid))")
        self.conn.commit()

    def initQuestions(self):
        self.c.execute("CREATE TABLE questions "
                       "(id INTEGER PRIMARY KEY, "
                       "question TEXT, "
                       "answered INTEGER, "
                       "username TEXT, "
                       "userid TEXT, "
                       "timestamp INTEGER, "
                       "matchedMentors BLOB, "
                       "assignedMentor TEXT, "
                       "FOREIGN KEY(assignedMentor) REFERENCES mentors(userid))")
        self.conn.commit()


class DB(Init):
    def __init__(self, dbpath):
        Init.__init__(self, dbpath)

    def query_db(self, query, args=(), one=False):
        cur = self.conn.execute(query, args)
        rv = cur.fetchall()
        cur.close()

        return (rv[0] if rv else None) if one else rv

    def insertMentor(self, name, username, userid, keywords):
        CMD = "INSERT INTO mentors " \
              "(name, username, userid, keywords) " \
              "VALUES (?, ?, ?, ?)"
        self.c.execute(CMD, [name, username, userid, keywords])
        self.conn.commit()

    def insertShift(self, userid, start, end):
        CMD = "INSERT INTO shifts " \
              "(userid, start, end) " \
              "VALUES (?, ?, ?)"
        self.c.execute(CMD, [userid, start, end])
        self.conn.commit()

    def insertQuestion(self, question, username, userid, matchedMentors):
        CMD = "INSERT INTO questions " \
              "(question, answered, username, userid, timestamp, matchedMentors, assignedmentor) " \
              "VALUES (?, 0, ?, ?, datetime('now', 'localtime'), ?, NULL)"
        self.c.execute(CMD, [question, username, userid, matchedMentors])
        self.conn.commit()
        return self.c.lastrowid

    def answerQuestion(self, userid, questionId):
        CMD = "UPDATE questions " \
              "SET answered=1, " \
              "assignedMentor=? " \
              "WHERE id=?"

        self.c.execute(CMD, [userid, questionId])
        self.conn.commit()
