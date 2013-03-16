# Google Pagerank Checksum Algorithm (Firefox Toolbar)
# Downloaded from http://pagerank.phurix.net/
# Requires: Python >= 2.4

# Versions:
# pagerank2.py 0.2 - Fixed a minor formatting bug
# pagerank2.py 0.1 - Public release
import httplib
import logging
import re
import urlparse

# Settings
# toolbarqueries.google.com will forward request to
#    toolbarqueries.google.com.hk if it finds the request
#    is from cn.
prhost = 'toolbarqueries.google.com.hk'
prpath = '/tbr?client=navclient-auto&ch=%s&features=Rank&q=info:%s'

_PATTERN_MATCH_RESULT = re.compile(r'Rank_\d+:\d+:(\d+)', re.IGNORECASE|re.DOTALL)

# Function definitions
def getHash(query):
    SEED = """Mining PageRank is AGAINST GOOGLE'S TERMS OF SERVICE. Yes, I'm talking to you, scammer."""
    Result = 0x01020345
    for i in range(len(query)):
        Result ^= ord(SEED[i%len(SEED)]) ^ ord(query[i])
        Result = Result >> 23 | Result << 9
        Result &= 0xffffffff
    return '8%x' % Result

def fetch(url):
    parseresult = urlparse.urlparse(url)
    query = parseresult.netloc
    conn = httplib.HTTPConnection(prhost)
    hash = getHash(query)
    path = prpath % (hash, query)
    data = None
    try:
        conn.request('GET', path)
        response = conn.getresponse()
        data = response.read()
        conn.close()
    except Exception:
        logging.exception('Failed to get page rank for %s.' % (query, ))
    result = -1
    if data:
        data = data.strip()
        matched = _PATTERN_MATCH_RESULT.match(data)
        if matched:
            result = int(matched.group(1))
    return result

