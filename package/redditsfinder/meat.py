#!/usr/bin/env python3

'''
              _     _ _ _        __ _           _
 _ __ ___  __| | __| (_) |_ ___ / _(_)_ __   __| | ___ _ __
| '__/ _ \/ _` |/ _` | | __/ __| |_| | '_ \ / _` |/ _ \ '__|
| | |  __/ (_| | (_| | | |_\__ \  _| | | | | (_| |  __/ |
|_|  \___|\__,_|\__,_|_|\__|___/_| |_|_| |_|\__,_|\___|_|


github.com/fitzy1293/redditsfinder


TO DO:
    - Add more optional args.
    - Instead of using a set to identify pictures:
        - name_com_extension
            -What if invalid extension?
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
import argparse


from rich.table import Table,Column
from rich.console import Console

from .redditsfinder_utils import *
from .after_run_parsing import *
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
            interestingPostData['body'] = humanReadablePost(postData['body'])
        if 'permalink' in postData.keys():
            interestingPostData['permalink'] = f'https://www.reddit.com{postData["permalink"]}'

    if postType == 'submission':
        if 'selftext' in postData.keys():
            interestingPostData['selftext'] = humanReadablePost(postData['selftext'])
        if 'url' in postData.keys():
            interestingPostData['url'] = postData["url"]
        if 'full_link' in postData.keys():
            interestingPostData['full_link'] = postData["full_link"]

    return interestingPostData
#─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
#=============================================================================================================================
#─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def getPosts(user, postType): # Pushshift API requests in chunks of 100
    console = Console()
    console.print(f'[bold blue underline]{postType[0].upper()}{postType[1:]} request log:')

    apiUrl = 'https://api.pushshift.io/reddit/search/'
    postSetMaxLen = 100 # Max num of posts in each pushshift request, seems to be 100 right now or it breaks.

    before = int(round(time.time()))
    beginTime = before
    allPosts = {}

    if postType == 'comment':
        highlight = '[cyan]'
    else:
        highlight = '[magenta]'

    ct = 0

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

        ct = ct + len(data)
        console.print(f'[bold green]\t{ct} {highlight}{url}')

        if len(data) < postSetMaxLen:
            break
#─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
#=============================================================================================================================
#─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def printTotals(tablesDict): #Prints table after the pushshift log.
    print('\n\n')
    console = Console()

    header = [
            '',
            'Recent comments:\nsubmission ID\ncomment ID',
            'Recent submissions:\nsubmission ID',
            'Comments count:\nfor each sub',
            f'[bold red]{tablesDict["commentsLen"]}[/bold red]',
            'Submissions count:\nfor each sub',
            f'[bold red]{tablesDict["submissionsLen"]}[/bold red]'#,
            #tablesDict["dir"],
            #'Run Time'
    ]

    console.log(f'[magenta]{tablesDict["user"]}')

    table = Table(show_header=True,header_style="bold blue")

    for i in header:
        table.add_column(i, justify='left')

    commentsColumn = '\n'.join([sub[0] for sub in tablesDict['postCounts']['comments']])
    commentsCt = '\n'.join([f'[bold red]{sub[1]}[/bold red]' for sub in tablesDict['postCounts']['comments']])

    submissionsColumn = '\n'.join([sub[0] for sub in tablesDict['postCounts']['submissions']])
    submissionsCt = '\n'.join([f'[bold red]{sub[1]}[/bold red]' for sub in tablesDict['postCounts']['submissions']])

    maxRecentPosts = 50
    posts = postRunJson(os.path.join(tablesDict['dir'], 'all_posts.json'), maxRecentPosts)

    #Numbers the columns
    columnLengths = max (i.count('\n') for i in [posts[0],posts[1], commentsColumn, submissionsColumn]) + 1
    columnNums = '\n'.join([str(i) for i in range(columnLengths)])
    print(columnLengths)


    rows = [
            columnNums,
            posts[0],
            posts[1],
            f'[purple]{commentsColumn}[/purple]',
            commentsCt,
            f'[purple]{submissionsColumn}[/purple]',
            submissionsCt,
            '[magenta underline]all_posts.json\nsubreddit_count.txt',
            f'[magenta underline]{round(tablesDict["end"] - tablesDict["start"], 1)} s'
    ]


    table.add_row(
    rows[0], rows[1], rows[2], rows[3], rows[4], rows[5], rows[6]#, rows[7], rows[8]
    )

    console.print(table, justify='center', style='bold white')
    print()
#─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
#=============================================================================================================================
#─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def run(args, user):
    start = time.time()
    console = Console()

    userDir = Path.cwd() / 'users' / user
    userDir.mkdir(parents=True, exist_ok=True)

    console.print(f'[bold blue]\nGathering and formatting data from pushshift for {user}.\n')

    if  '-pics' in args:
        keyType = {'submission': ('url', 'created_utc',)}
        images = imageUrls(user, [i for i in getPosts(user, 'submission')])

        images = set(open(os.path.join(userDir,'images.txt')).read().splitlines())
        imageStatus = '\n'.join([f'\t[bold green]{i+1} [cyan]{image}' for i, image in enumerate(images)])
        imageSubmissionLog = f'[bold blue underline]\nImages submitted by {user}:[/bold blue underline]\n{imageStatus}'
        console.print(imageSubmissionLog)

        if '-d' in args or '--download' in args:
            print()
            imagesdl(images, userDir)

    else:
        allPosts = {'comments': [i for i in getPosts(user, 'comment')],
                    'submissions': [i for i in getPosts(user, 'submission')]}
        postCounts = countPosts(allPosts)
        writeFiles(allPosts, postCounts, user, userDir)

        if not '-q' in args and not '--quiet' in args:
            tablesDict = {'postCounts': postCounts,
                          'commentsLen': str(len(allPosts['comments'])),
                          'submissionsLen': str(len(allPosts['submissions'])),
                          'dir': str(userDir),
                          'start': start,
                          'end': time.time(),
                          'user': user}
            printTotals(tablesDict)


    if not '-q' in args and not '--quiet' in args:
        fnamesStr = '\n\t' + '\n\t'.join([i for i in os.listdir(userDir)])
        console.print(f'\n[bold cyan underline]{userDir}{fnamesStr}')
        console.print(f'\n[bold blue]Run time - {round(time.time() - start, 1)} s\n')
#─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
#=============================================================================================================================
#─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def main():  # System arguments

    if len(sys.argv) == 1:
        print('''Running redditsfinder

        Test it on yourself to make sure it works.

        redditsfinder yourusername

        Basic usage

        redditsfinder username
        redditsfinder [options] username_0 username_1 username_2 ...

        With a file

        -f or --file
        redditsfinder [options] -f line_separated_text_file.txt

        Optional args

        -pics returns URLs of image uploads.
        -pics -d or -pics --download downloads them.
        -q or --quiet turns off non log related print statements.''' )


    else:
        redditsfinderArgs = sys.argv[1:]
        optionalArgs = ('-pics', '-d', '--download', '-q', '--quiet', '-f', '--file')
        enteredOptionalArgs = [i for i in redditsfinderArgs if i in optionalArgs]

        if '-f' in enteredOptionalArgs:
            usernames = open(sys.argv[-1]).read().splitlines()
        else:
            usernames = [i for i in redditsfinderArgs if i not in optionalArgs]

        print(f'Optional arguments: {enteredOptionalArgs}')
        print('Usernames: '), pprint(usernames)

        for user in usernames:
            run(enteredOptionalArgs, user)
