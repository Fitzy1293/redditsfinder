# redditsfinder
Python tool to get all of a users posts. Uses the pushshift API with different timestamps to get sets of posts.
PRAW is the wrapper for using python with reddits API, but reddits API is limited to 1000 posts with no real good way of getting around it.

# To install 
 Linux
 `cd ~ && mkdir -p redditsfinder && cd redditsfinder && wget http://github.com/Fitzy1293/redditsfinder/blob/master/push.py`

# How to use
 Make sure you are in the path where redditsfinder was installed. 
 `python3 push.py [redditUsername]`
