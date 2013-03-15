import datetime
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

    # pagerankInfo = pagerankinfo.fetch(url)
    # if pagerankInfo:
    #    result['pagerank'] = pagerankInfo

    if result:
        result['updated'] = datetime.datetime.utcnow()
    return result

