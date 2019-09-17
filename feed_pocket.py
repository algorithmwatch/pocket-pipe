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
max_articles = 100

# Your RSS feed, exported from Bloglines
countries = [
	{
		"name": "France",
		"twitter_query": '("politique" AND "algorithme")  OR "police prédictive" OR "décision automatisée"',
		"rss_feeds": [
			"https://technopolice.fr/feed/"
		]
	 }
]

# List of websites that you do not want to read from.
# Removing Twitter ensures that you won't be given linked tweets.
blacklisted_urls = [
  "https://twitter.com"                  # Embedded tweets
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

		r  = requests.post(url, data={"url": link, "tags": country_tag, "consumer_key": consumer_key, "access_token": access_token})
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
	for country in countries:
		country_tag = country["name"]
			for rss_feed in country["rss_feeds"]:
				d = feedparser.parse(rss_feed)
				for entry in d.entries[0:5]:
					add(entry.link, country_tag)
					successfully_parsed += 1

	return successfully_parsed

def checkTwitter():
	auth = OAuth(twitter_access_token, twitter_access_secret, twitter_key, twitter_secret)
	t = Twitter(auth=auth)

	urls = []

	for twitter_list in twitter_lists:
		for tweet in t.search.tweets(q="filter:links %s" % country["twitter_query"], count=10):
			if "urls" in tweet["entities"]:
				for url in tweet["entities"]["urls"]:
					if not any(x in url["expanded_url"] for x in blacklisted_urls):
						urls.append({"url": url["expanded_url"], "country_tag": country["name"]})

	return urls

def countUnreads():
	url = "https://getpocket.com/v3/get"
	r  = requests.post(url, data={"consumer_key": consumer_key, "access_token": access_token})
	data = json.loads(r.text)
	unread_items = data["list"]
	return len(unread_items)

def addLinks():
	urls = checkTwitter()
	unread_items = countUnreads()
	for url in urls:
		if unread_items <= max_articles:
			if add(url["url"], url["country_tag"]):
				unread_items += 1

if __name__ == "__main__":
    now = dt.datetime.utcnow()
    current_hour = now.hour
    if current_hour % 6 == 0:
	    selectLink()
	    checkRSS()
