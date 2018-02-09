from threading import Thread

from slackru import create_app
from slackru.bot.slackbot import SlackBot

bot = SlackBot()
t = Thread(target=bot.run)
t.start()

application = create_app()


if __name__ == "__main__":
    application.debug = True
    application.run()
