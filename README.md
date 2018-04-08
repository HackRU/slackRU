# Waffle Project Management

[![Waffle.io - Columns and their card count](https://badge.waffle.io/HackRU/SlackRU.svg?columns=all)](https://waffle.io/HackRU/SlackRU)

# Deployment

There are two parts to deploying SlackRU:

#### (1) Deploying the Server
The server is a Flask app. This can be deployed using any cloud server infrastructure that supports Flask. We have previously used an AWS beanstalk. Documentation for deploying a Flask app on a beanstalk can be found [here](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/create-deploy-python-flask.html).

#### (2) Deploying the SlackBot

The SlackBot connects to the Slack workspace using Slack's API. As such, the SlackBot can be launched from any machine with a working internet connection using `python main.py --config production slackbot`. It is preferable to deploy the SlackBot on a reliable cloud server (as opposed to deploying it on your own local machine).

# New Feature Ideas!
Be creative and liberal. It is expected that most of these features will never see the light of day, so feel free to dream big!

- [ ] `@<bot> mentors` command could prompt users for a "tag" (e.g. python, java, twilio, ...). This would give the hackers a view into the internals of the mentor matching and might make for better mentor matches.
- [ ] Scrape StackOverFlow for answers to hacker questions.
- [ ] Optimize shifts based on keywords (e.g. make sure someone with Python experience is always on shift).
- [ ] How can we gather stats from first hackathon to improve next one?
- [ ] No more `@<bot>` to start SlackBot commands (could we use Slack "slash" commands instead?: https://api.slack.com/slash-commands).
- [ ] Identify Female Names. Match female hackers w/ female mentors when possible. Not sure if this is desirable or not. Would definitely need to get a thumbs up before implementing something like this.
- [ ] Move these ideas to the homepage of the SlackRU Flask server (which doesn't currently exist) and add a "Like" button. Track and display how many likes each idea has.
- [ ] Tell A.I. Jokes.

# SlackRUTest
Is the Slack workspace we use for testing. Reach out to me if you are (or want to start) helping develop SlackRU and need access (bryan.bugyi@rutgers.edu).
