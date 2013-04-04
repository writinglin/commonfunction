import datetime
import json
import math
import urllib2

from commonutil import dateutil
from commonutil import htmlutil

def _getJulian(utcdate):
    a = (14 - utcdate.month) // 12
    y = utcdate.year + 4800 - a
    m = utcdate.month + 12 * a - 3
    num = utcdate.day + ((153 * m + 2) // 5) + 365 * y + y // 4 - y // 100 + y // 400 - 32045
    num = num + (utcdate.hour * 60 + utcdate.minute * 1.0) / 1440 - 0.5
    return num

def getGoogleJulianQuestion(value):
    # google datarange require integer, and 'daterange:2455621-2455621' means a whole day
    today = datetime.datetime.utcnow()
    today_julian_f = _getJulian(today)
    today_julian = math.floor(today_julian_f)
    # fraction = today_julian_f - today_julian
    start_julian = today_julian - 1
    return value + ' daterange:' + str(int(start_julian)) + '-' + str(int(today_julian))

def _getUrl(keyword):
    jsonUrl = 'http://ajax.googleapis.com/ajax/services/search/web?v=1.0&q={q}'
    julianQ = getGoogleJulianQuestion(keyword)
    return jsonUrl.replace('{q}', urllib2.quote(julianQ.encode('utf-8')))

def _fetch(url):
    try:
        req = urllib2.Request(url)
        res = urllib2.urlopen(req)
        content = res.read()
        res.close()
        responseText = content
    except Exception:
        responseText = None
    return responseText

def _parseGoogle(responseText, item2page):
    if not responseText:
        return None
    data = json.loads(responseText)
    if not data or not data.get('responseData') or 'results' not in data['responseData']:
        return None
    pages = []
    for item in data['responseData']['results']:
        pageItem = item2page(item)
        if pageItem:
            pages.append(pageItem)
    return pages

def _googleItem2page(item):
    pageItem = {}
    pageItem['title'] = htmlutil.getTextContent(item.get('title'))
    pageItem['url'] = item.get('unescapedUrl')
    pageItem['content'] = htmlutil.getTextContent(item.get('content'))
    return pageItem

def _parseGnews(responseText):
    return _parseGoogle(responseText, _googleItem2page)

def search(keyword):
    url = _getUrl(keyword)
    responseText = _fetch(url)
    return _parseGnews(responseText)

