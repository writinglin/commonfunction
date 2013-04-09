import json
import urllib2

from commonutil import dateutil
from commonutil import htmlutil

def _getUrl(keyword, large):
    jsonUrl = 'http://www.google.com/uds/GnewsSearch?q={q}&v=1.0'
    if large:
        jsonUrl += '&rsz=large'
    return jsonUrl.replace('{q}', urllib2.quote(keyword.encode('utf-8')))

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

def _gnewsItem2Page(item):
    pageItem = {}
    pageItem['title'] = htmlutil.getTextContent(item.get('title'))
    pageItem['url'] = item.get('unescapedUrl')
    pageItem['content'] = htmlutil.getTextContent(item.get('content'))
    pageItem['publisher'] = item.get('publisher')
    pageItem['published'] = dateutil.jsDate2utc14(item.get('publishedDate'))
    if item.get('image'):
        img = {}
        img['url'] = item['image'].get('url')
        img['width'] = item['image'].get('tbWidth')
        img['height'] = item['image'].get('tbHeight')
        pageItem['img'] = img
    return pageItem

def _parseGnews(responseText):
    return _parseGoogle(responseText, _gnewsItem2Page)

def getSearchUrl(keyword):
    searchUrl = 'http://news.google.com/news/search?q={q}'
    return searchUrl.replace('{q}', urllib2.quote(keyword.encode('utf-8')))

def search(keyword, large=False):
    url = _getUrl(keyword, large)
    responseText = _fetch(url)
    pages = None
    trycount = 3
    for _ in range(trycount):
        pages = _parseGnews(responseText)
        if pages is not None:
            break
    return pages or []

