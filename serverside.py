from flask import Flask
import sqlite3
import config
from twilio.rest import Client
app = Flask(__name__)
dbpath = config.dbpath
ph = config.twilioph
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
def pairMentorWithHacker(comment:str,username:str):
    """
    pairs a mentor with a hacker using the kwywords from the senntence
    :param comment:str -> the input string the parse
    :param username:str -> the username of the person asking the question
    """
    mentorlist = []
    #selec all the mentors 
    q = query_db("SELECT * from mentors")
    for keywordlist in q:
        for word in comment:
            if word in keywordlist['kewywords']:
                mentorlist.append(q)
    #insert the question and mentor list into the datavatse
    query_db("INSERT INTO ActiveQuestions (question,phones,is_ans) VALUES (?,?,?)",comment,str(mentorlist),False)

    for mentor in mentorlist:
        #message all the mentor
        message = client.messages.create(
        mentor['phone'],
        body="Hi, A Hacker had a question, " + comment + " " + "please meet the hacker at the mentor table"),
        from_=ph,
       ) 
    return mentorlist

@app.route('/makeRequest',methods = ['POST'])
def makeRequest():
    return "done"


    
