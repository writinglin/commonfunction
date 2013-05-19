import copy
import json
import logging
import time
import urllib2
import uuid

from configmanager import cmapi, models

def postData(url, data, tag=None, trycount=1, timeout=10, feedback=None):
    data = copy.deepcopy(data)
    data['uuid'] = str(uuid.uuid4())
    success = False
    jsonData = json.dumps(data)
    for i in range(trycount):
        try:
            f = urllib2.urlopen(url, jsonData, timeout=timeout)
            returncode = f.getcode()
            f.read()
            f.close()
            if feedback is not None and returncode != 200:
                logging.error('servererror happens: %s.' % (url, ))
                feedback['servererror'] = True
            else:
                success = True
            break
        except urllib2.HTTPError, e:
            if feedback is not None:
                logging.error('servererror happens: %s, %s.' % (url, e.code))
                feedback['servererror'] = True
            break
        except Exception, e:
            leftcount = trycount - i - 1
            logging.exception('Failed to post data for %s, %s, lefted %s: %s.' % (
                               url, tag, leftcount, type(e)))
            if leftcount > 0:
                time.sleep(1)
    return success

def isUuidHandled(uuid):
    if not uuid:
        return False
    items = cmapi.getItemValue('uuids', [], modelname='RunStatus')
    if uuid in items:
        return True
    return False

def updateUuids(uuid):
    _MAX_ITEM_COUNT = 100
    if not uuid:
        return
    items = cmapi.getItemValue('uuids', [], modelname='RunStatus')
    items.insert(0, uuid)
    items = items[:_MAX_ITEM_COUNT]
    cmapi.saveItem('uuids', items, modelname='RunStatus')

