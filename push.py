#!/usr/bin/python3
import urllib.request
import json
import time
import os
from pprint import pprint
import sys
from urllib.error import HTTPError
from datetime import datetime
import redditcleaner

def humanReadablePost(redditRawText): #Makes body and selftext not an abomination.
    cleaned = redditcleaner.clean(redditRawText).split() #Makes reddit's text formatting readable

    #Spliting post string into sets of 15 words so the output is readable when it reaches it's place within json.
    splitWords = []
    temp = []
    for i, word in enumerate(cleaned):
        temp.append(word)
        if i % 15 == 0 and i != 0:
            splitWords.append(temp)
            temp = []

    #
    #Another way of saying if the number of totalW words % 15 != 0. Need to put the leftover words where they belong
    if len(temp) != 0:
        splitWords.append(temp)

    outputValue = [' '.join(cleanPost) for cleanPost in splitWords] #1D list with each item containing a max of five words.

    return outputValue


def getPosts(user, keyType): #From pushshift API. Functions kind of a mess but works.

    apiUrl = 'https://api.pushshift.io/reddit/search/'
    postSetMaxLen = 100 #Max num of posts in each pushshift request, seems to be 100 right now or it breaks.


    before = int(round(time.time())) #Subtract off last amp in set, put in pushshift url.
    beginTime = before #To reset time to original value after comments.
    allPosts = {}

    #This for loop is because a lot of the code would have been the same for comments and submissions.
    #Things like if key == 'body' or key == 'selftext': can deal with a problem both comments and some submissions have.
    for postType in ('comment', 'submission'):
        print()

        print('Pushshift ' + postType[0] + postType[1:] + ' request log')

        ct = 0 #For logging each batch of posts returned by pushshift.
        posts = []
        while True: #We need to wait until we've collected all posts then break.
            time.sleep(.75) #Avoids rate limits.
            url = f'{apiUrl}{postType}/?author={user}&size={postSetMaxLen}&before={before}' #API request varying before while the while loop isn't broken.
            try:
                response = urllib.request.urlopen(url)
                data = json.loads(response.read())['data']

                for post in data:
                    ourKeys = keyType[postType] #Getting relevant keys for either a comment or submission.
                    apiKeys = post.keys() #All pushshift keys for this post, we do not want them all - we need readable output.

                    postDict = dict.fromkeys(ourKeys, None) #Kinda forgot why this is written like this.

                    for key in ourKeys: #We are doing things for specific keys, so we need another loop.
                        if key in ourKeys and key in apiKeys: #To only use the keys we need.

                            outputValue = post[key]

                            if key == 'body' or key == 'selftext': #Thanks redditcleaner making this less painful.
                                outputValue = humanReadablePost(outputValue)

                            if key == 'created_utc': #Create a datetime object from timestamp.
                                timestamp = int(post[key])
                                postDict['datetime'] = str(datetime.utcfromtimestamp(timestamp).strftime('%a %b %d %Y, %I:%M %p UTC'))

                            postDict[key] = outputValue

                    postDict['postType'] = postType

                    posts.append(postDict)

                if len(posts) != 0: #Cause if it is there's something there which means more posts to get.
                    before = posts[-1]['created_utc'] #Next time we make a request with the last timestamp from the list of posts from this list of posts.


                print('\t' + f'{ct+1} - {len(data)} {url}') #Log for each API request.
                ct+=1

                if len(data) < postSetMaxLen: #Get 100 posts at a time they switched from 1000?
                    allPosts[postType + 's'] = posts
                    break

            except HTTPError: #The sleep .75 deals with this.
                print('Rate limited')

        before = beginTime #before has been decreasing and we don't want it to start at the last comment for the beggining of submissions.

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

        #Sort by sub count, lambda let's you reach inside the dict and sort the tuples by the count index.
        #key=lambda is great.
        sortedCounts = sorted(counts.items(), key=lambda kv:(kv[1], kv[0]), reverse=True)

        postCounts[postType] = sortedCounts

    return postCounts

def writeFiles(allPosts, postCounts, user):
    usersDir = os.path.join(os.getcwd(), 'users') #New folder containing a folder for each username.
    if not os.path.exists(usersDir):
        os.mkdir(usersDir)

    userDir = os.path.join(usersDir, user) #Contains username files.
    if not os.path.exists(userDir):
        os.mkdir(userDir)

    if len(allPosts)!=0:
        jPath = os.path.join(userDir, f'{user}.json')
        with open(jPath, 'w+', newline='\n') as f:
            json.dump(allPosts, f, indent=4)

        tPath = os.path.join(userDir, f'{user}.txt')
        with open(tPath, 'w+') as g:
            for k,v in postCounts.items():
                postType = f'{k[0].upper()}{k[1:]}'
                g.write(postType + '\n')
                for i in v:
                    g.write(i[0] + ': ' + str(i[1]) + '\n')

                g.write('\n')

def run(user):
    start = time.time()

    #Pushshift attributes I thought were useful.
    keyType = {'comment': ('id', 'created_utc', 'subreddit', 'body', 'score', 'permalink', 'link_id', 'parent_id'),
               'submission': ('id', 'created_utc', 'subreddit', 'selftext', 'score', 'full_link', 'url')}

    outputDir = os.path.join(os.getcwd(), 'users', user)

    print(f'**Gathering and formatting data from reddit user {user}**')

    allPosts = getPosts(user, keyType)
    print()
    print('Totals')

    print('\t' + f'Comments = {len(allPosts["comments"])}')
    print('\t' + f'Submissions = {len(allPosts["submissions"])}')
    print()

    counts = countPosts(allPosts)

    writeFiles(allPosts, counts, user)

    print('File locations')
    print('\t' + outputDir )
    print('\t' + f'{user}.json')
    print('\t' + f'{user}.txt') #Could probably use a better filename.
    print()

    print('Run time - ' + f'{round(time.time() - start, 1)} s')


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print('Remember to add a username')
        print('For help enter redditsfinder -h')
    elif len(sys.argv) == 2:
        if sys.argv[-1] == '-h':
            print('Only argument is a username')
            print('Adding more options soon')
        else:
            run(sys.argv[1])

    else:
        print('Too many arguments')
