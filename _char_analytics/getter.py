from requests_oauthlib import OAuth1Session
from requests.exceptions import ConnectionError, ReadTimeout, SSLError
import json, datetime, time, re, sys, traceback, pymongo
from pymongo import MongoClient
from collections import defaultdict
import numpy as np

KEYS = {
        'consumer_key':'wplEx0bg9v2Gk3fz0MZDH2s37',
        'consumer_secret':'lENzNSXYnD5USAiJHLI4PsALsswhWuvpka5p7ZLcjvTY9mpI9I',
        'access_token':'621027158-XARti29Ts8LvNMEXh7HNFuOhkLigyOodRvgknUmP',
        'access_secret':'2V3qQCPGvggcZGr6iEllDQ7e7ox94RrpaG2ulgAyJ1VK5'
       }

twitter = None
connect = None
db      = None
tweetdata = None
meta    = None

# initialize
def initialize():
    global twitter, connect, db, tweetdata, meta
    twitter = OAuth1Session(KEYS['consumer_key'],KEYS['consumer_secret'],
                            KEYS['access_token'],KEYS['access_secret'])
    connect = MongoClient('localhost', 27017)
    db = connect.char_ana
    tweetdata = db.tweetdata
    meta = db.metadata

initialize()

def getTweetData():
    global twitter
    url = 'https://api.twitter.com/1.1/search/tweets.json'

    params = {  'q':'a',
                'count':'100',
                'lang':'en',
                'result_type':'recent',
    }

    req = twitter.get(url, params = params)   # get tweet data

    # decode the response
    if req.status_code == 200: # success
        timeline = json.loads(req.text)
        metadata = timeline['search_metadata']
        statuses = timeline['statuses']
        limit = req.headers['x-rate-limit-remaining'] if 'x-rate-limit-remaining' in req.headers else 0
        reset = req.headers['x-rate-limit-reset'] if 'x-rate-limit-reset' in req.headers else 0
        return {"result":True, "metadata":metadata, "statuses":statuses, "limit":limit, "reset_time":datetime.datetime.fromtimestamp(float(reset)), "reset_time_unix":reset}
    else: # fail
        print ("Error: %d" % req.status_code)
        return{"result":False, "status_code":req.status_code}

def str_to_date_jp(str_date):
    dts = datetime.datetime.strptime(str_date,'%a %b %d %H:%M:%S +0000 %Y')
    return pytz.utc.localize(dts).astimezone(pytz.timezone('Asia/Tokyo'))


def now_unix_time():
    return time.mktime(datetime.datetime.now().timetuple())



#-------------get the tweet data-------------#
sid=-1
mid = -1
count = 0

res = None
while(True):
    try:
        count = count + 1
        sys.stdout.write("%d, "% count)
        res = getTweetData()
        if res['result']==False:
            # break if failed
            print "status_code", res['status_code']
            break

        if int(res['limit']) == 0:
            print "Adding created_at field."
            for d in tweetdata.find({'created_datetime':{ "$exists": False }},{'_id':1, 'created_at':1}):
                tweetdata.update({'_id' : d['_id']},
                     {'$set' : {'created_datetime' : str_to_date_jp(d['created_at'])}})
            diff_sec = int(res['reset_time_unix']) - now_unix_time()
            print "sleep %d sec." % (diff_sec+5)
            if diff_sec > 0:
                time.sleep(diff_sec + 5)
        else:
            # metadata
            if len(res['statuses'])==0:
                sys.stdout.write("statuses is none. ")
            elif 'next_results' in res['metadata']:
                # insert to mogoDB
                meta.insert({"metadata":res['metadata'], "insert_date": now_unix_time()})
                for s in res['statuses']:
                    tweetdata.insert(s)
                next_url = res['metadata']['next_results']
                pattern = r".*max_id=([0-9]*)\&.*"
                ite = re.finditer(pattern, next_url)
                for i in ite:
                    mid = i.group(1)
                    break
            else:
                sys.stdout.write("next is none. finished.")
                break

    except SSLError as (errno, request):
        print "SSLError({0}): {1}".format(errno, strerror)
        print "waiting 5mins"
        time.sleep(5*60)
    except ConnectionError as (errno, request):
        print "ConnectionError({0}): {1}".format(errno, strerror)
        print "waiting 5mins"
        time.sleep(5*60)
    except ReadTimeout as (errno, request):
        print "ReadTimeout({0}): {1}".format(errno, strerror)
        print "waiting 5mins"
        time.sleep(5*60)
    except:
        print "Unexpected error:", sys.exc_info()[0]
        traceback.format_exc(sys.exc_info()[2])
        raise
    finally:
        info = sys.exc_info()
