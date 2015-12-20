#!/usr/local/bin/python
# -*- coding:utf-8 -*-

import json, urllib2, oauth2 as oauth
import sys
from DictionaryServices import *
from pymongo import MongoClient

KEYS = {
        'consumer_key':'wplEx0bg9v2Gk3fz0MZDH2s37',
        'consumer_secret':'lENzNSXYnD5USAiJHLI4PsALsswhWuvpka5p7ZLcjvTY9mpI9I',
        'access_token':'621027158-XARti29Ts8LvNMEXh7HNFuOhkLigyOodRvgknUmP',
        'access_secret':'2V3qQCPGvggcZGr6iEllDQ7e7ox94RrpaG2ulgAyJ1VK5'
       }

consumer = oauth.Consumer(key = KEYS['consumer_key'], secret = KEYS['consumer_secret'])
token = oauth.Token(key = KEYS['access_token'], secret = KEYS['access_secret'])

url = 'https://stream.twitter.com/1.1/statuses/sample.json'

request = oauth.Request.from_consumer_and_token(consumer, token, http_url=url)
request.sign_request(oauth.SignatureMethod_HMAC_SHA1(), consumer, token)
res = urllib2.urlopen(request.to_url())

def search_dictionary(word):
    result = DCSCopyTextDefinition(None, word, (0, len(word)))
    if result is None:
        return 0
    else:
        return 1

def is_english(text):
    words = text.split()
    text_len = len(words)
    count = 0
    for word in words:
        if search_dictionary(word) == 1:
            count += 1
    rate = float(count) / float(text_len)
    if rate > 0.6:
        return 1
    else:
        return 0

def get_at_mentions(text):
    words = text.split()
    for word in words:
        if word.startswith("@"):
            return word

def get_URLs(text):
    words = text.split()
    for word in words:
        if word.startswith("http"):
            return word

def get_plane_text(text):
    at_mention = get_at_mentions(text)
    URL = get_URLs(text)

    text = text.replace(at_mention, "")
    text = text.replace(URL, "")
    text = text.replace("RT", "")

    return text

def get_stream():
    for r in res:
        data = json.loads(r)
        try:
            if data['user']['lang'] == 'en':
                text =  data['text']
                if is_english(text) == 1:
                    text = get_plane_text(text)
                    print(text)
                    # insert texts to mongoDB
                    mongo_client = MongoClient('localhost:27017')
                    db_connect = mongo_client["eng_tweets"]
                    db_connect["eng_tweets"].insert_one({'text':text})
        except:
            pass


if __name__ == "__main__":
    get_stream()
