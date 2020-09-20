# redditsfinder 
**A command line program to easily view reddit users' post histories.** \
Get any reddit user's entire post history with one command while avoiding the reddit API. \
The main meat of this program is making the requests to pushshift and parsing and formatting the all_posts.json file. \
The terminal syntax highlighting is from `pip install rich`.

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

