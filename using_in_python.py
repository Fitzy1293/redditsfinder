#!/bin/env python3

import redditsfinder
from pprint import pprint

# Pretty prints all submission dicts
pprint(redditsfinder.submissions(user='spez', log=True))

# Pretty prints all comment bodies and text based self-posts.
print("Comments")
comments = redditsfinder.comments(lim=25, user='spez')
bodies = [v for dict in comments  for k, v in dict.items() if k == 'body']
pprint(bodies)

submissions = redditsfinder.submissions(lim=25, user='spez')
print("\nText Posts")
selftexts = [v for dict in submissions  for k, v in dict.items() if k == 'spez']
pprint(selftexts)
