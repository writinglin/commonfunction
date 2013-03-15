
import lxml
import pyquery

from contentfetcher import ContentFetcher

def fetch(url):
    result = {}
    fetcher = ContentFetcher(url, tried=2)
    fetchResult = fetcher.fetch()
    content = fetchResult.get('content')
    if not content:
        return result
    htmlelement = lxml.html.fromstring(content)
    match = pyquery.PyQuery(htmlelement)('head meta[name=keywords]')
    if match:
        mainElement = match[0]
        keywords = mainElement.get('content')
        if keywords:
            result['keywords'] = keywords
    match = pyquery.PyQuery(htmlelement)('head meta[name=description]')
    if match:
        mainElement = match[0]
        description = mainElement.get('content')
        if description:
            result['description'] = description
    match = pyquery.PyQuery(htmlelement)('head title')
    if match:
        mainElement = match[0]
        title = mainElement.text_content()
        if title:
            result['title'] = title
    return result

