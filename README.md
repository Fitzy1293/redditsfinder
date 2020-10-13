# redditsfinder --- reddit user info
**`pip3 install redditsfinder`**

**A command line program to easily download reddit users' post histories.**

Get any reddit user's entire post history with one command while avoiding the reddit API's 1000 post limit. \
The main functionality of this program is making the requests to pushshift and manipulating pushshift's JSON for into more convenient data.

The colored terminal features and markup are from https://github.com/willmcgugan/rich \
`pip3 install rich` which is one the coolest python packages I've seen. It's very easy to pick up, but as is shown with the animated example in its README, still has a lot of depth.  

https://github.com/LoLei/redditcleaner `pip3 install redditcleaner` was also a massive help for dealing with reddit's strange markup. \
Comments and self-posts can be unreadable when put in another format like JSON if they have a fair amount of formatting. \
To deal with it, I gave up and looked online for an alternative. Luckily there was a good one readily available.

# Installation
`pip3 install redditsfinder`

# Running redditsfinder

***Test it on yourself to make sure it works.***

`redditsfinder yourusername`

***In a python file***

**Currently working on making it usable in python files.**

**As of version 1.3.2 you can use it to make standard python objects**

```python3

import redditsfinder
from pprint import pprint

#Pretty prints all submission dicts
pprint(redditsfinder.submissions(user='spez', log=True))

# Pretty prints all comment bodies and text based self-posts.
user = 'spez'
lim = 5

comments = redditsfinder.comments(lim=lim, user=user)
bodies = [v for dict in comments  for k, v in dict.items() if k == 'body']

submissions = redditsfinder.submissions(lim=lim, user=user)
selftexts = [v for dict in submissions  for k, v in dict.items() if k == 'selftext']

pprint(bodies)
pprint(selftexts)

```

***Basic usage***

**Returns every post to a different JSON file for each user and formats a table in the terminal for a quick view.\
Takes an arbitrary number of user names, such that there is at least one user name.**\
\
`redditsfinder username`\
`redditsfinder [options] username_0 username_1 username_2 ...`

***Newline separated file***

**Uses user names from a file.**\
\
`-f` or `--file`\
`redditsfinder [options] -f line_separated_text_file.txt`




***Optional args***

`-pics` returns URLs of image uploads.\
`-pics -d` or `-pics --download` downloads them.\
`-q` or `--quiet` turns off non log related print statements.

# Example Pushshift request log
![Imgur Image](https://imgur.com/VJDzFAh.png)

# Example terminal table
![Imgur Image](https://imgur.com/ZncrWFX.png)

# Example JSON object
![Imgur Image](https://imgur.com/SfoDXHQ.png)
