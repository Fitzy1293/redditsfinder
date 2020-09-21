#!/usr/bin/env python3

'''
github.com/fitzy1293/redditsfinder
TO DO:
    - REFACTOR getPosts. Name it something more appropriate relating to the fact that it gets the pushshift data.
    - Implement argparse instead of doing sys.argv[] conditions. Just learned about it and it is clearly much better.
        - Easily can do things like allow arbitrary numbers of users to be entered in one command.

'''

import urllib.request
import json
import time
import os,sys
from pprint import pprint
from urllib.error import HTTPError
from datetime import datetime
from pathlib import Path

from rich.table import Table,Column
from rich.console import Console

import redditsfinder_utils as redtil
import after_run_parsing as postrun
#─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
#=============================================================================================================================
#─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def getPosts(user, keyType, correctPostType): # Uses pushshift API. Functions kind of a mess but works.
    console = Console()

    apiUrl = 'https://api.pushshift.io/reddit/search/'
    # Max num of posts in each pushshift request, seems to be 100 right now or it breaks.
    postSetMaxLen = 100

    before = int(round(time.time()))
    beginTime = before
    allPosts = {}

    for postType in correctPostType:
        console.print(f'[bold blue]{postType[0].upper()}{postType[1:]} request log:')
        if postType == 'comment':
            highlight = '[cyan]'
        else:
            highlight = '[magenta]'

        ct = 0
        posts = []
        while True:  # We need to wait until we've collected all posts then break.
            time.sleep(.75)  # Avoids rate limits.
            url = f'{apiUrl}{postType}/?author={user}&size={postSetMaxLen}&before={before}'
            try:
                response = urllib.request.urlopen(url)
                data = json.loads(response.read())['data']

                for post in data:
                    ourKeys = keyType[postType]
                    postDict = dict.fromkeys(ourKeys, None)

                    for key in ourKeys:  # We are doing things for specific keys, so we need another loop.
                        if key in ourKeys and key in post.keys():  # To only use the keys we need.
                            outputValue = post[key]

                            # Thanks redditcleaner making this less painful.
                            if key == 'body' or key == 'selftext':
                                outputValue = redtil.humanReadablePost(outputValue)

                            if key == 'permalink':
                                outputValue = f'https://www.reddit.com{outputValue}'

                            # Create a datetime object from timestamp.
                            if key == 'created_utc':
                                timestamp = int(post[key])
                                postDict['datetime'] = str(datetime.utcfromtimestamp(
                                    timestamp).strftime('%a %b %d %Y, %I:%M %p UTC'))

                            postDict[key] = outputValue

                    posts.append(postDict)

                # Cause if it is there's something there which means more posts to get.
                if len(posts) != 0:
                    # Next time we make a request with the last timestamp from the list of posts.
                    before = posts[-1]['created_utc']

                ct = ct + len(data)
                console.print(f'{highlight}\t{ct} {url}')

                if len(data) < postSetMaxLen:  # Get 100 posts at a time they switched from 1000?
                    allPosts[postType + 's'] = posts
                    break

            except HTTPError:  # The sleep .75 deals with this.
                print('Rate limited')

        # before has been decreasing and we don't want it to start at the last comment for the beggining of submissions.
        before = beginTime
        print()

    if len(correctPostType) == 1:
        urls = [v for i in allPosts['submissions']  for k,v in i.items() if k == 'url']
        imageUrls = []
        for url in urls:
            if url.endswith(('.png', '.PNG', '.jpg', '.JPG', '.gif', '.GIF')):
                imageUrls.append(url)
                continue

            if '://reddit.com' in url:
                continue
            if 'imgur.com' in url:
                if '/a/' in url:
                    imageUrls.append(url + '/zip')
                else:
                    imageUrls.append(url + '.jpg')

        imageUrlsStr = '\n'.join(imageUrls)
        images = os.path.join(os.getcwd(), 'users', user, 'images.txt')
        with open(images, 'w+') as f:
            f.write(imageUrlsStr+ '\n')
        return imageUrlsStr

    else:
        return allPosts
#─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
#=============================================================================================================================
#─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def printTotals(totalsDict, userDir): #Printed stuff after the pushshift log.
    print('\n\n')
    console = Console()

    header = [
            'Recent comments:\nsubmissionID/comment_ID',
            'Recent submissions:\nsubmission_ID',
            'Comments count:\nfor each sub',
            f'[bold red]{totalsDict["commentsLen"]}[/bold red]',
            'Submissions count:\nfor each sub',
            f'[bold red]{totalsDict["submissionsLen"]}[/bold red]',
            totalsDict["dir"],
            'Run Time'
    ]

    console.log(f'[magenta]{totalsDict["user"]}')

    table = Table(show_header=True,header_style="bold blue")

    for i in header:
        table.add_column(i, justify='left')

    commentsColumn = '\n'.join([sub[0] for sub in totalsDict['postCounts']['comments']])
    commentsCt = '\n'.join([f'[bold red]{sub[1]}[/bold red]' for sub in totalsDict['postCounts']['comments']])

    submissionsColumn = '\n'.join([sub[0] for sub in totalsDict['postCounts']['submissions']])
    submissionsCt = '\n'.join([f'[bold red]{sub[1]}[/bold red]' for sub in totalsDict['postCounts']['submissions']])


    maxRecentPosts = 100
    posts = postrun.postRunJson(os.path.join(userDir, 'all_posts.json'), maxRecentPosts)

    table.add_row(
                posts[0],
                posts[1],
                f'[purple]{commentsColumn}[/purple]',
                commentsCt,
                f'[purple]{submissionsColumn}[/purple]',
                submissionsCt,
                '[magenta underline]all_posts.json\nsubreddit_count.txt',
                f'[magenta underline]{round(totalsDict["end"] - totalsDict["start"], 1)} s'
    )

    console.print(table, justify='left', style='bold white')

#─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
#=============================================================================================================================
#─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def run(user, options):
    start = time.time()

    userDir = Path.cwd() / 'users' / user
    userDir.mkdir(parents=True, exist_ok=True)

    print(f'Gathering and formatting data from pushshift for {user}.\n')

    if '-pics' in options:
        console = Console()
        keyType = {'submission': ('url', 'created_utc',)}
        images = getPosts(user, keyType, ['submission'])

        images = set(open(os.path.join(userDir,'images.txt')).read().splitlines())
        imageStatus = '\n'.join([f'[red]{i+1}\t[magenta]{image}' for i, image in enumerate(images)])
        imageSubmissionLog = f'[bold blue]Images submitted by {user}\n{imageStatus}'
        console.print(imageSubmissionLog)

        if '-d' in options:
            print()
            redtil.imagesdl(images, userDir)

        console.print(f'\n[bold blue]Run time - {round(time.time() - start, 1)} s')


    else:
        keyType = {'comment': ('id', 'created_utc', 'subreddit', 'body', 'score', 'permalink', 'link_id', 'parent_id'),
                   'submission': ('id', 'created_utc', 'subreddit', 'selftext', 'score', 'full_link', 'url')}

        allPosts = getPosts(user, keyType, ['comment', 'submission'])
        postCounts = redtil.countPosts(allPosts)
        redtil.writeFiles(allPosts, postCounts, user, userDir)

        totalsDict = {'postCounts': postCounts,
                      'commentsLen': str( len(allPosts['comments']) ),
                      'submissionsLen': str( len(allPosts['submissions']) ),
                      'dir': str(userDir),
                      'start': start,
                      'end': time.time(),
                      'user':user}


        printTotals(totalsDict, userDir)


#─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
#=============================================================================================================================
#─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
if __name__ == '__main__':  # System arguments.

    if len(sys.argv) == 1:
        print('Remember to add a username')
        print('For help enter redditsfinder -h')

    elif len(sys.argv) == 2:

        if sys.argv[-1] == '-h':
            print('Only argument is a username')
            print('Adding more options soon')
        else:
            run(sys.argv[-1], [''])

    elif len(sys.argv) >= 3:
        optArgs = [arg for arg in sys.argv[1:-1]]
        run(sys.argv[-1], optArgs)
