# -*- coding: utf-8 -*-
import os
import urllib2
import unittest

from contentfetcher.bs import getEncodingFromContent, getEncodingByChardet

class TestContentFetcher(unittest.TestCase):

    def setUp(self):
        pass

    def _loadTestData(self, filename):
        filepath = os.path.join(os.path.dirname(__file__), 'data', filename)
        with open(filepath, 'r') as f:
            content = f.read()
        return content

    def testEncoding(self):
        content = self._loadTestData('ftchinese-invalid-character.htm')
        encoding = getEncodingFromContent(content)
        self.assertEquals(encoding, 'utf-8')
        contentEncoding = getEncodingFromContent(content)
        chardetEncoding = getEncodingByChardet(content)
        self.assertEquals(contentEncoding, 'utf-8')
        self.assertEquals(chardetEncoding, 'ISO-8859-2')

    """Proxy works as unittest.
       But it does not work when it runs on local GAE or product GAE.
    """
    def atestProxy(self):
        url = 'http://www.myhttp.info/'
        req = urllib2.Request(url)
        req.add_header('User-agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:15.0) Gecko/20100101 Firefox/15.0.1')
        handler = urllib2.ProxyHandler({'http': '127.0.0.1:8087'})
        handler = urllib2.HTTPHandler()
        opener = urllib2.build_opener(handler)
        res = opener.open(req, timeout=30)
        content = res.read()
        res.close()
        self.assertIsNotNone(content)

    def btestBasicFetcher(self):
        url = 'http://www.xinhua.org/'
        fetcher = ContentFetcher(url, timeout=10)
        fetchUrl, fetchEncoding, content = fetcher.fetch()
        self.assertEquals(url, fetchUrl)
        self.assertEquals(fetchEncoding, 'utf-8')
        self.assertIsNotNone(content)

    def ctestBasicFetcherPreventCache(self):
        url = 'http://www.xinhua.org/'
        fetcher = ContentFetcher(url, preventCache=True, timeout=10)
        fetchUrl, fetchEncoding, content = fetcher.fetch()
        self.assertNotEquals(url, fetchUrl)
        self.assertIsNotNone(content)


if __name__ == '__main__':
    unittest.main()

