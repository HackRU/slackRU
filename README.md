# SlackRU


|Commands|Status|Comments|
|--------|:----:|:------:|
|checkStatus|Finished||
|busy|Finished||
|unbusy|Finished||
|mentors|Finished|Needs testing with mentor channel id|
|shortenlist|Finished||
|help|Finished||

### Backlog
- [X] We don't need a password on unbusy/busy or status
- [ ] Change password in the event that it is exposed!
- [X] Continuous reminder about how to use commands
- [ ] Funny Stuff? randomgif :D?
- [X] What's next command: Tells the users whats next on the list of events (next 5 events?)
- [X] Code review
- [X] Function to find a userid given a username
- [X] Make a new row for 'MentorID' in sqlite3
- [X] Annoucements -> (syncing with google calendar?)
- [ ] Being able to change anoucements based on calendar/director changes
- [X] Testing Database
- [X] Testing all functions on dummy data
- [X] MentorID's and Mentor Channel ID's integrated
- [ ] Message all directors function
- [X] How many hours left in the hackathon?

# SlackRU for F 2017
- Text the issue to all people who are related to question after a few minutes if not dequed it would go to the help desk. Mentors and Hackers go to Mentor Desk when you dequeue request.
- Give name when the dequeue happens

Hacker has question on python -> Question is sent out in text form to all mentors who know python -> First person to dequeue is told to go to mentor table, Also tell hacker the same

-> Text them saying no one is avaliable with that resource, go to mentor desk for further help -> Done
                                                   
-> No hacker avaliable (Every mentor on shift that knows python said no) -> Text back in 10-15min -> return to the loop
                                                   
 -> In the case that people ignore it/some said no -> request is automated to those who ignored it to do stuff (Automated need different commands for this so we know what the mentor is referencing) -> Ignoring Automated Calls                                               or our calls more than x times, text them "We will not text/call you again, a note has been made about this, please talk to the mentor table to be reconsidered"

- For the onsite mentors we need a form for them to sign up!
- We need a feed of all questions
- Send it out to all mentors on shift if there is no one who knows it
- Slack bot server and Actual server to do commands.
