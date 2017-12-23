import sys
from slackru.config import getConfig


def server():
    from slackru import create_app
    app = create_app(getConfig['development'])
    app.run()


def client():
    print("Running Client!")


options = dict.fromkeys(['-s', '--server'], server)
options.update(dict.fromkeys(['-c', '--client'], client))

if __name__ == '__main__':
    options[sys.argv[1]]()
