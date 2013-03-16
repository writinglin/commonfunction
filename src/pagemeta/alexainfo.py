import logging
import urlparse

import lxml

from commonutil import lxmlutil
from contentfetcher import ContentFetcher

def getAlexaInfo(tree):
    alexa = {}
    sds = tree.xpath('/ALEXA/SD')
    if sds:
        sd = sds[0]
        reachRanks = sd.xpath('REACH/@RANK')
        if reachRanks:
            alexa['reach'] = int(reachRanks[0])
        countries = sd.xpath('COUNTRY')
        if countries:
            country = countries[0]
            countrycode = country.get('CODE')
            if countrycode:
                alexa['country'] = countrycode
            countryrank = country.get('RANK')
            if countryrank:
                alexa['countryrank'] = countryrank
    return alexa

def getDmozInfo(tree):
    dmoz = {}
    sites = tree.xpath('/ALEXA/DMOZ/SITE')
    if sites:
        site = sites[0]
        desc = site.get('DESC')
        if desc:
            dmoz['desc'] = desc
        categories = site.xpath('CATS/CAT')
        # 'CATS/CAT/@ID' will return lxml.etree._ElementUnicodeResult
        # but HtmlElement.get(attr) will return normal string
        # TODO: testcase to validate it
        if categories:
            dmoz['categories'] = [lxmlutil.getPureString(category.get('ID'))
                                    for category in categories]
    return dmoz

def fetch(url):
    parseresult = urlparse.urlparse(url)
    queryurl = 'http://data.alexa.com/data?cli=10&url=%s' % (parseresult.netloc, )
    result = {}
    fetcher = ContentFetcher(queryurl, tried=2)
    fetchResult = fetcher.fetch()
    content = fetchResult.get('content')
    if not content:
        return result
    tree = lxmlutil.parseFromUnicode(content)
    alexa = getAlexaInfo(tree)
    if alexa:
        result['alexa'] = alexa
    dmoz = getDmozInfo(tree)
    if dmoz:
        result['dmoz'] = dmoz
    return result

