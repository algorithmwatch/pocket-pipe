import requests, json, feedparser, os, random
import datetime as dt
import peewee
from peewee import *
from twitter import *
import urllib.parse as urlparse

if 'CLEARDB_DATABASE_URL' not in os.environ:
    from playhouse.sqlite_ext import SqliteExtDatabase

access_token = os.environ["access_token"]
consumer_key = os.environ["consumer_key"]
twitter_access_token = os.environ["twitter_access_token"]
twitter_access_secret = os.environ["twitter_access_secret"]
twitter_key = os.environ["twitter_key"]
twitter_secret = os.environ["twitter_secret"]

# Maximum number of unread articles to be shown in your Pocket
max_articles = 7

# Your RSS feed, exported from Bloglines
rss_feeds = ["http://blog.nkb.fr/atom.xml"
,"https://ecointerview.wordpress.com/feed/"
,"http://tumourrasmoinsbete.blogspot.com/feeds/posts/default"
,"https://xkcd.com/rss.xml"
,"https://www.schneier.com/blog/atom.xml"
,"https://blog.barbayellow.com/feed/"
,"http://border1871.hypotheses.org/feed"
,"https://lavoiedelepee.blogspot.com/feeds/posts/default"
,"https://gabriel-et-tristan.blogspot.com/feeds/posts/default"
,"http://www.maartenlambrechts.com/feed.xml"
,"https://www.youtube.com/feeds/videos.xml?channel_id=UCmY71FGkk5kMwde_TP3KbnQ"
,"https://www.youtube.com/feeds/videos.xml?channel_id=UC3XTzVzaHQEd30rQbuvCtTQ"]

# The Twitter lists to pull links from
twitter_lists = [{"id": 45745119, "slug": "✭✭✭✭"}]

# List of websites that you do not want to read from.
# Removing Twitter ensures that you won't be given linked tweets.
blacklisted_urls = [
  "https://twitter.com"                  # Embedded tweets
, "legorafi.fr", "theonion.com"          # Parody
, "observablehq.com"                     # Does not render on Pocket's browser
, "mindnews.fr"							 # Hard paywall
, "haaretz"								 # Paywall
, ".pdf"								 # Doesn't read well on Pocket
, "paper.li"							 # Not interesting
]

def dbInit():
    if 'CLEARDB_DATABASE_URL' in os.environ:
        url = urlparse.urlparse(os.environ['CLEARDB_DATABASE_URL'])
        db = peewee.MySQLDatabase(url.path[1:], host=url.hostname, user=url.username, passwd=url.password)
    else:
        db = SqliteExtDatabase('links.db')

    class BaseModel(Model):
        class Meta:
            database = db

    class Link(BaseModel):
        url = CharField()

        class Meta:
            primary_key = CompositeKey('url')

    db.connect()
    db.create_tables([Link], safe=True)

    return Link

def checkDuplicate(link):
    Link = dbInit()
    try:
        Link.create(url = link)
        return True

    except IntegrityError:
        return False
        pass

def add(link, from_tag = None):
	if checkDuplicate(link):
		url = "https://getpocket.com/v3/add"

		r  = requests.post(url, data={"url": link, "tags": from_tag, "consumer_key": consumer_key, "access_token": access_token})
		data = json.loads(r.text)
		
		if data["status"] == 1:
			print("Added %s. Word count %s" % (data["item"]["title"], data["item"]["word_count"]))
			return data["item"]
		else:
			return False
	else:
		return False

def checkRSS():
	successfully_parsed = 0
	for rss_feed in rss_feeds:
		d = feedparser.parse(rss_feed)
		for entry in d.entries[0:5]:
			add(entry.link, "RSS")
			successfully_parsed += 1

	return successfully_parsed

def checkTwitter():
	auth = OAuth(twitter_access_token, twitter_access_secret, twitter_key, twitter_secret)
	t = Twitter(auth=auth)

	urls = []

	for twitter_list in twitter_lists:
		for tweet in t.lists.statuses(list_id=twitter_list["id"], slug=twitter_list["slug"], count=500):
			tweet_user = tweet["user"]["screen_name"]
			tweet_user = "@" + tweet_user
			if "urls" in tweet["entities"]:
				for url in tweet["entities"]["urls"]:
					if not any(x in url["expanded_url"] for x in blacklisted_urls):
						urls.append({"url": url["expanded_url"], "username": tweet_user})

	return urls

def countUnreads():
	url = "https://getpocket.com/v3/get"
	r  = requests.post(url, data={"consumer_key": consumer_key, "access_token": access_token})
	data = json.loads(r.text)
	unread_items = data["list"]
	return len(unread_items)

def selectLink():
	urls = checkTwitter()
	unread_items = countUnreads()
	while unread_items <= max_articles:
		url = random.choice(urls)
		if add(url["url"], url["username"]):
			unread_items += 1

if __name__ == "__main__":
    selectLink()
    checkRSS()