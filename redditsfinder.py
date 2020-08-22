#!/usr/bin/python3

'''
github.com/fitzy1293/redditsfinder
The README.md is helpful

'''

import urllib.request, requests
import json
import time
import os,sys
from pprint import pprint
from urllib.error import HTTPError
from datetime import datetime
import imghdr
from zipfile import ZipFile

import redditcleaner #Not in standard lib.

#─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
#=============================================================================================================================
#─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def humanReadablePost(redditRawText): # Makes body and selftext not an abomination.
    # Makes reddit's text formatting readable
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

    # 1D list with each item containing a max of 15 words.
    return [' '.join(cleanPost) for cleanPost in splitWords]
#─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
#=============================================================================================================================
#─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def getPosts(user, keyType, picFlag): # Uses pushshift API. Functions kind of a mess but works.

    apiUrl = 'https://api.pushshift.io/reddit/search/'
    # Max num of posts in each pushshift request, seems to be 100 right now or it breaks.
    postSetMaxLen = 100

    # Subtract off last amp in set, put in pushshift url.
    before = int(round(time.time()))
    beginTime = before  # To reset time to original value after comments.
    allPosts = {}


    if picFlag:
        correctPostType = ['submission']
    else:
        correctPostType = ['comment', 'submission']


    for postType in correctPostType:

        print(f'{postType[0].upper()}{postType[1:]} request log:')

        ct = 0
        posts = []
        while True:  # We need to wait until we've collected all posts then break.
            time.sleep(.75)  # Avoids rate limits.
            url = f'{apiUrl}{postType}/?author={user}&size={postSetMaxLen}&before={before}'
            try:
                response = urllib.request.urlopen(url)
                data = json.loads(response.read())['data']

                for post in data:
                    # Relevant keys for either a comment or submission.
                    ourKeys = keyType[postType]


                    postDict = dict.fromkeys(ourKeys, None)

                    for key in ourKeys:  # We are doing things for specific keys, so we need another loop.
                        if key in ourKeys and key in post.keys():  # To only use the keys we need.
                            outputValue = post[key]

                            # Thanks redditcleaner making this less painful.
                            if key == 'body' or key == 'selftext':
                                outputValue = humanReadablePost(outputValue)


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
                print(f'\t{ct} {url}')

                if len(data) < postSetMaxLen:  # Get 100 posts at a time they switched from 1000?
                    allPosts[postType + 's'] = posts

                    break

            except HTTPError:  # The sleep .75 deals with this.
                print('Rate limited')

        # before has been decreasing and we don't want it to start at the last comment for the beggining of submissions.
        before = beginTime
        print()

    if picFlag:
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
        postCounts[f'Sorted {postType}:'] = sortedCounts

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
def makeBox(list): #Takes 1 d list of strings, returns str in a box that fits.
    fixedTabsList = [i.replace('\t', '    ') for i in list]
    longestStr = list.count('\t')  + len(max(fixedTabsList, key=len))

    box = str('─') * (longestStr) #Box drawing char, not dash.
    boxedStr = '\n'.join([f'│{i}{ str(" " * (longestStr - len(i))) }│' for i in fixedTabsList])

    return f'┌{box}┐\n{boxedStr}\n└{box}┘' #(U+2518) and (U+2510) box drawing chars respecitvely.
#─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
#=============================================================================================================================
#─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def printTotals(totalsDict): #Printed stuff after the pushshift log.
    for k, v in totalsDict['postCounts'].items():
        postTypeList = [k]
        for subreddit in v:

            new = f'\t{subreddit[0]} {subreddit[1]}'
            postTypeList.append(new)

        print(makeBox(postTypeList))

    #Box containing # of comments/submissions, dir and path of files, and run time.
    comments = f'Comments\t= {totalsDict["commentsLenPrint"]}'
    submissions = f'Submissions = {totalsDict["submissionsLenPrint"]}'
    dir = totalsDict['dir']
    allPosts = f'\tall_posts.json'
    sortedSubreddits = f'\tsorted_subreddits.txt'  # Could probably use a better filename.
    runTime = f'Run time - {round(totalsDict["end"] - totalsDict["start"], 1)} s'


    infoToBox = [comments, submissions, '', dir, allPosts, sortedSubreddits, '', runTime]

    print(makeBox(infoToBox))
#─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
#=============================================================================================================================
#─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def imagesdl(images, userDir):
    for i, url in enumerate(images):
        try:
            #if i!= 18: continue
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
            dlLog = f'Downloaded {os.path.split(imagePath)[-1]}{" " * 4}{url}'
            print(dlLog)

            try:
                bytes = open(imagePath,'rb').read().decode()[1:9]
                if type(bytes) == str and  bytes[0:2] == 'PK':
                    continue

                else:
                    print(f'Invalid image link - removing {os.path.split(imagePath)[-1]}{" " * 4}')
                    os.remove(imagePath)
                    continue
            except UnicodeDecodeError as e:
                pass

            try:
                with ZipFile(imagePath, 'r') as zipObj:
                    listOfiles = zipObj.namelist()

            except Exception as e:
                if urlType == 'image':
                    continue

                imghdrExtension = imghdr.what(imagePath)
                if str(imghdrExtension) == 'None':
                    imghdrExtension = 'jpeg'

                newFname = f'{i+1}.{imghdrExtension}'

                newFpath = os.path.join(userDir, newFname)
                os.rename(imagePath, newFpath)

                logSplit = dlLog.split(' ')
                logSplit[1] = f'{i+1}.{imghdrExtension}'

                changeExtension = str(i+1) + '.zip => ' + newFname

                spaces = len(logSplit[0] + logSplit[1]) - len(changeExtension) + 4
                print(f'{changeExtension}{" " * spaces}{e}')

        except Exception as e:
            print(f'Unexpected exception: {e}')
#─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
#=============================================================================================================================
#─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def run(user, options):
    start = time.time()

    usersDir = os.path.join(os.getcwd(), 'users')
    userDir = os.path.join(usersDir, user)  # Contains files for username.
    for dir in (usersDir, userDir):
        if not os.path.exists(dir):
            os.mkdir(dir)


    print(f'Gathering and formatting data from pushshift for {user}.\n')

    if '-pics' in options:
        keyType = {'submission': ('url', 'created_utc',)}
        images = getPosts(user, keyType, True)

        images = open( os.path.join(userDir,'images.txt')).read().splitlines()
        images = set(images)
        boxedImages = [f'Images submitted by {user}'] + [f'{i+1}\t{image}' for i, image in enumerate(images)]
        print(makeBox(boxedImages))

        if '-d' in options:
            print()
            imagesdl(images, userDir)

        print(f'\nRun time - {round(time.time() - start, 1)} s')

    else:
        keyType = {'comment': ('id', 'created_utc', 'subreddit', 'body', 'score', 'permalink', 'link_id', 'parent_id'),
                   'submission': ('id', 'created_utc', 'subreddit', 'selftext', 'score', 'full_link', 'url')}

        allPosts = getPosts(user, keyType, False)
        postCounts = countPosts(allPosts)
        writeFiles(allPosts, postCounts, user, userDir)

        totalsDict = {'postCounts': postCounts,
                      'commentsLenPrint': str( len(allPosts['comments']) ),
                      'submissionsLenPrint': str( len(allPosts['submissions']) ),
                      'dir': userDir,
                      'start': start,
                      'end': time.time()}

        printTotals(totalsDict)
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
