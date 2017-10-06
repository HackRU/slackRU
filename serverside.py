from flask import Flask
import sqlite3
import config
from twilio.rest import Client
app = Flask(__name__)
dbpath = config.dbpath
ph = config.twilioph
qid = 1
questionstruct = {}
#setup twilio with sid and authid
client = Client(config.sid, config.authid)
def get_db():
    """
    From the Flask Websitei, probs best practice to connect to the databse this way
    """
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(dbpath)
    return db
def query_db(query, args=(), one=False):
    """
    Query function from flask documentation to avoid the usage of a raw cursor
    """
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

@app.route("/pairmentor")
def pairMentor(methods = ['POST']):
    return "Hello World!"

#the twilio end point that will text mentors
def textMentorsQuestion(comment:str,username:str) -> None:
    """
     Given a question , tries to find mentors with the keywords with the key words and sends a message that a hacker needs help
    :param comment:str -> the input string the parse
    :param username:str -> the username of the person asking the question
    """
    mentorlist = []
    #selec all the mentors 
    q = query_db("SELECT * from mentors")
    for keywordlist in q:
        for word in comment:
            if word in keywordlist['keywords']:
                mentorlist.append(q['phone'])
    questionstruct[str(qid)] = {}
    questionstruct[str(qid)]['id'] = qid
    questionstruct[str(qid)]['phones'] =mentorlist
    questionstruct[str(qid)]['answered'] = False
    for mentor in mentorlist:
        #message all the mentor
        message = client.messages.create(
        mentor['phone'],
        body="Hi, A Hacker had a question, " + comment + " " + "please type accept " + str(qid) " to accept" + " or " + "decline " + str(qid) " to decline"),
        from_=ph,
       ) 
    qid +=1

@app.route('/makeRequest',methods = ['POST'])
def makeRequest():

    return "done"


    
