import requests, json, time

consumer_key = os.environ["consumer_key"]
redirect_uri = "http://nkb.fr"

r = requests.post("https://getpocket.com/v3/oauth/request", 
	              data = {"consumer_key": consumer_key, "redirect_uri": redirect_uri})

code = r.text.replace("code=", "").strip()

print ("Click here: https://getpocket.com/auth/authorize?request_token=%s&redirect_uri=%s" % (code, redirect_uri))

timer = 10

print ("You have %s seconds left!" % timer)

while timer > 0:
	time.sleep(1)
	timer -= 1
	print ("%s seconds" % timer)

r = requests.post("https://getpocket.com/v3/oauth/authorize",
	              data = {"consumer_key": consumer_key, "code": code})

print (r.text)