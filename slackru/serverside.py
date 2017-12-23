import time
import queue
import threading


queueOfTimes = queue.Queue()


def query_db(db, query, args=(), one=False):
    """
    Query function from flask documentation to avoid the usage of a raw cursor
    """
    cur = db.conn.execute(query, args)
    rv = cur.fetchall()
    cur.close()

    return (rv[0] if rv else None) if one else rv


def schedulequeueScan(app):
    if queueOfTimes.qsize() > 0:
        ep = queueOfTimes.get()
        with app.app_context():
            quest = query_db("SELECT * from activequestions WHERE timestamp = ?", [ep], one=True)
            currentepoch = int(time.time())
            if ((currentepoch - quest['timestamp']) > 600):
                pass  # messageHackersToTryAgain(quest['id'])
            else:
                queueOfTimes.put(quest['timestamp'])
    # every 5 min run the scanner
    threading.Timer(300.0, schedulequeueScan).start()
