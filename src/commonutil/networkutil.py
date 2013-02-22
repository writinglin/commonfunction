import json
import logging
import time
import urllib2

def postData(url, data, tag=None, trycount=1, timeout=10):
    success = False
    jsonData = json.dumps(data)
    for i in range(trycount):
        try:
            f = urllib2.urlopen(url, jsonData, timeout=timeout)
            f.read()
            f.close()
            success = True
            break
        except Exception:
            leftcount = trycount - i - 1
            logging.exception('Failed to post data for %s, %s, lefted %s.' % (
                               url, tag, leftcount, ))
            if leftcount > 0:
                time.sleep(1)
    return success

