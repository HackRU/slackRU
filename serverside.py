from flask import Flask,request,jsonify,g
import sqlite3
import config
import util
from twilio.rest import Client
app = Flask(__name__)
dbpath = config.dbpath
ph = config.twilioph
qid = 0
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
    def make_dicts(cursor, row):
        return dict((cursor.description[idx][0], value)
                    for idx, value in enumerate(row))

    db.row_factory = make_dicts
    return db
def query_db(query, args=(), one=False):
    """
    Query function from flask documentation to avoid the usage of a raw cursor
    """
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()

    return (rv[0] if rv else None) if one else rv

@app.route("/pairmentor",methods = ['POST'])
def pairMentor():
    '''
        Route that client sends the question to
    '''
    print(request.form.to_dict())
    jsonreqest = request.form.to_dict()
    dat = jsonreqest['data']
    user = jsonreqest['user']
    textMentorsQuestion(dat,user)
    return "done"
#the twilio end point that will text mentors
def textMentorsQuestion(comment:str,username:str) -> None:
    """
     Given a question , tries to find mentors with the keywords with the key words and sends a message that a hacker needs help
    :param comment:str -> the input string the parse
    :param username:str -> the username of the person asking the question
    """
    global qid
    q_test = 0
    mentorlist = []
    #selec all the mentors 
    q = query_db("SELECT * from mentors")
    for keywordlist in q:
        print (keywordlist['phone'])

        li  = keywordlist['keywords'].split(',')
        for word in comment:
            if word in li:
                mentorlist.append(keywordlist)

                get_db().execute("INSERT into activequestions (answered,userid) VALUES(?,?)",[0,username]) 
                get_db().commit()
                q_test = query_db("SELECT last_insert_rowid()",one = True)
                break
    questionstruct[str(qid)] = {}
    questionstruct[str(qid)]['id'] = qid
    questionstruct[str(qid)]['phones'] =mentorlist
    questionstruct[str(qid)]['answered'] = False
    for mentor in mentorlist:
        #message all the mentor
        sendMessage(mentor['phone'],"hi, a hacker had a question, " + comment + " " + "please type accept " + str(q_test['last_insert_rowid()']) + " to accept" + " or " + "decline " + str(qid) +  " to decline")
    qid +=1

@app.route('/makeRequest',methods = ['POST'])
def makeRequest():
    from_no = request.form['From']
    body = request.form['Body']
    if len(body.split()) !=2:
        sendMessage(from_no,"please fix your formatting, either accept <id> or decline <id>")
    else :

        splitBody = body.split()
        if splitBody[0] == 'accept':

            if questionstruct[str(splitBody[0])]['answered']  == True:
                sendMessage(from_no,"Hi, Another mentor has already accepted this question")
            else :
                #message the user via slack using the util class as we are storing the USERNAME of the person
                name = query_db('select name from mentors where phone=?',from_no,one = True)
                util.message(questionstruct[str(splitBody[1])]['id'], "Hi You Have been paired with" + name + " , please goto the mentor table and meet the mentor and take the mentor back to you work area")
                questionstruct[splitBody[1]]['answered'] = True
                sendMessage(from_no,"Hi, You have been assigned this question, please goto the mentor desk and find the hacker")
        

    return "done"
def sendMessage(to:str,message:str) -> None:
    """
        Helper method to send messages
        :param to:str -> the phone numner to send to
        :param message:str -> the message we send
    """
    
    message = client.messages.create(
        to,
        body=message,
        from_=ph
       ) 
if __name__ == '__main__':
    app.run(debug=True)
