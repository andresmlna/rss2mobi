[**rss2mobi in action**](https://andresmlna.me/kindle)

rss2mobi fetch RSS articles into a SQLite database every hour, using populate_db.py. Using articles2mobi.py downloads all URLs stored and converts to .mobi format for Amazon Kindle. 


**Optional, you can create a .html file for audit all .mobi files generated.**

![.mobi files website](https://i.imgur.com/ZXl7pyQ.png)

---

**Requirements**

Python +3.5

kp3 [andresmlna/kindle-periodical](https://github.com/andresmlna/kindle-periodical)

feedparser

newspaper3k

[kindlegen](https://www.amazon.com/gp/feature.html?docId=1000765211)
