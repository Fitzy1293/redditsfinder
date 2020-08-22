# redditsfinder - A simple tool to analyze reddit users
![Imgur Image](https://i.imgur.com/fuLrbSh.gif)

# Installation
***With git (easiest method)***
```
pip3 install redditcleaner
git clone https://github.com/Fitzy1293/redditsfinder.git
```

***Linux***
```
pip3 install redditcleaner 
wget https://raw.githubusercontent.com/Fitzy1293/redditsfinder/master/redditsfinder.py
mv redditsfinder.py ~/bin/redditsfinder && chmod +x ~/bin/redditsfinder
```

***Mac***
```
pip3 install redditcleaner 
curl https://raw.githubusercontent.com/Fitzy1293/redditsfinder/master/redditsfinder.py > redditsfinder.py 
mv redditsfinder.py ~/bin/redditsfinder && chmod +x ~/bin/redditsfinder
```
Mac doesn't include wget, so redirect curl to redditsfinder.py. \
Might work, haven't tested it though so who knows.

***Windows***\
Install with git.

# Running redditsfinder
`python3 redditsfinder.py [options] redditUsername` 

***If you made it executable***\
`redditsfinder [options] redditUsername` 

***Arguments***\
`redditsfinder redditUsername` returns every user post.\
`-pics` returns URLs of user's image uploads.\
`-pics -d` downloads them.

# Example JSON object
![Imgur Image](https://i.imgur.com/yHR87rG.png)

# Why bother with this? 
If you want to archive a reddit user's posts it's impossible to do with the reddit API if there are more than 1k posts. \
