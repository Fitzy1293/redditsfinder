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

# f strings are amazing.


# Makes body and selftext not an abomination.
def humanReadablePost(redditRawText):
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


# Uses pushshift API. Functions kind of a mess but works.
def getPosts(user, keyType):

    apiUrl = 'https://api.pushshift.io/reddit/search/'
    # Max num of posts in each pushshift request, seems to be 100 right now or it breaks.
    postSetMaxLen = 100

    # Subtract off last amp in set, put in pushshift url.
    before = int(round(time.time()))
    beginTime = before  # To reset time to original value after comments.
    allPosts = {}

    # This for loop is because a lot of the code would have been the same for comments and submissions.
    # Things like if key == 'body' or key == 'selftext': can deal with a problem both comments and some submissions have.
    for postType in ('comment', 'submission'):
        print()

        print(f'{postType[0].upper()}{postType[1:]} request log:')

        ct = 0  # For logging each batch of posts returned by pushshift.
        posts = []
        while True:  # We need to wait until we've collected all posts then break.
            time.sleep(.75)  # Avoids rate limits.
            # API request varying before while the while loop isn't broken.
            url = f'{apiUrl}{postType}/?author={user}&size={postSetMaxLen}&before={before}'
            try:
                response = urllib.request.urlopen(url)
                data = json.loads(response.read())['data']

                for post in data:
                    # Relevant keys for either a comment or submission.
                    ourKeys = keyType[postType]
                    # All pushshift keys for this post, we do not want them all - we need readable output.
                    apiKeys = post.keys()

                    # Kinda forgot why this is written like this.
                    postDict = dict.fromkeys(ourKeys, None)

                    for key in ourKeys:  # We are doing things for specific keys, so we need another loop.
                        if key in ourKeys and key in apiKeys:  # To only use the keys we need.

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

                    postDict['postType'] = postType

                    posts.append(postDict)

                # Cause if it is there's something there which means more posts to get.
                if len(posts) != 0:
                    # Next time we make a request with the last timestamp from the list of posts.
                    before = posts[-1]['created_utc']

                ct = ct + len(data)
                # print(f'\t{ct+1} - {len(data)} {url}') #Log for each API request.
                print(f'\t{ct} {url}')

                if len(data) < postSetMaxLen:  # Get 100 posts at a time they switched from 1000?
                    allPosts[postType + 's'] = posts
                    break

                # ct+=1

            except HTTPError:  # The sleep .75 deals with this.
                print('Rate limited')

        # before has been decreasing and we don't want it to start at the last comment for the beggining of submissions.
        before = beginTime

    return allPosts


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


def writeFiles(allPosts, postCounts, user):

    # New folder containing a folder for each username.
    usersDir = os.path.join(os.getcwd(), 'users')
    userDir = os.path.join(usersDir, user)  # Contains files for username.
    for dir in (usersDir, userDir):
        if not os.path.exists(dir):
            os.mkdir(dir)

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

def makeBox(list): #Takes 1 d list of strings, returns str in a box that fits.
    longestStr = len(max(list, key=len))
    box = str('─') * (longestStr + 1)

    boxedStr = '\n'.join([f'│{i}{ str(" " * ( longestStr + 1 - len(i) )) }│' for i in list])

    return f'┌{box}┐\n{boxedStr}\n└{box}┘' #(U+2518) and (U+2510) box drawing chars respecitvely.



def printTotals(totalsDict): #Printed stuff after the pushshift log.
    print()
    countableTab = str(" " * 4) #For getting length of string to box easier because a tab is only one character.

    ##############################################################################################################################
    sortedPrintList = []
    for k, v in totalsDict['postCounts'].items():
        postTypeList = [k]
        for subreddit in v:

            new = f'{countableTab}{subreddit[0]} {subreddit[1]}'
            postTypeList.append(new)

        #postTypeList.append('')

        print(makeBox(postTypeList))

    #*****************************************************************************************************************************

    ##############################################################################################################################
    #Box containing # of comments/submissions, dir and path of files, and run time.

    comments = f'Comments{countableTab}= {totalsDict["commentsLenPrint"]}'
    submissions = f'Submissions = {totalsDict["submissionsLenPrint"]}'
    dir = totalsDict['dir']
    allPosts = f'{countableTab}all_posts.json'
    sortedSubreddits = f'{countableTab}sorted_subreddits.txt'  # Could probably use a better filename.
    runTime = f'Run time - {round(totalsDict["end"] - totalsDict["start"], 1)} s'


    infoToBox = [comments, submissions, '', dir, allPosts, sortedSubreddits, '', runTime]

    print(makeBox(infoToBox))

    #*****************************************************************************************************************************




def run(user):
    start = time.time()

    # Pushshift attributes I thought were useful.
    keyType = {'comment': ('id', 'created_utc', 'subreddit', 'body', 'score', 'permalink', 'link_id', 'parent_id'),
               'submission': ('id', 'created_utc', 'subreddit', 'selftext', 'score', 'full_link', 'url')}

    print(f'**Gathering and formatting data from reddit user {user}**')

    allPosts = getPosts(user, keyType)


    postCounts = countPosts(allPosts)

    writeFiles(allPosts, postCounts, user)

    #printTotals makes the terminal output look nice
    totalsDict = {'postCounts': postCounts,
                  'commentsLenPrint': str( len(allPosts['comments']) ),
                  'submissionsLenPrint': str( len(allPosts['submissions']) ),
                  'dir': os.path.join(os.getcwd(), 'users', user),
                  'start': start,
                  'end': time.time()}

    printTotals(totalsDict)




if __name__ == '__main__':  # System arguments
    if len(sys.argv) == 1:
        print('Remember to add a username')
        print('For help enter redditsfinder -h')
    elif len(sys.argv) == 2:
        if sys.argv[-1] == '-h':
            print('Only argument is a username')
            print('Adding more options soon')
        else:
            run(sys.argv[1])

    elif len(sys.argv):
        print('Too many arguments')
