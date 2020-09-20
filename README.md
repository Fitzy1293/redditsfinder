# redditsfinder 
**A command line program to easily view reddit users' post histories.** \
Get any reddit user's entire post history with one command while avoiding the reddit API's 1000 post limit. \
The main meat of this program is making the requests to pushshift and manipulating pushshift's JSON for a more readable all_posts.json file. \
There is also a handly image downloader I made that avoids a lot of the problems of trying to grab multiple images from different sites at once. Things like file types being not what the file is encoded as, and changed URLs. Or a URL that ends with .png that returns ASCII text. It gets imgur albums along with images, because at least for a while imgur was essentially reddit's non-official image hosting service. 


The terminal syntax highlighting is from https://github.com/willmcgugan/rich \
`pip install rich` which is one the coolest python packages I've seen. 

# Installation and a sample run
***With git (easiest method)***
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

![Imgur Image](https://i.imgur.com/BvQP4c5.png) 

***In the directory where you installed redditsfinder.py***\
`python3 redditsfinder.py [options] redditUsername` 

***If you made it executable***\
`redditsfinder [options] redditUsername` 

***Arguments***\
`redditsfinder redditUsername` returns every user post.\
`-pics` returns URLs of user's image uploads.\
`-pics -d` downloads them.

# Example JSON object
![Imgur Image](https://i.imgur.com/yHR87rG.png)

# Example use of -pics -d
![Imgur Image](https://i.imgur.com/8MMLhMD.png)

