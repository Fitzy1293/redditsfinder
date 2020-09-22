#!/usr/bin/env python3

'''
github.com/fitzy1293/redditsfinder
TO DO:
    - REFACTOR getPosts. Name it something more appropriate relating to the fact that it gets the pushshift data.
        #Done
    - Implement argparse instead of doing sys.argv[] conditions. Just learned about it and it is clearly much better.
        - Easily can do things like allow arbitrary numbers of users to be entered in one command.

'''

import urllib.request
import requests
import json
import time
import os,sys
import traceback
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
def cleanupPostData(postData, postType): #Thanks /u/kwelzel for helping me refactor!
    interestingPostData = {}

    timestamp = int(postData['created_utc'])
    interestingPostData['datetime'] = str(datetime.utcfromtimestamp(timestamp).strftime('%a %b %d %Y, %I:%M %p UTC'))

    submissionAndCommentKeys = ('id', 'created_utc', 'subreddit', 'score', 'link_id', 'parent_id') #
    for i in submissionAndCommentKeys:
        if i in postData.keys():
            interestingPostData[i] = postData[i]

    if postType == 'comment':
        if 'body' in postData.keys():
            interestingPostData['body'] = redtil.humanReadablePost(postData['body'])
        if 'permalink' in postData.keys():
            interestingPostData['permalink'] = f'https://www.reddit.com{postData["permalink"]}'

    if postType == 'submission':
        if 'selftext' in postData.keys():
            interestingPostData['selftext'] = redtil.humanReadablePost(postData['selftext'])
        if 'url' in postData.keys():
            interestingPostData['url'] = postData["url"]

    return interestingPostData
#─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
#=============================================================================================================================
#─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def getPosts(user, postType): # Pushshift API requests in chunks of 100
    console = Console()
    console.print(f'[bold blue]{postType[0].upper()}{postType[1:]} request log:')

    apiUrl = 'https://api.pushshift.io/reddit/search/'
    postSetMaxLen = 100 # Max num of posts in each pushshift request, seems to be 100 right now or it breaks.

    before = int(round(time.time()))
    beginTime = before
    allPosts = {}

    if postType == 'comment':
        highlight = '[cyan]'
    else:
        highlight = '[magenta]'

    ct, testCt = 0, 0

    posts = []
    while True:
        time.sleep(.75)
        url = f'{apiUrl}{postType}/?author={user}&size={postSetMaxLen}&before={before}'

        response = requests.get(apiUrl + postType, params={'author': user, 'size': postSetMaxLen, 'before': before})
        data = response.json()['data']
        if not data:
            break

        for postData in data:
            before = postData['created_utc']
            yield cleanupPostData(postData, postType)

        #testCt+=1 #For testing.
        #if testCt>1: break

        ct = ct + len(data)
        console.print(f'[red]\t{ct} {highlight}{url}')

        if len(data) < postSetMaxLen:
            break
#─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
#=============================================================================================================================
#─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def printTotals(totalsDict): #Prints table after the pushshift log.
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


    maxRecentPosts = 10
    posts = postrun.postRunJson(os.path.join(totalsDict['dir'], 'all_posts.json'), maxRecentPosts)

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
    print()
#─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
#=============================================================================================================================
#─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def run(user, options):
    start = time.time()
    console = Console()

    userDir = Path.cwd() / 'users' / user
    userDir.mkdir(parents=True, exist_ok=True)

    console.print(f'[bold blue]\nGathering and formatting data from pushshift for {user}.\n')

    if '-pics' in options:
        keyType = {'submission': ('url', 'created_utc',)}
        images = redtil.imageUrls(user, [i for i in getPosts(user, 'submission')])

        images = set(open(os.path.join(userDir,'images.txt')).read().splitlines())
        imageStatus = '\n'.join([f'[red]{i+1}\t[magenta]{image}' for i, image in enumerate(images)])
        imageSubmissionLog = f'[bold blue]\nImages submitted by {user}\n{imageStatus}'
        console.print(imageSubmissionLog)

        if '-d' in options:
            print()
            redtil.imagesdl(images, userDir)


        fnamesStr = '\n\t' + '\n\t'.join([i for i in os.listdir(userDir)])
        console.print(f'\n[bold cyan]{userDir}{fnamesStr}')
        console.print(f'\n[bold blue]Run time - {round(time.time() - start, 1)} s\n')


    else:
        allPosts = {'comments': [i for i in getPosts(user, 'comment')],
                    'submissions': [i for i in getPosts(user, 'submission')]}

        postCounts = redtil.countPosts(allPosts)
        redtil.writeFiles(allPosts, postCounts, user, userDir)

        totalsDict = {'postCounts': postCounts,
                      'commentsLen': str( len(allPosts['comments']) ),
                      'submissionsLen': str( len(allPosts['submissions']) ),
                      'dir': str(userDir),
                      'start': start,
                      'end': time.time(),
                      'user':user}


        printTotals(totalsDict)
#─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
#=============================================================================================================================
#─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
if __name__ == '__main__':  # System arguments. CHANGE TO ARGPARSER

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
