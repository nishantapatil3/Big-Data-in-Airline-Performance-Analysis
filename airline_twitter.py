import tweepy
from tweepy import Stream
from tweepy.streaming import StreamListener
import re
from tweepy import OAuthHandler
from textblob import TextBlob
import sys
import json
# from __future__ import print_function
from pymongo import MongoClient

RESTAURANT = None
POLARITY = None


def twitter_update(restaurant,state):
    if state == 0:
        return True
    restaurant_name  = restaurant.replace("_"," ").lower()
    connection = MongoClient("ds117311.mlab.com", 17311)
    db = connection['restreco']
    db.authenticate("restUser", "restUser123#")
    val = 0
    if state == 1:
        db.restaurants_dump.update_one({"name": re.compile(restaurant_name, re.IGNORECASE),"rating":{"$lt":5}}, {
            '$inc': {
                'rating': 0.1
            }
        }, upsert=False)
    elif state == -1:
        db.restaurants_dump.update_one({"name": re.compile(restaurant_name, re.IGNORECASE), "rating": {"$gt": 0}}, {
            '$inc': {
                'rating': -0.1
            }
        }, upsert=False)

    return True

# list of restaurant from the db
LOOKUP_KEYWORDS = ["deltaairlines", "southwestairlines","jetblue","virginairlines"] # to be taken from the mongo DB


# for i in xrange(len(LOOKUP_KEYWORDS)):
#     LOOKUP_KEYWORDS[i] = LOOKUP_KEYWORDS[i].replace(" ", "_")

print("str: "+str(LOOKUP_KEYWORDS))


class AnalyzeTweet():

    def clean_tweet(self, tweet):
        '''
        Utility function to clean tweet text by removing links, special characters
        using simple regex statements.
        '''
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

    def get_tweet_sentiment(self, tweet):
        '''
        Utility function to classify sentiment of passed tweet
        using textblob's sentiment method
        '''
        restaurant = "-"
        for rest in LOOKUP_KEYWORDS:
            if rest in tweet:
                restaurant = rest

        # create TextBlob object of passed tweet text
        analysis = TextBlob(self.clean_tweet(tweet))
        # set sentiment
        print("Polarity:"+str(analysis.sentiment.polarity))
        if analysis.sentiment.polarity > 0:
            return 1
        elif analysis.sentiment.polarity == 0:
            return 0
        else:
            return -1

# tweet_analyzer = AnalyzeTweet()
# input_text = "This restaurant #pistahouse"
# print("Input:"+input_text+"\nSentiment:"+tweet_analyzer.get_tweet_sentiment(input_text))
# sys.exit()

class MyListener(StreamListener):

    def on_data(self, data):
        try:
            with open('twitter_data.json', 'a') as f:
                f.write(data)
                tweet_obj = json.loads(data)
                tweet = tweet_obj['text']
                print("NEW TWEET: "+str(tweet))
                sentiment = tweet_analyzer.get_tweet_sentiment(tweet)
                restaurant = ""
                print("Sentiment: "+str(sentiment))
                # get restaurant name from the text
                for rest in LOOKUP_KEYWORDS:
                    if rest in tweet:
                        restaurant = rest
                print("Airline: "+restaurant)

                twitter_update(restaurant, sentiment)
                return True
        except BaseException as e:
            print("Error on_data: " % str(e))
        return True

    def on_error(self, status):
        print("Error in streaming!!")
        print(status)
        return True

consumer_key = "KYS0m11ML0WWuftNvjdaKF7iR"
consumer_secret = "hKszS7x6pmkblS4iIa6Z5UkNpogucRK45T81T5DRoStmxn2a6y"
access_token = "84014050-tgU5RY2ekrdRrQh4xVcZzuTHdbIimZ3SsFjobEn1J"
access_token_secret = "SKtdtX1856iCTWk1UVARjLT3ObR3OGvnuIAiVHiv6U7uT"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)
tweet_analyzer = AnalyzeTweet()

# twitter_stream = Stream(auth, MyListener())
# twitter_stream.filter(track=LOOKUP_KEYWORDS)
# scripts starts listening to the global tweet at this point
#
# # Below code to print the tweet matching the desired keyword.
#
public_tweets = api.home_timeline()
cricTweet = tweepy.Cursor(api.search, q='Tejas').items()

for tweet in cricTweet:
    print "=================================================================================="
    print "Created at: ",tweet.created_at
    print "Tweet: ",tweet.text
    print "lang:", tweet.lang
    print "geo:", tweet.geo
    try:
        print "place country name:", tweet.place.country
        print "place name:", tweet.place.name
    except:
        print "No place found"
    # print "User:", tweet.user
    print "User Location:", tweet.user.location
    print "User name:", tweet.user.name
