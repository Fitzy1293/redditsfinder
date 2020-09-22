import json
import traceback
from pprint import pprint
from rich.table import Table,Column
from rich.console import Console

def shortenUrl(postType, postObjectsList, maxPrint): #Shortens URLs and formats for console.print()
    consolePrintableStr = ''

    if postType == 'comments':
        highlight = '[cyan]'
        pushshiftUrlAttribute = 'permalink'
    else:
        highlight = '[magenta]'
        pushshiftUrlAttribute = 'full_link'

    urlsCol = []
    for i, post in enumerate(postObjectsList):
        if i == maxPrint:
            break

        try:
            if post[pushshiftUrlAttribute] is None:
                continue

            repUrl = post[pushshiftUrlAttribute].replace('https://www.reddit.com', '')
            repUrl = repUrl.replace('/r/', '', 1).split('/')

            subreddit = f'[#4287f5]{repUrl[0]}[/#4287f5]'
            comments = f'[bold green]{repUrl[1]}[/bold green]'
            submissionID = f'[bold red]{repUrl[2]}[/bold red]'
            commentID = f'[bold green]{repUrl[4]}[/bold green]'


            necessaryInfoToFindPost = [submissionID, commentID]

            if postType == 'comments':
                urlShort = f'{necessaryInfoToFindPost[0]} {necessaryInfoToFindPost[1]}'
            else:
                urlShort = necessaryInfoToFindPost[0]

            urlsCol.append(urlShort)

            consolePrintableStr = '\n'.join(urlsCol)

        except Exception as e:
            print(traceback.format_exc())

    return consolePrintableStr

def postRunJson(jsonPath, maxPrint):
    with open(jsonPath) as f:
        data = json.load(f)

    return [shortenUrl(k, data[k], maxPrint) for k in data.keys()]
