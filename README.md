# redditsfinder - A simple tool to analyze reddit users
**A command line program to get past the 1000 post API limit for a reddit user.**
<br>
![Imgur Image](https://i.imgur.com/u59i2Qq.png)
![Imgur Image](https://i.imgur.com/k4dEG7F.png)
![Imgur Image](https://i.imgur.com/9DatCOJ.png)

# Installation
***With git (easiest method)***
```
pip3 install redditcleaner rich
git clone https://github.com/Fitzy1293/redditsfinder.git
cd redditsfinder
```

***Linux***
```
pip3 install redditcleaner rich
wget https://raw.githubusercontent.com/Fitzy1293/redditsfinder/master/redditsfinder.py
mv redditsfinder.py ~/bin/redditsfinder && chmod +x ~/bin/redditsfinder
```

***Mac***
```
pip3 install redditcleaner rich
curl https://raw.githubusercontent.com/Fitzy1293/redditsfinder/master/redditsfinder.py > redditsfinder.py 
mv redditsfinder.py ~/bin/redditsfinder && chmod +x ~/bin/redditsfinder
```
Mac doesn't include wget, so redirect curl to redditsfinder.py. \
Might work, haven't tested it though so who knows.

***Windows***\
Install with git.

# Running redditsfinder
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

