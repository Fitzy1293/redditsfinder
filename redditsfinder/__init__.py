#!/usr/bin/env python3

'''
              _     _ _ _        __ _           _
 _ __ ___  __| | __| (_) |_ ___ / _(_)_ __   __| | ___ _ __
| '__/ _ \/ _` |/ _` | | __/ __| |_| | '_ \ / _` |/ _ \ '__|
| | |  __/ (_| | (_| | | |_\__ \  _| | | | | (_| |  __/ |
|_|  \___|\__,_|\__,_|_|\__|___/_| |_|_| |_|\__,_|\___|_|


github.com/fitzy1293/redditsfinder


TO DO:
    - Make the module useful when imported
'''

#import urllib.request
import requests
import json
import time
import os,sys
#from urllib.error import HTTPError
from pathlib import Path

from rich.table import Table,Column
from rich.console import Console

from .redditsfinder_utils import *

CONSOLE = Console()

#─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
#=============================================================================================================================
#─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def getPosts(user, postType, printIt=True): # Pushshift API requests in chunks of 100
    console = Console()
    if printIt:
        console.print(f'[bold blue underline]{postType[0].upper()}{postType[1:]} request log:')

    postSetMaxLen = 100 # Max num of posts in each pushshift request, seems to be 100 right now or it breaks.

    return pushshift(None, postType, postSetMaxLen, user=user, log=printIt)
#─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
#=============================================================================================================================
#─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def printTotals(dataForTable, maxRecentPosts=50, printIt=True): #Prints table after the pushshift log.

    header = (
                'line #\n',
                'subreddit\n',
                'karma\n',
                'comment\ncount',
                'comment\nkarma',
                'submission\ncount',
                'submission\nkarma'
    )

    table = Table(show_header=True,header_style="bold blue")

    for colTitle in header:
        table.add_column(colTitle, justify='left')


    for i, subredditDictObject in enumerate(dataForTable):
        subTitle = subredditDictObject.get('sub')
        subKarma = subredditDictObject.get('karma')
        commentInfo, submissionInfo  = subredditDictObject.get('submission,comment') #(comment data, submission data)


        table.add_row(
                        f'[bold red]{str(i+1)}[/bold red]',
                        f'[bold magenta underline]{subTitle}[/bold magenta underline]',
                        f'[bold magenta underline]{subKarma}[/bold magenta underline]',
                        f'[bold cyan underline]{commentInfo[0]} [/bold cyan underline]',
                        f'[bold cyan]{commentInfo[1]}[/bold cyan]',
                        f'[bold green underline]{submissionInfo[0]} [/bold green underline]',
                        f'[bold green]{submissionInfo[1]}[/bold green]'
        )

    CONSOLE.print(table, justify='center')

#─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
#=============================================================================================================================
#─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def run(cliArgs, user='', printIt=True, **kwargs):
    start = time.time()
    console = Console()

    if kwargs:
        cliArgs = ['--' + i for i in kwargs.keys()]

    if 'user' in kwargs.keys():
        user = kwargs['user']

    if printIt:
        console.print(f'[bold blue]Gathering and formatting data from pushshift for {user}.\n')

    if  '-pics' in cliArgs or '--pics' in cliArgs:
        keyType = {'submission': ('url', 'created_utc',)}
        images                 = imageUrls(user, [i for i in getPosts(user, 'submission', printIt=printIt)])

        if printIt:
            imageStatus        = ''.join([f'\t[bold green]{i+1} [cyan]{image}\n' for i, image in enumerate(images)])
            imageSubmissionLog = f'[bold blue underline]\nImages submitted by {user}:[/bold blue underline]\n{imageStatus}'
            console.print(imageSubmissionLog)

        if '-d' in cliArgs or '--download' in cliArgs:
            imagesdl(images, os.path.join(os.getcwd(), 'users', user))
            print()

    else:
        allPosts = {'comments': [i for i in getPosts(user, 'comment', printIt=printIt)],
                    'submissions': [i for i in getPosts(user, 'submission', printIt=printIt)]}
        numericInfoBySub = countPosts(allPosts)

        if printIt:
            print()
            printTotals(numericInfoBySub)
            print()
        if '--write' or '-w' in cliArgs:
            userDir = Path.cwd() / 'users' / user
            userDir.mkdir(parents=True, exist_ok=True)
            writeFiles(allPosts, numericInfoBySub, user, userDir)

            if printIt:
                fnamesStr = '\n\t' + '\n\t'.join([i for i in os.listdir(userDir)])
                console.print(f'\n[bold cyan underline]{userDir}{fnamesStr}')

    if printIt:
        console.print(f'[bold blue]Run time - {round(time.time() - start, 1)} (s)[/bold blue]\n[bold cyan]{"-"*50}[/bold cyan]')

#─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
#=============================================================================================================================
#─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def main():  # System arguments

    if len(sys.argv) == 1:
        print(f'''Running redditsfinder
{'-' * 21}
    Test it on yourself to make sure it works.
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
            -quiet or -q turns off printing''' )


    else:
        redditsfinderArgs = sys.argv[1:]
        optionalArgs = {'--write', '-w', '-pics', '--pics', '-d', '--download', '-q', '--quiet', '-f', '--file'}
        enteredOptionalArgs = set([i for i in redditsfinderArgs if i in optionalArgs])

        if '-f' in enteredOptionalArgs:
            if sys.argv[-1] in os.path.exists():
                with open(sys.argv[-1]) as f:
                    usernames = f.read().splitlines()
            else:
                sys.exit(f'error: {sys.argv[-1]} not found')
        else:
            usernames = [i for i in redditsfinderArgs if i not in optionalArgs]

        usersCt = len(usernames)

        if not '-q' in enteredOptionalArgs and not '--quiet' in enteredOptionalArgs:
            printIt = True
        else:
            printIt=False

        if usersCt > 1 and printIt:
            print('\nnote: this is not done in parallel, an account like automoderator with millions of posts will be blocking\n')

        for user in usernames:
            run(enteredOptionalArgs, user=user, printIt=printIt)

if __name__ == '__main__':
    main()
