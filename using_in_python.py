#!/bin/env python3

import redditsfinder
from pprint import pprint

pprint(redditsfinder.submissions(user='boomerfelonowl', log=True))

print("\nComments")
comments = redditsfinder.comments(lim=25, user='boomerfelonowl')
pprint([v for dict in comments  for k, v in dict.items() if k == 'body'])

submissions = redditsfinder.submissions(lim=25, user='boomerfelonowl')
print("\nText Posts")
pprint([v for dict in submissions  for k, v in dict.items() if k == 'selftext'])
