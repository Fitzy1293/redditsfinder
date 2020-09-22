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
To deal with it, I gave up and looked online for an alternative. Luckily there was a good one readily available.

# Installation and a sample run
***With pypi (easiest)***\
`pip3 install redditsfinder`

***With git***
```
pip3 install redditcleaner rich
git clone https://github.com/Fitzy1293/redditsfinder.git
cd redditsfinder
```
Now test if it works. 

```
python3 redditsfinder.py 'yourUsername'
```
That's all there is to setup. 


# Running redditsfinder

***Arguments***\
`python3 -m redditsfinder 'username'` returns every user post.\
`python3 -m redditsfinder -pics 'username'` returns URLs of user's image uploads.\
`python3 -m redditsfinder -pics -d 'username'` downloads them.

![Imgur Image](https://i.imgur.com/t0hR7Oc.png) 

## If you installed with pip
`python3 -m redditsfinder [options] 'username'`

## If you installed with git

***In the directory where you installed redditsfinder.py***\
`python3 redditsfinder.py [options] 'username'` 

***If you made it executable***\
`./redditsfinder.py [options] 'username'` 



# Example JSON object
![Imgur Image](https://i.imgur.com/yHR87rG.png)

# Example use of -pics -d
![Imgur Image](https://i.imgur.com/1bMuKlV.png)

