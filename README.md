# redditsfinder - A simple tool to analyze reddit users. 
Python tool to get all of a users submissions and comments. Uses the pushshift API with different timestamps to get sets of posts. \
PRAW is the wrapper for using python with reddits API, but reddits API is limited to 1000 posts with no real good way of getting around it.\
The only argument is a reddit username. \
Output is important fields from pushshift and check for which subreddits the person posts the most in.


# To install 
I would like to add a shell script to ~/bin so you don't have to type out the python commands.\
Not really important for it to work though.\
*Linux basic build*.\
`cd ~ && mkdir -p redditsfinder && cd redditsfinder && wget https://raw.githubusercontent.com/Fitzy1293/redditsfinder/master/push.py`\
Windows & Mac\
Copy and paste the code from push.py wherever you want. 


# How to use
Make sure you are in the path where redditsfinder was installed. \
`python3 push.py [redditUsername]` \
The location of the output files are listed when the script is finished.
