# redditsfinder - reddit user info
**`pip3 install redditsfinder`**

**A program to get reddit user post data.**

The colored terminal features for the CLI are from https://github.com/willmcgugan/rich \
`pip3 install rich` which is one the coolest python packages.

https://github.com/LoLei/redditcleaner `pip3 install redditcleaner` was also a massive help for dealing with reddit's markdown.

# Installation
`pip3 install redditsfinder`

# Running redditsfinder

***Test it on yourself to make sure it works (or another valid user name).***

`redditsfinder yourusername`

***In a python file***

**Currently working on making it usable in python files.**

**As of version 1.3.2 you can use it to make standard python objects.**

```python3
from redditsfinder import submissions
from pprint import pprint

#Pretty prints all submission dicts.
pprint(submissions(user='spez', log=True))

```


```python3
'''
This code uses redditsfinder to get text based posts.
    redditsfinder.comments(lim=lim, user=user)
    redditsfinder.submissions(lim=lim, user=user)
'''

import redditsfinder
from pprint import pprint

def byKey(posts, postKey=''):
    return [v for dict in posts  for k, v in dict.items() if k == postKey]

user = 'spez'
lim = 5

comments = redditsfinder.comments(lim=lim, user=user)
bodies = byKey(comments, postKey='body')

submissions = redditsfinder.submissions(lim=lim, user=user)
selftexts = byKey(submissions, postKey='selftext')

textPosts = {'bodies': bodies, 'selftexts': selftexts}
pprint(textPosts)

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

# User object
```json

{
    "comments": [
      {
          "id": "comment_1",
          "created_utc": 0,
          "subreddit": "",
          "score": 1,
          "link_id": "",
          "parent_id": "",
          "datetime": "",
          "permalink": "",
          "body": ["word_1", "word_2", "word_3", "..."]

      },

      {
          "id": "comment_2",
          "created_utc": 0,
          "subreddit": "",
          "score": 1,
          "link_id": "",
          "parent_id": "",
          "datetime": "",
          "permalink": "",
          "body": ["word_1", "word_2", "word_3", "..."]

      }

      ],

    "submissions": [

      {
        "id": "submission_1",
        "created_utc": 0,
        "subreddit": "",
        "score": 1,
        "link_id": "",
        "parent_id": "",
        "datetime": "",
        "url": "",
        "full_link": "",
        "selftext": ["word_1", "word_2", "word_3", "..."]

      },

      {
          "id": "submission_2",
          "created_utc": 0,
          "subreddit": "",
          "score": 1,
          "link_id": "",
          "parent_id": "",
          "datetime": "",
          "url": "",
          "full_link": "",
          "selftext": ["word_1", "word_2", "word_3", "..."]

      }

    ]

}

```

# Example Pushshift request log
![Imgur Image](https://imgur.com/VJDzFAh.png)

# Example terminal table
![Imgur Image](https://imgur.com/ZncrWFX.png)
