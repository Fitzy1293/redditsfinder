import urllib.request
import json
import time
import os
from pprint import pprint
import sys
from urllib.error import HTTPError
from json2html import *


def getPosts(user):

    apiUrl = 'https://api.pushshift.io/reddit/search/'

    #Pushshift attributes I thought were useful.
    keyType = {'comment': ('id', 'created_utc', 'subreddit', 'body', 'score', 'permalink'),
               'submission': ('id', 'created_utc', 'subreddit', 'selftext', 'score', 'full_link', 'url')}

    before = int(round(time.time())) #Subtract off last timestamp in set, put in pushshift url.
    beginTime = before #To reset time to original value after comments.
    allPosts = {}
    for postType in ('comment', 'submission'):
        print()


        print('Pushshift ' + postType[0] + postType[1:] + ' request log')

        ct = 0
        posts = []
        while True:
            time.sleep(.5)
            url = f'{apiUrl}{postType}/?author={user}&size=100&before={before}'
            try:
                response = urllib.request.urlopen(url)
                data = json.loads(response.read())['data']

                for i in data:
                    ourKeys = keyType[postType]
                    apiKeys = i.keys()


                    postDict = dict.fromkeys(ourKeys, None)
                    for key in ourKeys:
                        if key in ourKeys and key in apiKeys:
                            postDict[key] = i[key]
                    postDict['postType'] = postType

                    posts.append(postDict)

                if len(posts)!=0:
                    before = posts[-1]['created_utc']

                log = f'{ct+1} - {len(data)} '
                print('\t' + log + ' ' + url)
                ct = ct+1

                if len(data)<100: #Get 100 posts at a time.
                    allPosts[postType + 's'] = posts
                    break
            except HTTPError:
                print('Rate limited')





        before = beginTime



    return allPosts

def countPosts(allPosts): #Count and order most posted subs.
    postCounts = {}
    for postType, posts in allPosts.items():
        subreddits = [post['subreddit'] for post in posts]
        subredditSet = set(subreddits)

        counts = {}
        for subreddit in subredditSet:
            if subreddit is not None:
                counts[subreddit] = subreddits.count(subreddit)

        sortedCounts = sorted(counts.items(), key=lambda kv:(kv[1], kv[0]), reverse=True)

        postCounts[postType] = sortedCounts

    return postCounts

def writeFiles(allPosts, postCounts, user):
    usersDir = os.path.join(os.getcwd(), 'users') #New folder containing a folder for each user.
    if not os.path.exists(usersDir):
        os.mkdir(usersDir)

    userDir = os.path.join(usersDir, user) #New folder containing a folder for each user.
    if not os.path.exists(userDir):
        os.mkdir(userDir)

    if len(allPosts)!=0:
        newUtc = int(round(time.time()))

        jFname = f'{user}.json'
        jPath = os.path.join(userDir, jFname)
        with open(jPath, 'w+', newline='\n') as f:
            json.dump(allPosts, f, indent=4)

        cFname = f'{user}.txt'
        cPath = os.path.join(userDir, cFname)
        with open(cPath, 'w+') as g:
            for k,v in postCounts.items():
                postType = f'***{k[0].upper()}{k[1:]}***'
                g.write(postType + '\n')
                for i in v:
                    g.write(i[0] + ': ' + str(i[1]) + '\n')

                g.write('\n')

        for fname in os.listdir(userDir):
            oldFname = os.path.join(userDir, fname)
            if oldFname not in (jPath, cPath):
                os.remove(oldFname)



if __name__ == '__main__':
    start = time.time()

    user = sys.argv[1]
    outputDir = os.path.join(os.getcwd(), 'users', user)
    print(f'Gathering and formatting data from reddit user {user}')



    allPosts = getPosts(user)
    print('Totals')

    print('\t' + f'Comments = {len(allPosts["comments"])}')


    print('\t' + f'Submissions = {len(allPosts["submissions"])}')

    counts = countPosts(allPosts)

    writeFiles(allPosts, counts, user)

    totalTime = round(time.time() - start, 1)

    print('\tFiles created in  = ' + outputDir )
    print('\tTrimmed and concatenated pushshift JSON = ' + user +'.json')
    print('\tMost posted in subreddits = ' + user +'.txt') #Could probably use a better filename.
    print('\tRun time = ' + f'{totalTime} s')
