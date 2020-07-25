# redditsfinder - A simple tool to analyze reddit users
![Alt text](images/readable.png "Optional Title") \
Python tool to get all submissions and comments of a reddit user. \
Uses the pushshift API with different timestamps to get sets of posts. \
The only argument is a reddit username. 

# Installation 
**Make sure you have python3 installed**.\
***Linux*** \
Get python source.\
`cd ~ && pip3 install redditcleaner && mkdir -p redditsfinder && cd redditsfinder && wget https://raw.githubusercontent.com/Fitzy1293/redditsfinder/master/push.py`\
Add to your bin to use as a command line tool. \
`mkdir -p ~/bin && cp push.py ~/bin/redditsfinder && cd ~/bin && chmod +x redditsfinder`


***Windows & Mac***\
Copy and paste the code from push.py wherever you want. 





# How to use
If you did the full linux install. `redditsfinder[redditUsername]` \
If you only ran the first linux command or are on Windows or Mac. `python3 push.py [redditUsername]` \
Make sure you're in the reddtsfinder directory for the python interpreter way.

**Example terminal output**\
![Alt text](images/runScript.png?raw=true "Optional Title")

# User's subreddit rankings

**Example subreddit rankings**\
![Alt text](images/rank.png?raw=true "Optional Title")

