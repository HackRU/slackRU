""" All SQLite database interactions should route through a DB instance """

from datetime import datetime

from slackru import sqlalch_db as db


#####################
#  Database Models  #
#####################
class Mentor(db.Model):
    __tablename__ = 'mentors'
    userid = db.Column(db.String(64), primary_key=True)
    fullname = db.Column(db.String(64))
    username = db.Column(db.String(64))
    phone_number = db.Column(db.String(12), unique=True)
    keywords = db.Column(db.String(1000))
    questions = db.relationship('Question', backref='mentor', lazy=True)
    posts = db.relationship('Post', backref='mentor', lazy=True)


class Question(db.Model):
    __tablename__ = "questions"
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(64))
    answered = db.Column(db.Boolean)
    username = db.Column(db.String(64))
    userid = db.Column(db.String(64))
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    matchedMentors = db.Column(db.String(128))
    assignedMentor = db.Column(db.String(64), db.ForeignKey('mentors.userid'), nullable=False)
    posts = db.relationship('Post', backref='question', lazy=True)


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    questionId = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    userid = db.Column(db.String(64), db.ForeignKey('mentors.userid'), nullable=False)
    channel = db.Column(db.String(64))
    timestamp = db.Column(db.Integer)


db.create_all()


#######################
#  Database Wrappers  #
#######################
class BaseDB:
    """ Base Database Class """
    def __init__(self):
        self.Mentor = Mentor
        self.Post = Post
        self.Question = Question

    def execAndCommit(self, *objs):
        for obj in objs:
            db.session.add(obj)
        db.session.commit()

    def __getattr__(self, name):
        method = getattr(db, name)
        return method


class InsertDB(BaseDB):
    """ Insert Operations """
    def insertMentor(self, fullname: str, username: str, userid: str,
            phone_number: str, keywords: str):
        isDuplicate = False
        mentor = Mentor.query.filter_by(userid=userid).first()
        if mentor is not None:
            mentor.fullname = fullname
            mentor.phone_number = phone_number
            mentor.keywords = keywords
            db.session.commit()
            isDuplicate = True
        else:
            mentor = Mentor(fullname=fullname, username=username, userid=userid,
                    phone_number=phone_number, keywords=keywords)
            self.execAndCommit(mentor)

        return isDuplicate

    def insertQuestion(self, question: str, userid: str, matchedMentors: '[str]'):
        Q = Question(question=question, userid=userid, matchedMentors=matchedMentors,
                assignedMentor='')
        self.execAndCommit(Q)
        return Question.query.order_by(Question.id).all()[-1].id

    def insertPost(self, questionId: int, userid: str, channel: str, timestamp: str):
        post = Post(questionId=questionId, userid=userid, channel=channel,
                timestamp=timestamp)
        self.execAndCommit(post)


class DB(InsertDB):
    """ DB Interface Class """
    def markAnswered(self, userid: str, questionId: int):
        Q = Question.query.get(questionId)
        Q.answered = True
        Q.assignedMentor = userid

        self.execAndCommit(Q)
