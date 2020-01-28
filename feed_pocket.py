import requests, json, feedparser, os, random
import datetime as dt
import peewee
from peewee import *
from twitter import *
import urllib.parse as urlparse
from sys import argv

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

countries = [
	{
		"name": "Czech",
		"twitter_query": '("politika" AND "algoritmus")  OR ("rozhodnutí" AND "algoritmus") OR ("mesto" AND "algoritmus")  OR "prediktivní policie" OR "rozpoznávání tváře" -Čína -Pixel -Samsung',
		"rss_feeds": []
	},
	{
		"name": "Danish",
		"twitter_query": '("afgørelse" AND "algoritme") OR ("politik" AND "algoritme") OR ("by" AND "algoritme")  OR "forudsigeligt politi" OR "ansigtsgenkendelse" -kina -Pixel -Samsung',
		"rss_feeds": []
	},
	{
		"name": "Dutch",
		"twitter_query": '("besluit" AND "algoritme") OR ("politiek" AND "algoritme") OR ("stad" AND "algoritme") OR "voorspellende politie" OR "Gezichtsherkenning" OR "risicoprofilering" -china -Pixel -Samsung',
		"rss_feeds": [
			"https://bijvoorbaatverdacht.nl/feed/"
		]
	},
	{
		"name": "English",
		"twitter_query": '"iborderctrl" OR "automated decision making" OR "automated decision-making" OR "algocracy" OR "algorithmic governance" OR ("AI" and "job interview") -china -Pixel -Samsung',
		"rss_feeds": []
	},
	{
		"name": "French",
		"twitter_query": '("algorithme" AND "travail") OR ("politique" AND "algorithme") OR ("social" AND "algorithme") OR ("ville" AND "algorithme")  OR "police prédictive" OR "décision automatisée" -chine -Pixel -Samsung',
		"rss_feeds": [
			"https://technopolice.fr/feed/"
		]
	},
	{
		"name": "German",
		"twitter_query": '("algorithmus" AND "arbeitsmarkt") OR ("algorithmus" AND "politik") OR ("algorithmus" AND "stadt") OR ("algorithmus" AND "sozial") OR ("entscheidung" AND "algorithmus") -china -Pixel -Samsung',
		"rss_feeds": [
			"https://algorithmenethik.de/feed/"
		]
	},
	{
		"name": "Hungarian",
		"twitter_query": '("automatizált" AND "algoritmus")  OR ("döntés" AND "algoritmus") OR ("város" AND "algoritmus")  OR "prediktív rendőrség" OR "arcfelismerő" -Kína -Pixel -Samsung',
		"rss_feeds": []
	},
	{
		"name": "Italian",
		"twitter_query": '("algoritmo" AND "decisione")  OR ("algoritmo" AND "politica") OR ("algoritmo" AND "città") OR "polizia predittiva" -cina -Pixel -Samsung',
		"rss_feeds": []
	},
	{
		"name": "Polish",
		"twitter_query": '("algorytm" AND "decyzja") OR ("algorytm" AND "polityka") OR ("algorytm" AND "miasto") OR "prognozowanie policji" OR "rozpoznawania rysów twarzy" -Chiny -Pixel -Samsung',
		"rss_feeds": [
			"https://epf.org.pl/en/projects/feed/"
			# "https://www.sztucznainteligencja.org.pl/tematy/ludzie/spoleczenstwo/feed/"
		]
	},
	{
		"name": "Romanian",
		"twitter_query": '("algoritmul" AND "decizie")  OR ("algoritmul" AND "politică") OR ("oraș" AND "algoritmul") OR "previziune poliție" OR "recunoaşterea facială" -china -Pixel -Samsung',
		"rss_feeds": []
	},
	{
		"name": "Slovak",
		"twitter_query": '("politický" AND "algoritmus") OR ("rozhodnutie" AND "algoritmus") OR ("mesto" AND "algoritmus") OR "prediktívne policajné" -Čína -Pixel -Samsung',
		"rss_feeds": []
	},
	{
		"name": "Serbian",
		"twitter_query": '("алгоритам" AND "политичка") OR ("вештачка интелигенција" AND "град") OR ("Србија" AND "вештачка интелигенција") OR "предвидивање полиције" -Кина -Pixel -Samsung',
		"rss_feeds": [
			"https://www.sharefoundation.info/en/category/news/feed/"
		]
	},
	{
		"name": "Spanish",
		"twitter_query": '("decisión" AND "algoritmo") OR ("política" AND "algoritmo") OR ("ciudad" AND "algoritmo") OR "policía predictiva" -china -Pixel -Samsung',
		"rss_feeds": []
	},
	{
		"name": "Swedish",
		"twitter_query": '("beslut" AND "algoritm") OR ("politik" AND "algoritm") OR ("stad" AND "algoritm") OR "prediktiv polis" OR "ansiktsigenkänning" -kina -Pixel -Samsung',
		"rss_feeds": []
	 }
]

# List of websites that you do not want to read from.
# Removing Twitter ensures that you won't be given linked tweets.
blacklisted_urls = [
  "twitter.com"	             # Embedded tweets
 ,"freie-welt.eu"			 # Probably a content farm
 ,"stohl.de"				 # Looks like automated link collection 
 ,"tweetedtimes.com"		 # List of links
 ,"linkedin.com"			 # Never read something interesting there
]

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

db.connect(reuse_if_open=True)
db.create_tables([Link], safe=True)


def checkDuplicate(link):
    try:
        # Shorten link to 255 chars
        link = link[:254]
        Link.create(url = link)
        return True

    except IntegrityError:
        return False
        pass

def add(link, country_tag = None):
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

	for country in countries:
		response = t.search.tweets(q="filter:links %s" % country["twitter_query"], count=200)
		for tweet in response["statuses"]:
			if "urls" in tweet["entities"]:
				for url in tweet["entities"]["urls"]:
					if not any(x in url["expanded_url"] for x in blacklisted_urls):
						# Remove anything after the ? in the URL (can contain twitter or FB details)
						final_url = url["expanded_url"].split('?', 1)[0]
						# Reject domains, i.e. URLS with less than 4 / (because http://domain.tld/)
						if final_url.count('/') <= 3:
							pass
						else:
							urls.append({"url": final_url, "country_tag": country["name"]})

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

	force = False
	for arg in argv:
		if arg == "force":
			force = True

	now = dt.datetime.utcnow()
	current_hour = now.hour
	if current_hour % 8 == 0 or force:
		addLinks()
		checkRSS()
