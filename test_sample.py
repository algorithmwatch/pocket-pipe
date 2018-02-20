import feed_pocket

def test_addlink():
	link = "http://blog.nkb.fr/retour-a-quick"
	from_tag = "test"
	assert(feed_pocket.add(link, from_tag) == True)

def test_RSS():
	assert(feed_pocket.checkRSS() > 0)

def test_check_dup():
	feed_pocket.checkDuplicate("http://google.com")
	assert(feed_pocket.checkDuplicate("http://google.com") == False)

def test_checkTwitter():
	assert(len(feed_pocket.checkTwitter()) > 0)