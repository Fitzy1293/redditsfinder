import redditcleaner #Not in standard lib.
import requests
import traceback
import os,sys
import imghdr
from zipfile import ZipFile
import json
from pprint import pprint
from pathlib import Path
from rich.table import Table,Column
from rich.console import Console

def humanReadablePost(redditRawText): # Makes body and selftext not an abomination.
    cleaned = redditcleaner.clean(redditRawText).split()

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
#─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
#=============================================================================================================================
#─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def countPosts(allPosts):  # Count and order most posted subs.
    postCounts = {}
    for postType, posts in allPosts.items():
        subreddits = [post['subreddit'] for post in posts]
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
