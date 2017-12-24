import sqlite3


class Base:
    def __init__(self, dbpath):
        self.dbpath = dbpath

    def open(self):
        self.conn = sqlite3.connect(self.dbpath)
        self.conn.row_factory = sqlite3.Row
        self.c = self.conn.cursor()
        return self

    def close(self):
        self.conn.close()


class Init(Base):
    def __init__(self, dbpath):
        Base.__init__(self, dbpath)

        self.open()

        if self.isEmpty():
            self.initAll()

        self.close()

    def isEmpty(self):
        self.c.execute('SELECT name FROM sqlite_master WHERE type="table";')
        return self.c.fetchall() == []

    def initAll(self):
        self.initMentors()
        self.initShifts()
        self.initQuestions()

    def initMentors(self):
        self.c.execute("CREATE TABLE mentors "
                       "(name TEXT, "
                       "keywords VARCHAR(1000), "
                       "id INTEGER PRIMARY KEY);")
        self.conn.commit()

    def initShifts(self):
        self.c.execute("CREATE TABLE shifts "
                       "(userid INTEGER, "
                       "start TEXT, "
                       "end TEXT, "
                       "FOREIGN KEY(userid) REFERENCES mentors(id));")
        self.conn.commit()

    def initQuestions(self):
        self.c.execute("CREATE TABLE questions "
                       "(id INTEGER PRIMARY KEY, "
                       "question TEXT, "
                       "answered INTEGER, "
                       "username INTEGER, "
                       "userid INTEGER, "
                       "timestamp INTEGER, "
                       "matchedMentors BLOB, "
                       "assignedMentor VARCHAR(255));")
        self.conn.commit()


def id_counter(method):
    def wrapper(*args):
        wrapper.id += 1
        return method(*args)
    wrapper.id = -1
    return wrapper


class DB(Init):
    def __init__(self, dbpath):
        Init.__init__(self, dbpath)

    def query_db(self, query, args=(), one=False):
        cur = self.conn.execute(query, args)
        rv = cur.fetchall()
        cur.close()

        return (rv[0] if rv else None) if one else rv

    @id_counter
    def insertQuestion(self, question, username, userid, matchedMentors):
        CMD = "INSERT INTO questions " \
              "(id, question, answered, username, userid, timestamp, matchedMentors, assignedmentor) " \
              "VALUES (?, ?, 0, ?, ?, datetime('now', 'localtime'), ?, NULL)"
        self.c.execute(CMD, [self.insertQuestion.id, question, username, userid, matchedMentors])
        return self.insertQuestion.id
