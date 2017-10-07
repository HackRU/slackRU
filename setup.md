Hello, this is a guide about how to get the Slackbot up and running.
1. You will need to first create a slack workspace in order to get working so go do that
2. Now, you will need to add a bot integration. I know there is probably a better way to do this but
    I don't reall know how to cuz I'm a bit lazy (feel free to provide better instructions). Go to
    https://api.slack.com/bot-users and scroll down to the section called "Custom bot users" and click
    the link that says "creating a new bot user". Make the bot.
3. cp config.py.sample config.py
4. Now, you will need 3 things to get it up and running. You will need your oauth token, which can be obtained
    by heading to "OAuth & Permissions" in your slackAPI developer console (left hand side) and copy the value
    in OAuth Access Token. Set the value oauthT to that value. In your bot integrations page, there should be
    an API Token at the top, copy that value and set apiT to that value. 
5. Go to your workspace, and add your bot to one of the channels
6. Now, you will need to get the botID. I do not really know how but my advice is to execute "python slackrureborn.py"
    ,go into the channel and type @<botname> hello, and see what the code in the console is. It should be in json format
    in the field called "text". It should show up as <@[random-string-of-characters>. That random string of characters
    is your botID.
7. You are all set to go.
