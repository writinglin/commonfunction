# -*- coding: utf-8 -*-
import base64
import logging
import re
import urllib2
import urlparse

import chardet
import lxml.html

from commonutil import statistics

import contentfetcher.config as globalconfig

_PATTERN_MATCH_BODY = re.compile(r'^(.+)<body', re.IGNORECASE|re.DOTALL)
_PATTERN_MATCH_CONTENTTYPE = re.compile(r'<meta[^>]+http\-equiv="Content\-Type"[^>]+content="([^"]+)"[^>]*>', re.IGNORECASE|re.DOTALL)
_PATTERN_MATCH_ENCODING = re.compile(r'<meta[^>]+charset="([^>]+)"[^>]*>', re.IGNORECASE|re.DOTALL)
_PATTERN_MATCH_REFRESH_URL = re.compile(r'<meta http-equiv="refresh"[^>]+content="(\d+);[^>]*URL=([^>]+)"[^>]*>', re.IGNORECASE)

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
    headerContent = None
    m = _PATTERN_MATCH_BODY.search(content)
    if m:
        headerContent = m.group(1)
    else:
        headerContent = content
    m = _PATTERN_MATCH_CONTENTTYPE.search(headerContent)
    if m:
        contentType = m.group(1)
        return _getEncodingFromContentType(contentType)
    else:
        m = _PATTERN_MATCH_ENCODING.search(headerContent)
        if m:
            return m.group(1).strip()
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

    def _fetch(self, fetchUrl):
        encodingUsed = self.encoding
        encodingSrc = 'self'
        try:
            req = urllib2.Request(fetchUrl)
            self.authenticate(req)
            if self.useragent:
                req.add_header('User-agent', self.useragent)
            if self.header:
                for key, value in self.header.iteritems():
                    req.add_header(key, value)
            handler = urllib2.HTTPHandler()
            opener = urllib2.build_opener(handler)
            res = opener.open(req, timeout=self.timeout)
            # httpheaderEncoding = getEncodingFromResponse(res)
            content = res.read()
            res.close()

            # encoding in page content is specified by developer,
            # and we'd better trust developer.

            # chardet can mislead by some mistaken character which is invisible for user.
            # http://www.ftchinese.com/story/001047706 is an example
            if not encodingUsed:
                contentEncoding = getEncodingFromContent(content)
                encodingSrc = 'content'
                encodingUsed = contentEncoding
            if not encodingUsed:
                chardetEncoding = getEncodingByChardet(content)
                encodingUsed = chardetEncoding
                encodingSrc = 'chardet'
            if not encodingUsed:
                encodingUsed = 'UTF-8'
                encodingSrc = 'default'
            ucontent = unicode(content, encodingUsed, 'ignore')
        except Exception, err:
            response = 'Error on fetching data from %s.' % (self.url, )
            logging.exception(response)
            ucontent = ''
        return fetchUrl, encodingSrc, encodingUsed, ucontent

    def fetch(self):
        oldContent = None
        fetchUrl = self.url
        _MAX_REDIRECT_COUNT = 10
        for i in range(_MAX_REDIRECT_COUNT):
            fetchUrl, encodingSrc, encodingUsed, content = self._fetch(fetchUrl)
            if not content:
                break
            statistics.increaseIncomingBandwidth(len(content))
            m = _PATTERN_MATCH_REFRESH_URL.search(content)
            if not m:
                break
            seconds = int(m.group(1).strip())
            redirectUrl = m.group(2).strip()
            if seconds < 10:
                redirectUrl = urlparse.urljoin(fetchUrl, redirectUrl)
                logging.info('Redirect to: %s; old content length: %s.' %
                                (redirectUrl, len(content)))
                oldContent = content
                fetchUrl = redirectUrl
        return {
            'url': fetchUrl,
            'encoding': encodingUsed,
            'encoding.src': encodingSrc,
            'content': content,
            'content.old': oldContent,
        }

class BasicAuthContentFetcher(ContentFetcher):
    def __init__(self, url, username, password, encoding=None):
        super(BasicAuthContentFetcher, self).__init__(url, encoding=encoding)
        self.username = username
        self.password = password

    def authenticate(self, req):
        base64string = base64.encodestring('%s:%s' % (self.username, self.password))[:-1]
        authheader =  'Basic %s' % base64string
        req.add_header('Authorization', authheader)

