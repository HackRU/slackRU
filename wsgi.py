""" WSGI: Web Server Gateway Interface

This file is used by the production AWS server (which uses the WSGI protocol) to run
the SlackRU flask application.
"""
from slackru import create_app

application = create_app()
