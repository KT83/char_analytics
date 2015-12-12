#!/usr/local/bin/python
# -*- coding:utf-8 -*-

import json, urllib2, oauth2 as oauth

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

for r in res:
    data = json.loads(r)

    try:
        if data['user']['lang'] == 'en':
            print data['text']
            # insert texts to mongoDB
    except:
        pass
