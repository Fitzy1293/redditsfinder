import time
import requests
import traceback
import os,sys
import imghdr
from datetime import datetime

from zipfile import ZipFile
import json
from pprint import pprint
from pathlib import Path
from rich.table import Table,Column
from rich.console import Console

#─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
#=============================================================================================================================
#─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def cleanupPostData(postData, postType): #Thanks /u/kwelzel for helping me refactor!
    interestingPostData = {}
    submissionAndCommentKeys = ('id', 'created_utc', 'subreddit', 'score', 'link_id', 'parent_id')

    for i in submissionAndCommentKeys:
        if not i in postData.keys():
            interestingPostData[i] = None

        else:
            interestingPostData[i] = postData[i]

    timestamp = int(postData['created_utc'])
    interestingPostData['datetime'] = str(datetime.utcfromtimestamp(timestamp).strftime('%a %b %d %Y, %I:%M %p UTC'))

    if postType == 'comment':
        if 'permalink' in postData.keys():
            interestingPostData['permalink'] = f'https://www.reddit.com{postData["permalink"]}'
        else:
            interestingPostData['permalink'] = None
        if 'body' in postData.keys():
            interestingPostData['body'] = textPostWords(postData['body'])
        else:
            interestingPostData['body'] = None

    if postType == 'submission':
        if 'url' in postData.keys():
            interestingPostData['url'] = postData["url"]
        else:
            interestingPostData['url'] = None
        if 'full_link' in postData.keys():
            interestingPostData['full_link'] = postData["full_link"]
        else:
            interestingPostData['full_link'] = None
        if 'selftext' in postData.keys():
            interestingPostData['selftext'] = textPostWords(postData['selftext'])
        else:
            interestingPostData['selftext'] = None

    return interestingPostData
#─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
#=============================================================================================================================
#─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def pushshift(lim, postType, postSetMaxLen, user='', log=False): #Pushshift requests
    console = Console()
    before = int(round(time.time()))

    if postType == 'comment':
        highlight = '[cyan]'
    else:
        highlight = '[magenta]'

    ct = 0

    while True:

        if lim is not None:
            if ct >= lim:
                break

        apiUrl = 'https://api.pushshift.io/reddit/search/'
        url = f'{apiUrl}{postType}/?author={user}&size={postSetMaxLen}&before={before}'

        response = requests.get(apiUrl + postType, params={'author': user, 'size': postSetMaxLen, 'before': before})
        data = response.json()['data']
        if not data:
            break

        for postData in data:
            before = postData['created_utc']
            yield postData

        ct += len(data)

        if log:
            console.print(f'[bold green]\t{ct} {highlight}{url}')

        if len(data) < postSetMaxLen:
            break

        time.sleep(.75) # rate limiting, pushshift says too bad if you go to quick
#─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
#=============================================================================================================================
#─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def comments(lim=None, user='', log=False):
    postSetMaxLen = 100
    comment = [i for i in pushshift(lim, 'comment', postSetMaxLen, user=user, log=log)]
    return comment[:lim]
#─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
#=============================================================================================================================
#─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def submissions(lim=None, user='', log=False):
    postSetMaxLen = 100
    submission = [i for i in pushshift(lim, 'submission', postSetMaxLen, user=user, log=log)]
    return submission[:lim]
#─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
#=============================================================================================================================
#─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def countPosts(allPosts):  # Count and order most posted subs.

    '''
    Formats data for the table.
    '''
    postSubredditKarmaStrings = []


    commentSubList = [] # To turn into a set
    for i, comment in enumerate(allPosts.get('comments')):
        urlFromIds = f'reddit.com/comments/{comment.get("link_id")[3:]}//{comment.get("id")}'
        sub = comment.get("subreddit")#.lower()
        karma = comment.get("score")
        subKarmaStr = f'{sub}-c-{karma}|{urlFromIds}'

        commentSubList.append(sub)
        postSubredditKarmaStrings.append(subKarmaStr)

    submissionSubList = [] # To turn into a set
    for submission in allPosts.get('submissions'):
        urlFromIds = f'reddit.com/{submission.get("id")}'
        sub = submission.get("subreddit")#.lower()
        karma = submission.get("score")
        subKarmaStr = f'{sub}-s-{karma}|{urlFromIds}'

        submissionSubList.append(sub)
        postSubredditKarmaStrings.append(subKarmaStr)

    postSubredditSet = set(commentSubList) | set(submissionSubList)


    returnList = []
    for uniqSub in sorted(postSubredditSet):
        commentsKarmaTotal = 0
        submissionsKarmaTotal = 0
        postTypeStartIndex = len(uniqSub) + 1
        countPostsList = []
        for post in postSubredditKarmaStrings:
            if post.startswith(f'{uniqSub}-'):

                typePipeKarmaStr = post[postTypeStartIndex:post.find('|')]
                countablePostTypeChar = typePipeKarmaStr[0]

                if countablePostTypeChar == 'c':
                    commentsKarmaTotal += int(typePipeKarmaStr[2:])
                elif countablePostTypeChar == 's':
                    submissionsKarmaTotal+= int(typePipeKarmaStr[2:])



                countPostsList.append(countablePostTypeChar)

        totalKarma    = commentsKarmaTotal + submissionsKarmaTotal
        commentsCt    = countPostsList.count('c')
        submissionsCt = countPostsList.count('s')
        info          = ( (str(commentsCt), str(commentsKarmaTotal)), (str(submissionsCt), str(submissionsKarmaTotal)) )

        returnList.append({'sub': uniqSub, 'karma': totalKarma, 'submission,comment': info})


    sortedByKarmaThenName = sorted(returnList, key = lambda i: (i['karma'], i['sub']), reverse=True)

    return sortedByKarmaThenName
#─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
#=============================================================================================================================
#─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def writeFiles(allPosts, subredditInfo, user, userDir):
    if len(allPosts) != 0:
        jPath = os.path.join(userDir, 'posts.json')
        with open(jPath, 'w+', newline='\n') as jsonFile:
            json.dump(allPosts, jsonFile, indent=4)

        tPath = os.path.join(userDir, 'count.json')
        with open(tPath, 'w+') as subredditsFile:
            json.dump(subredditInfo, subredditsFile, indent=4)
#─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
#=============================================================================================================================
#─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def imageUrls(user, submissions):
    urls = [v for i in submissions  for k,v in i.items() if k == 'url']
    imageUrls = []
    for url in urls:
        if url.endswith(('.png', '.PNG', '.jpg', '.JPG', 'jpeg', 'JPEG' '.gif', '.GIF')):
            imageUrls.append(url)
            continue

        if '://reddit.com' in url:
            continue
        elif 'imgur.com' in url:
            if '/a/' in url:
                imageUrls.append(url + '/zip')
            else:
                imageUrls.append(url + '.jpg')
    return imageUrls

#─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
#=============================================================================================================================
#─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def imagesdl(images, userDir): # Needs to deal with all the nonsense involved with image formatting
    console = Console()

    if not os.path.exists('users'):
        os.mkdir('users')
    if not os.path.exists(userDir):
        os.mkdir(userDir)

    for i, url in enumerate(images):
        try:

            if url.endswith(('.png', '.PNG', '.jpg', '.JPG', '.gif', '.GIF')) and not 'imgur.com' in url:
                urlType = 'image'
                fname = url.rstrip("/").split("/")[-1].replace('?', '-')
                imagePath = os.path.join(userDir, f'{fname}')
                response = requests.get(url, stream=True)
                status_code = response.status_code
                if status_code != 200:
                    console.print(f'\t[bold red]{status_code}\t{i+1} bad response {url}')
                    continue

            else:
                #url = url.replace('.gifv.', '.')
                status_code_imgur = requests.get(url)
                status_code = status_code_imgur.status_code
                if  status_code != 200 and not url.endswith('.gifv.jpg'):
                    console.print(f'\t[bold red]{status_code}\t{i+1} bad response {url}')
                    continue

                if url.startswith('https://imgur.com') or url.startswith('https://i.imgur.com'):
                    if url.endswith('.gifv.jpg'):
                        url = url.replace('.gifv.jpg', '.mp4')
                        response = requests.get(url, stream=True)
                        imagePath = os.path.join(userDir, url.split('/')[-1])
                    elif not url.endswith('/zip'): # jpgs, pngs
                        response = requests.get(url, stream=True)
                        imagePath = os.path.join(userDir, url.split('/')[-1])

                    else: # zips
                        url = url.rstrip('/').rstrip('/zip')
                        urlType   = 'zip'
                        get_real_url_response  = requests.get(url)


                        html_from_fake_response = get_real_url_response.text
                        real_url = html_from_fake_response.split('<meta property="og:image"')[1]
                        final_real_url = real_url[real_url.find('https://'):real_url.find('">')]

                        if '?' in final_real_url:
                            actual_final_url = final_real_url.split('?')[0]
                        else:
                            actual_final_url = final_real_url

                        response = requests.get(actual_final_url, stream=True)
                        imagePath = os.path.join(userDir, actual_final_url.rstrip('/').split('/')[-1])

            if not os.path.exists(imagePath):
                with open(imagePath, 'wb') as f:
                    f.write(response.content)

                dlLog = f'{i+1} {os.path.split(imagePath)[-1]} - Downloaded: {url}'
                console.print(f'\t[green]{status_code}\t{dlLog}[/green]')

            elif os.path.exists(imagePath):
                dlLog = f'{i+1} {os.path.split(imagePath)[-1]} - Already Downloaded: {url}'
                console.print(f'\t[green]{status_code}[/green]\t[yellow]{dlLog}')


        except Exception as e: # don't do this...
            console.print(f'\t{status_code}[bold red]\t{i+1} {url} unexpected exception\n\t{e}')
