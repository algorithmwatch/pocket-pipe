# Pocket pipe

I love Twitter because I get to discover great articles linked to by people I chose to follow. 

I hate Twitter because some people share context-less snippets or photos, write threads, make sneaky comments with no informational value (how many tweets with "this is the most X" have you read today?) or retweet jokes I don't get.

To fight against the time sink Twitter is and regain some sanity, I decided to remove my Twitter client from my cell phone. Instead, I built this small script to feed my Pocket with content from RSS feeds and randomly picked links people I follow shared on Twitter.

After a few days of use, I find the set up very efficient. I spend much less time getting upset about upsetting things referred to in 280 characters by upset people. And I get to read much more about more diverse topics.

On the downside, if everyone moves away from Twitter and stops sharing links there, my whole set up is ruined. That's the problem with freeriding.

#### How's this different from paper.li?

The selecting algorithm is transparent. I'm in control of what links make it to my Pocket.

#### How's this different from a newspaper?

Over the past 10 years, I carefully selected a group of 200 experts in various fields in a neat Twitter list. No black box editorial meetings - I know exactly why I read what I'm reading.

#### Why Pocket?

Pocket is one of the few apps where you can actually pay to be a customer, not a product.

## How to make your own pipe

**Create a Pocket app.** Go to [Create an Application](https://getpocket.com/developer/apps/new) on the Pocket website and create your app. You just need the _Add_ permission. Choose any one platform you want, it makes no difference.

**Get your Pocket access token.** Pocket then gives you a _Consumer Key_. You need to combine it with an _Access Token_ to be able to programmatically add content to your Pocket. To obtain this token, replace `os.environ["consumer_key"]` with your Consumer Key and run `get_pocket_token.py`. Save the access token you'll be given on the terminal.

**Create a Twitter App**. Go to [Create an application](https://apps.twitter.com/app/new) at Twitter and create a Twitter app. You just need the _Read_ permission.

**Get your Twitter tokens**. Once your app is created, go to the Keys and Access Tokens tab and authorize the app for yourself. Then collect your Consumer Key, Consumer Secret, Access Token and Access Token Secret and add them as environment variables or directly in the feed_pocket.py file.

**Add some content to your pipe.** In feed_pocket.py, replace the RSS feeds and Twitter lists with your own.

**Create a cron on Heroku.** Push your files to a new Heroku app. In the add-ons tab, create an hourly scheduler with the task `python feed_pocket.py` and add a ClearDB database (both add-ons are free). If you don't know what I mean, create an issue and I'll write a real tutorial.

**That's it!** Enjoy waking up to new articles instead of angry tweeps!