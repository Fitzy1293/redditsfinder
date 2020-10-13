#!/bin/env python3

import redditsfinder
from pprint import pprint

#Pretty prints all submission dicts
#pprint(redditsfinder.submissions(user='spez', log=True))

# Pretty prints all comment bodies and text based self-posts.
comments = redditsfinder.comments(lim=5, user='spez')
bodies = [v for dict in comments  for k, v in dict.items() if k == 'body']

submissions = redditsfinder.submissions(lim=5, user='spez')
selftexts = [v for dict in submissions  for k, v in dict.items() if k == 'selftext']

pprint(bodies)
pprint(selftexts)
