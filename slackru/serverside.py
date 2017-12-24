import json


def askQuestion(db, question, username, userid):
    query = "SELECT mentors.* FROM shifts " \
            "JOIN mentors ON mentors.id = shifts.userid " \
            "WHERE datetime('now', 'localtime') >= datetime(shifts.start) AND " \
            "datetime('now', 'localtime') < datetime(shifts.end)"

    matchedMentors = []
    query_results = db.query_db(query)
    for mentor in query_results:
        keywords = mentor['keywords'].split(',')
        for word in question.split():
            if word in keywords:
                matchedMentors.append(mentor)
                break

    if matchedMentors == []:
        for mentor in query_results:
            matchedMentors.append(mentor)

    return db.insertQuestion(question, username, userid, json.dumps(matchedMentors))
