# redditsfinder - A simple tool to analyze reddit users

## The goal of this program is ease of use and correctly grabbing every post from a reddit user. <br/> 


***Linux install instructions***\
`pip3 install redditcleaner` \
`wget https://raw.githubusercontent.com/Fitzy1293/redditsfinder/master/redditsfinder.py` \
`mv redditsfinder.py ~/bin/redditsfinder && chmod +x ~/bin/redditsfinder`\
Do the last command with regard to however you handle creating new commands. 

***Mac***\
`pip3 install redditcleaner` \
`curl https://raw.githubusercontent.com/Fitzy1293/redditsfinder/master/redditsfinder.py > redditsfinder.py` \
`mv redditsfinder.py ~/bin/redditsfinder && chmod +x ~/bin/redditsfinder`\
Mac doesn't include wget, so curl it into a new file instead. \
Might work, haven't tested it though so who knows.

***Windows***\
Run this in PowerShell\
`wget https://raw.githubusercontent.com/Fitzy1293/redditsfinder/master/redditsfinder.py -OutFile redditsfinder.py`\
PowerShell has wget, but you need to specify it's output file. 

# How to use
![Imgur Image](https://i.imgur.com/yOuflW5.gif)

If you did the full unix like install. `redditsfinder [redditUsername]` \
To run with python. `python3 redditsfinder.py [redditUsername]` \
Make sure you're in the redditsfinder directory for the python interpreter way.\
**Make sure you have python3 installed**.

# Example JSON object

![Imgur Image](https://i.imgur.com/jHcdUKB.png)

# Why bother with this? 
If you want to archive a reddit user's posts it's impossible to do with the reddit API if there are more than 1k posts. \
This was primarily designed to be used as a linux command line tool. I'm not as familiar with making Windows shell scripts but if someone wanted to help make a Windows one line install that'd be great. \
**The ultimage goal is to trim and automate the collection of data from pushshift and improve readability of each post object, while adding things like datetime.** 
