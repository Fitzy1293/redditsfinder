# redditsfinder - A simple tool to analyze reddit users. 
Python tool to get all of a users submissions and comments. Uses the pushshift API with different timestamps to get sets of posts. \
The only argument is a reddit username. 

# Installation 
**Linux single command basic build**\
`cd ~ && mkdir -p redditsfinder && cd redditsfinder && wget https://raw.githubusercontent.com/Fitzy1293/redditsfinder/master/push.py`
I would like to add a shell script to ~/bin so you don't have to type out the python commands.\
Not really important for it to work though.\

**Windows & Mac**\
Copy and paste the code from push.py wherever you want. 





# How to use
Usage > `python3 push.py [redditUsername]` \
Make sure you have python3 installed.\
Make sure you are in the path where redditsfinder was installed. \
**Example terminal output**\
![Alt text](runScript.png?raw=true "Optional Title")

# Files created by the script
**Example post object**
![Alt text](genericObject.png?raw=true "Optional Title") \
**Example subreddit rankings**\
![Alt text](rank.png?raw=true "Optional Title")

