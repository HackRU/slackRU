import sqlite3


class Base:
    def __init__(self, dbpath):
        self.dbpath = dbpath
        self.conn = None
        self.c = None

    def open(self):
        self.conn = sqlite3.connect(self.dbpath)

        def make_dicts(cursor, row):
            return dict((cursor.description[idx][0], value)
                        for idx, value in enumerate(row))

        self.conn.row_factory = make_dicts
        self.c = self.conn.cursor()
        return self

    def close(self):
        self.conn.close()

    def execAndCommit(self, *args):
        self.c.execute(*args)
        self.conn.commit()


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
        self.initPosts()

    def initMentors(self):
        self.execAndCommit("CREATE TABLE mentors "
                           "(userid TEXT PRIMARY KEY, "
                           "name TEXT, "
                           "username, "
                           "keywords VARCHAR(1000))")

    def initShifts(self):
        self.execAndCommit("CREATE TABLE shifts "
                           "(userid TEXT, "
                           "start TEXT, "
                           "end TEXT, "
                           "FOREIGN KEY(userid) REFERENCES mentors(userid))")

    def initQuestions(self):
        self.execAndCommit("CREATE TABLE questions "
                           "(id INTEGER PRIMARY KEY, "
                           "question TEXT, "
                           "answered INTEGER, "
                           "username TEXT, "
                           "userid TEXT, "
                           "timestamp INTEGER, "
                           "matchedMentors BLOB, "
                           "assignedMentor TEXT, "
                           "FOREIGN KEY(assignedMentor) REFERENCES mentors(userid))")

    def initPosts(self):
        self.execAndCommit("CREATE TABLE posts "
                           "(questionId INTEGER, "
                           "userid TEXT, "
                           "channel TEXT, "
                           "timestamp TEXT, "
                           "FOREIGN KEY(questionId) REFERENCES questions(id), "
                           "FOREIGN KEY(userid) REFERENCES mentors(userid))")


class DB(Init):
    def __init__(self, dbpath):
        Init.__init__(self, dbpath)

    def runQuery(self, query, args=(), one=False):
        cur = self.conn.execute(query, args)
        rv = cur.fetchall()
        cur.close()

        return (rv[0] if rv else None) if one else rv

    def insertMentor(self, name, username, userid, keywords):
        CMD = "INSERT INTO mentors " \
              "(name, username, userid, keywords) " \
              "VALUES (?, ?, ?, ?)"
        self.execAndCommit(CMD, [name, username, userid, keywords])

    def insertShift(self, userid, start, end):
        CMD = "INSERT INTO shifts " \
              "(userid, start, end) " \
              "VALUES (?, ?, ?)"
        self.execAndCommit(CMD, [userid, start, end])

    def insertQuestion(self, question, username, userid, matchedMentors):
        CMD = "INSERT INTO questions " \
              "(question, answered, username, userid, timestamp, matchedMentors, assignedmentor) " \
              "VALUES (?, 0, ?, ?, datetime('now', 'localtime'), ?, NULL)"
        self.execAndCommit(CMD, [question, username, userid, matchedMentors])
        return self.c.lastrowid

    def insertPost(self, questionId, userid, channel, timestamp):
        CMD = "INSERT INTO posts " \
              "(questionId, userid, channel, timestamp) " \
              "VALUES (?, ?, ?, ?)"
        self.execAndCommit(CMD, [questionId, userid, channel, timestamp])

    def markAnswered(self, userid, questionId):
        CMD = "UPDATE questions " \
              "SET answered=1, " \
              "assignedMentor=? " \
              "WHERE id=?"

        self.execAndCommit(CMD, [userid, questionId])
