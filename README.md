# redditsfinder - reddit user info
**`pip3 install redditsfinder`**

**A program to get reddit user post data.**

```Running redditsfinder

Test it on a user to make sure it works.
    redditsfinder someusername

Basic usage
    redditsfinder username
    redditsfinder [options] username_0 username_1 username_2 ...

With an input file
    -f or --file.
    redditsfinder [options] -f line_separated_text_file.txt

Examples
    - just print the summary table to stdout
        $ redditsfinder someusername

    - save data locally and print the summary table to stdout
        $ redditsfinder --write someusername

    - just save data locally without printing
        $ redditsfinder --write --quiet someusername

    - download pictures
        $ redditsfinder --pics someusername

Optional args
    --pics returns URLs of image uploads
    -pics -d or --pics --download downloads them
    -quiet or -q turns off printing
```
<<<<<<< HEAD
=======


```python3


import redditsfinder
from pprint import pprint

'''
This code uses redditsfinder to get text based posts.
'''

def byKey(posts, postKey=''):
    return [v for dict in posts  for k, v in dict.items() if k == postKey]

user = 'spez'
lim = 5

comments = redditsfinder.comments(lim=lim, user=user)
submissions = redditsfinder.submissions(lim=lim, user=user)

textPosts = {
    'bodies': byKey(comments, postKey='body'),
    'selftexts': byKey(submissions, postKey='selftext')
    }

pprint(textPosts)

```

***CLI usage***

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
>>>>>>> refs/remotes/origin/master
