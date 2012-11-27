# -*- coding: utf-8 -*-
import base64
import logging
import urllib2

import chardet
import lxml.html

import contentfetcher.config as globalconfig

def _getEncodingFromContentType(contentType):
    if not contentType:
        return None
    parts = contentType.split('charset=', 1)
    if len(parts) > 1:
        return parts[1].strip()
    return None

def getEncodingFromResponse(res):
    contentType = res.info().getheader('Content-Type')
    return _getEncodingFromContentType(contentType)

def getEncodingFromContent(content):
    doc = lxml.html.fromstring(content)
    logging.info('49')
    nodes = doc.findall("//meta")
    logging.info('44')
    for node in nodes:
        logging.info('40')
        equiv = node.attrib.get('http-equiv')
        logging.info('4')
        if equiv.lower() == 'content-type':
            contentType = node.text_content()
            return _getEncodingFromContentType(contentType)
    return None

def getEncodingByChardet(content):
    detectResult = chardet.detect(content)
    if detectResult:
        return detectResult['encoding']
    return None

class ContentFetcher(object):
    def __init__(self, url, header=None, encoding=None, tried=0):
        self.url = url
        self.header = header if header else {}
        self.encoding = encoding

        self.useragent = globalconfig.getUserAgent()
        defaultTimeout = globalconfig.getFetchTimeout()
        self.timeout = defaultTimeout * (tried + 1)

    def authenticate(self, req):        
        pass

    def fetch(self):
        fetchUrl = None
        encodingUsed = None
        try:
            fetchUrl = self.url
            req = urllib2.Request(fetchUrl)
            self.authenticate(req)
            if self.useragent:
                req.add_header('User-agent', self.useragent)
            for key, value in self.header.iteritems():
                req.add_header(key, value)
            handler = urllib2.HTTPHandler()
            opener = urllib2.build_opener(handler)
            res = opener.open(req, timeout=self.timeout)
            httpheaderEncoding = getEncodingFromResponse(res)
            content = res.read()
            res.close()
            # contentEncoding = getEncodingFromContent(content)
            chardetEncoding = getEncodingByChardet(content)
            ucontent = None
            encodings = [httpheaderEncoding, chardetEncoding]
            for encoding in encodings:
                if not encoding:
                    continue
                try:
                    ucontent = unicode(content, encoding)
                    encodingUsed = encoding
                    break
                except:
                    pass
            if not ucontent and chardetEncoding:
                ucontent = unicode(content, chardetEncoding, 'ignore')
                encodingUsed = chardetEncoding
            return fetchUrl, encodingUsed, ucontent
        except Exception, err:
            response = 'Error on fetching data from %s.' % (self.url, )
            logging.exception(response)
            return fetchUrl, encodingUsed, ''

class BasicAuthContentFetcher(ContentFetcher):
    def __init__(self, url, username, password, encoding=None):
        super(BasicAuthContentFetcher, self).__init__(url, encoding=encoding)
        self.username = username
        self.password = password

    def authenticate(self, req):
        base64string = base64.encodestring('%s:%s' % (self.username, self.password))[:-1]
        authheader =  'Basic %s' % base64string
        req.add_header('Authorization', authheader)

