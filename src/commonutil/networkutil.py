import copy
import json
import logging
import time
import urllib2
import uuid

from configmanager import cmapi

def postData(url, data, tag=None, trycount=1, timeout=10):
    data = copy.deepcopy(data)
    data['uuid'] = str(uuid.uuid4())
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

def isUuidHandled(uuid):
    if not uuid:
        return False
    items = cmapi.getItemValue('~.uuids', [])
    if uuid in items:
        return True
    return False

def updateUuids(uuid):
    _MAX_ITEM_COUNT = 100
    if not uuid:
        return
    items = cmapi.getItemValue('~.uuids', [])
    items.insert(0, uuid)
    items = items[:_MAX_ITEM_COUNT]
    cmapi.saveItem('~.uuids', items)

