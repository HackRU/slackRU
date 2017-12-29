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
                       "(id INTEGER PRIMARY KEY, "
                       "name TEXT, "
                       "username, "
                       "userid TEXT, "
                       "keywords VARCHAR(1000))")
        self.conn.commit()

    def initShifts(self):
        self.c.execute("CREATE TABLE shifts "
                       "(mentor_id INTEGER, "
                       "start TEXT, "
                       "end TEXT, "
                       "FOREIGN KEY(mentor_id) REFERENCES mentors(id));")
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
                       "assignedMentor VARCHAR(255));")
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
        return self.c.lastrowid

    def insertShift(self, mentor_id, start, end):
        CMD = "INSERT INTO shifts " \
              "(mentor_id, start, end) " \
              "VALUES (?, ?, ?)"
        self.c.execute(CMD, [mentor_id, start, end])
        self.conn.commit()

    def insertQuestion(self, question, username, userid, matchedMentors):
        CMD = "INSERT INTO questions " \
              "(question, answered, username, userid, timestamp, matchedMentors, assignedmentor) " \
              "VALUES (?, 0, ?, ?, datetime('now', 'localtime'), ?, NULL)"
        self.c.execute(CMD, [question, username, userid, matchedMentors])
        self.conn.commit()
        return self.c.lastrowid
