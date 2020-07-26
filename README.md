# redditsfinder - A simple tool to analyze reddit users
![Alt text](images/readable.png "Optional Title") 
## The goal of this program is ease of use and correctly grabbing every post. <br/> 
***Linux one line install*** \
`wget -O - https://raw.githubusercontent.com/Fitzy1293/redditsfinder/master/install.sh | bash`

***Contents of install.sh***\
`cd ~ && pip3 install redditcleaner && mkdir -p redditsfinder && cd redditsfinder && wget https://raw.githubusercontent.com/Fitzy1293/redditsfinder/master/push.py
mkdir -p ~/bin && cp push.py ~/bin/redditsfinder && cd ~/bin && chmod +x redditsfinder && rm -rf ~/redditsfinder && cd ~ 
echo "Successfully installed redditsfinder"`



***Windows & Mac***\
Copy and paste the code from push.py wherever you want. \
To do the one line install on Windows you could use a linux virtual machine, or get Ubuntu from the Windows store which is apparently possible. 

# How to use
If you did the full linux install. `redditsfinder [redditUsername]` \
If you only ran the first linux install command or are on Windows or Mac. `python3 push.py [redditUsername]` \
Make sure you're in the redditsfinder directory for the python interpreter way.\
**Make sure you have python3 installed**.

# Example terminal output
![Alt text](images/log.png?raw=true "Optional Title")\
![Alt text](images/out.png?raw=true "Optional Title")

# Why bother with this? 
If you want to archive a reddit user's posts it's impossible to do with the reddit API if there are more than 1k posts. \
This was primarily designed to be used as a linux command line tool. I'm not as familiar with making Windows shell scripts but if someone wanted to help make a Windows one line install that'd be great. \
**The ultimage goal is to trim and automate the collection of data from pushshift and improve readability of each post object, while adding things like datetime.** 
