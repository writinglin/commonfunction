import datetime
import logging

from commonutil import dateutil

from . import pageinfo
from . import alexainfo
from . import pagerankinfo

def getPage(url):
    result = {}
    pageInfo = pageinfo.fetch(url)
    if pageInfo:
        result['page'] = pageInfo

    alexaInfo = alexainfo.fetch(url)
    if alexaInfo:
        if 'alexa' in alexaInfo:
            result['alexa'] = alexaInfo['alexa']
        if 'dmoz' in alexaInfo:
            result['dmoz'] = alexaInfo['dmoz']

    pagerank = pagerankinfo.fetch(url)
    if pagerank >= 0:
        result['pagerank'] = pagerank

    if result:
        result['updated'] = dateutil.getDateAs14(datetime.datetime.utcnow())
    return result

