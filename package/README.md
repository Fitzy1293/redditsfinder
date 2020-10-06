# redditsfinder
**`pip3 install redditsfinder`**\
**A command line program to easily download reddit users' post histories.** \
Get any reddit user's entire post history with one command while avoiding the reddit API's 1000 post limit. \
The main meat of this program is making the requests to pushshift and manipulating pushshift's JSON for a more readable all_posts.json file. \
There is also a handly image downloader I made that avoids a lot of the problems of trying to grab multiple images from different sites at once. Things like file types being not what the file is encoded as, and changed URLs. Or a URL that ends with .png that returns ASCII text. It gets imgur albums along with images, because at least for a while imgur was essentially reddit's non-official image hosting service. 

The colored terminal features and markup are from https://github.com/willmcgugan/rich \
`pip3 install rich` which is one the coolest python packages I've seen. It's very easy to pick up, but as is shown with the animated example in its README, still has a lot of depth.  

https://github.com/LoLei/redditcleaner `pip3 install redditcleaner` was also a massive help for dealing with reddit's strange markup. \
Comments and self-posts can be unreadable when put in another format like JSON if they have a fair amount of formatting. \
To deal with it, I gave up and looked online for an alternative. Luckily there was a good one readily available. \

# Installation
`pip3 install redditsfinder`

# Running redditsfinder

***Arguments***\
Takes an arbitrary number of usernames, such that there is at least one username.\
`redditsfinder [options] username_0 username_1 username_2 ...`\
`redditsfinder username` returns every post to a JSON file and formats a table in the terminal for a quick view.\
***Optional args***\
`-pics` returns URLs of image uploads.\
`-pics -d` downloads them.\
`-q` turns off non log related print statements.

# Example terminal table
![Imgur Image](https://i.imgur.com/t0hR7Oc.png) 

# Example use of -pics -d
![Imgur Image](https://i.imgur.com/1bMuKlV.png)

# Example JSON object
![Imgur Image](https://i.imgur.com/yHR87rG.png)


