import time
import queue
import threading

queueOfTimes = queue.Queue()




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
