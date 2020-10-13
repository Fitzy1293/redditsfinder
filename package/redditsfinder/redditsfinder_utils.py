import redditcleaner #Not in standard lib.
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
            yield cleanupPostData(postData, postType)

        ct += len(data)

        if log:
            console.print(f'[bold green]\t{ct} {highlight}{url}')

        if len(data) < postSetMaxLen:
            break

        time.sleep(.75)
#─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
#=============================================================================================================================
#─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def countRequests(lim, postSetMaxLen):
    postSetMaxLen = 100
    numOfRequests = lim // postSetMaxLen
    if lim % postSetMaxLen != 0:
        remainingPosts = lim % postSetMaxLen
        numOfRequests +=1

    return numOfRequests
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
def textPostWords(redditRawText): # Makes body and selftext not an abomination.
    return redditcleaner.clean(redditRawText).split()
    '''
    # Spliting post string into sets of 15 words so the output is readable when it reaches it's place within json.
    splitWords = []
    temp = []
    for i, word in enumerate(cleaned):
        temp.append(word)
        if i % 15 == 0 and i != 0:
            splitWords.append(temp)
            temp = []

    # Another way of saying if the number of totalW words % 15 != 0. Need to put the leftover words where they belong
    if len(temp) != 0:
        splitWords.append(temp)

    return [' '.join(cleanPost) for cleanPost in splitWords]
    '''
#─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
#=============================================================================================================================
#─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def countPosts(allPosts):  # Count and order most posted subs.
    postCounts = {}
    for postType, posts in allPosts.items():
        subreddits = [post['subreddit'] for post in posts if 'subreddit' in post.keys()]
        subredditSet = set(subreddits)

        counts = []
        for subreddit in subredditSet:
            if subreddit is not None:
                counts.append([subreddit,subreddits.count(subreddit)])

        #Sort by number of posts user has in each sub that they have posted in.
        sortedCounts = sorted(counts, key=lambda subredditPostCount: (subredditPostCount[1], subredditPostCount[0]), reverse=True)
        postCounts[postType] = sortedCounts

    return postCounts
#─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
#=============================================================================================================================
#─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def writeFiles(allPosts, postCounts, user, userDir):
    if len(allPosts) != 0:
        jPath = os.path.join(userDir, 'all_posts.json')
        with open(jPath, 'w+', newline='\n') as f:
            json.dump(allPosts, f, indent=4)

        tPath = os.path.join(userDir, 'subreddit_count.txt')
        with open(tPath, 'w+') as g:
            for k, v in postCounts.items():
                g.write(f'{k}\n')
                for i in v:
                    g.write(f'{i[0]}, {str(i[1])}\n')

#─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
#=============================================================================================================================
#─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def imageUrls(user, submissions):
    urls = [v for i in submissions  for k,v in i.items() if k == 'url']
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
    userDir = Path.cwd() / 'users' / user
    images = os.path.join(str(userDir), 'images.txt')
    with open(images, 'w+') as f:
        f.write(imageUrlsStr+ '\n')
    return imageUrlsStr
#─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
#=============================================================================================================================
#─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def imagesdl(images, userDir): #Needs to deal with all the nonsense involved with image formatting
    console = Console()
    for i, url in enumerate(images):
        try:
            response = requests.get(url, stream=True)

            if url.endswith(('.png', '.PNG', '.jpg', '.JPG', '.gif', '.GIF')):
                urlType = 'image'
                fileType = f'{url.split(".")[-1]}'
                imagePath = os.path.join(userDir, f'{str(i+1)}.{fileType}')

            else:
                urlType = 'zip'
                fileType = 'urlType'
                imagePath = os.path.join(userDir, f'{i+1}.zip')

            with open(imagePath, 'wb+') as f:
                f.write(response.content)

            dlLog = f'\t{os.path.split(imagePath)[-1]} - Downloaded: {url}'
            console.print(f'[green]{dlLog}')

            try:
                bytes = open(imagePath,'rb').read().decode()[1:9]
                if type(bytes) == str and  bytes[0:2] == 'PK': #A zip file
                    continue

                else:
                    console.print(f'[bold red]Invalid image link - removing {os.path.split(imagePath)[-1]}{" " * 4}')
                    os.remove(imagePath)
                    continue
            except UnicodeDecodeError as e:
                pass

            changedFlag = False
            imghdrExtension = imghdr.what(imagePath)
            if str(imghdrExtension) == 'None':
                imghdrExtension = 'jpeg'
                changedFlag = True

            if urlType == 'image' and not changedFlag:
                newFname = f'{i+1}.{imghdrExtension}'

                newFpath = os.path.join(userDir, newFname)
                os.rename(imagePath, newFpath)

            try:
                with ZipFile(imagePath, 'r') as zipObj:
                    listOfiles = zipObj.namelist()

            except Exception as e:
                if urlType == 'image':
                    continue

                newFname = f'{i+1}.{imghdrExtension}'

                newFpath = os.path.join(userDir, newFname)
                os.rename(imagePath, newFpath)

                logSplit = dlLog.split(' ')
                logSplit[1] = f'{i+1}.{imghdrExtension}'

                changeExtension = str(i+1) + '.zip => ' + newFname

                spaces = len(logSplit[0] + logSplit[1]) - len(changeExtension) + 4
                console.print(f'[bold blue]{changeExtension}{" " * spaces}{e}')

        except Exception as e:
            console.print(f'[bold red]{i} {url} unexpected exception: {traceback.format_exc()}')
