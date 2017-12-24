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

    def initQuestions(self):
        self.c.execute("CREATE TABLE questions "
                       "(id INTEGER PRIMARY KEY, "
                       "answered INTEGER, "
                       "username INTEGER, "
                       "userid INTEGER, "
                       "timestamp INTEGER, "
                       "phones BLOB, "
                       "peoplewhoans BLOB, "
                       "assignedmentor VARCHAR(255));")
        self.conn.commit()


class DB(Init):
    def __init__(self, dbpath):
        Init.__init__(self, dbpath)

    def query_db(self, query, args=(), one=False):
        cur = self.conn.execute(query, args)
        rv = cur.fetchall()
        cur.close()

        return (rv[0] if rv else None) if one else rv
