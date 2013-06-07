import json
import logging
import urllib2

import oauth2 as oauth

from commonutil import dateutil

class TwitterSearcher():

    def __init__(self, comsumerkey, comsumersecret,
                 accesstoken, accesssecret):
        self.comsumerkey = comsumerkey
        self.comsumersecret = comsumersecret
        self.accesstoken = accesstoken
        self.accesssecret = accesssecret

    def _query(self, url):
        consumer = oauth.Consumer(key=self.comsumerkey, secret=self.comsumersecret)
        token = oauth.Token(key=self.accesstoken, secret=self.accesssecret)
        client = oauth.Client(consumer, token)
        try:
            responsehead, responsebody = client.request(
                   url,
                   method='GET',
            )
            if responsehead.get('reason') == 'OK':
                return json.loads(responsebody)
            logging.error('Return value: %s, %s. ' % (
                            responsehead, responsebody,))
        except Exception:
            logging.exception('Failed to query from twitter.')
        return None

    def _getQueryUrl(self, keyword):
        jsonUrl = 'https://api.twitter.com/1.1/search/tweets.json?q={q}&result_type=popular&include_entities=false'
        return jsonUrl.replace('{q}', keyword)

    def search(self, keyword):
        jsonUrl = self._getQueryUrl(keyword)
        return self._query(jsonUrl)

def _pareData(jsonvalue):
    if not jsonvalue or 'statuses' not in jsonvalue:
        return []
    pages = []
    for item in jsonvalue['statuses']:
        page = {
            'content': item['text'],
            'published': dateutil.jsDate2utc14(item['created_at']),
        }
        if 'user' in item and 'name' in item['user']:
            page['publisher'] = item['user']['name']
        pages.append(page)
    return pages

def search(keyword, accountInfo):
    searchEngine = TwitterSearcher(accountInfo['comsumerkey'], accountInfo['comsumersecret'],
                        accountInfo['accesstoken'], accountInfo['accesssecret'])

    return _pareData(searchEngine.search(keyword))

