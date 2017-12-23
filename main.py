import sys
from slackru.serverside import app


def server():
    app.run()


def client():
    print("Running Client!")


{'-s': server, '-c': client}[sys.argv[1]]()
