import sys
from slackru.config import getConfig


def server():
    from slackru import create_app
    app = create_app(getConfig['development'])
    app.run()


def client():
    print("Running Client!")


{'-s': server, '-c': client}[sys.argv[1]]()
