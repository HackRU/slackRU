import json
import slackru.util as util


def askQuestion(db, question: str, username: str, userid: str) -> (int, list):
    query = "SELECT mentors.* FROM shifts " \
            "JOIN mentors ON mentors.userid = shifts.userid " \
            "WHERE datetime('now', 'localtime') >= datetime(shifts.start) " \
            "AND datetime('now', 'localtime') < datetime(shifts.end)"

    matchedMentors = []
    query_results = db.query_db(query)
    for mentor in query_results:
        keywords = [word.lower() for word in mentor['keywords'].split(',')]
        for word in question.split():
            if word.lower() in keywords:
                matchedMentors.append(mentor['userid'])
                break

    if matchedMentors == []:
        for mentor in query_results:
            matchedMentors.append(mentor['userid'])

    questionId = db.insertQuestion(question, username, userid, json.dumps(matchedMentors))

    return (questionId, matchedMentors)


def answerQuestion(db, userid: str, questionId: int, accept: bool):
    if accept:
        db.answerQuestion(userid, questionId)
        util.deleteDirectMessages(questionId, all=True)
    else:
        util.deleteDirectMessages(userid=userid)
