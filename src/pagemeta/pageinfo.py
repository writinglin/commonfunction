import logging
import lxml
import pyquery

from commonutil import lxmlutil
from contentfetcher import ContentFetcher

def fetch(url):
    result = {}
    fetcher = ContentFetcher(url, tried=2)
    fetchResult = fetcher.fetch()
    content = fetchResult.get('content')
    if not content:
        return result
    try:
        htmlelement = lxml.html.fromstring(content)
    except Exception:
        logging.error('Failed to load html from content.')
        return result
    match = pyquery.PyQuery(htmlelement)('head meta[name=keywords]')
    if match:
        mainElement = match[0]
        keywords = mainElement.get('content')
        if keywords:
            result['keywords'] = lxmlutil.getPureString(keywords)
    match = pyquery.PyQuery(htmlelement)('head meta[name=description]')
    if match:
        mainElement = match[0]
        description = mainElement.get('content')
        if description:
            result['description'] = lxmlutil.getPureString(description)
    match = pyquery.PyQuery(htmlelement)('head title')
    if match:
        mainElement = match[0]
        title = mainElement.text_content()
        if title:
            result['title'] = lxmlutil.getPureString(title)
    return result

