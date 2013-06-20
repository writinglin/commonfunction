"""
Save item value to memcache to improve performance.

Don't take concurrency into condideration. Please take care.
"""
import json
import logging
import random

from google.appengine.api import memcache
from google.appengine.ext import db

from . import models

MAX_ITEM_SIZE = 1024 * 800
PART_KEY_SUFFIX = '.pend'

"""
A class support a config -> an entity in db -> a record in memcache.

"""
class BasicManager(object):

    def __init__(self, modelclass):
        self.modelclass = modelclass

    def _getCacheKey(self, keyname):
        return '%s-%s' % (self.modelclass.kind(), keyname)

    def _getDbKey(self, keyname):
        return keyname

    def getItemValue(self, keyname=None, cachekey=None, dbkey=None,
                        defaultValue=None, jsonType=True):
        if keyname:
            cachekey = self._getCacheKey(keyname)
            dbkey = self._getDbKey(keyname)
        cachevalue = memcache.get(cachekey)
        if cachevalue is None:
            configitem = self.modelclass.get_by_key_name(dbkey)
            if configitem:
                cachevalue = configitem.value
            if cachevalue is None and defaultValue is not None:
                cachevalue = json.dumps(defaultValue)
            if cachevalue is not None:
                memcache.set(cachekey, cachevalue)
        if jsonType and cachevalue is not None:
            cachevalue = json.loads(cachevalue)
        return cachevalue

    def removeItem(self, keyname=None, cachekey=None, dbkey=None):
        if keyname:
            cachekey = self._getCacheKey(keyname)
            dbkey = self._getDbKey(keyname)
        memcache.delete(cachekey)
        keyobj = db.Key.from_path(self.modelclass.kind(), dbkey)
        db.delete(keyobj)
        return True

    def saveItem(self, keyname=None, cachekey=None, dbkey=None,
            jsonvalue=None, strvalue=None):
        if keyname:
            cachekey = self._getCacheKey(keyname)
            dbkey = self._getDbKey(keyname)
        if jsonvalue is None:
            cachevalue = strvalue
            dbvalue = strvalue
        else:
            dbvalue = json.dumps(jsonvalue)
            cachevalue = dbvalue
        item = self.modelclass(key_name=dbkey, value=dbvalue)
        trycount = 3
        success = False
        for i in range(trycount):
            try:
                memcache.set(cachekey, cachevalue)
                item.put()
                success = True
                break
            except Exception:
                logging.exception('Failed to save data, left: %s.' % (trycount - 1 - i,))
        return success


"""
A class supports a config storing as multi parts.
"""
class ConfigManager(BasicManager):

    def __init__(self, modelclass):
        super(ConfigManager, self).__init__(modelclass)

    def getRawItems(self):
        items = {}
        for item in self.modelclass.all():
            dbkey = item.key().name()
            if dbkey.endswith(PART_KEY_SUFFIX):
                continue
            # db key can be used as key name.
            value = self.getItemValue(dbkey)
            items[dbkey] = value
        return items

    def getModelKeys(self):
        items = []
        for item in self.modelclass.all():
            dbkey = item.key().name()
            if dbkey.endswith(PART_KEY_SUFFIX):
                continue
            items.append(dbkey)
        return items

    def _getCacheKey(self, keyname, randomId=None, part=-1):
        cachekey = super(ConfigManager, self)._getCacheKey(keyname)
        if part < 0:
            return cachekey
        if randomId:
            return '%s.%s.%s%s' % (cachekey, randomId, part, PART_KEY_SUFFIX)
        else:
            return '%s.%s%s' % (cachekey, part, PART_KEY_SUFFIX)

    def _getDbKey(self, keyname, randomId=None, part=-1):
        dbkey = super(ConfigManager, self)._getDbKey(keyname)
        if part < 0:
            return dbkey
        if randomId:
            return '%s.%s.%s%s' % (dbkey, randomId, part, PART_KEY_SUFFIX)
        else:
            return '%s.%s%s' % (dbkey, part, PART_KEY_SUFFIX)

    def _getPartCount(self, jsonvalue):
        return jsonvalue.get('partcount')

    def _getRandomId(self, jsonvalue):
        return jsonvalue.get('randomid')

    def _isBigItem(self, jsonvalue):
        return type(jsonvalue) == dict and bool(self._getPartCount(jsonvalue))

    def _isBigCount(self, partcount):
        return partcount > 1

    def getItemValue(self, keyname, defaultValue=None):
        mainValue = super(ConfigManager, self).getItemValue(keyname,
                                defaultValue=defaultValue)
        if not self._isBigItem(mainValue):
            return mainValue
        partcount = self._getPartCount(mainValue)
        randomId = self._getRandomId(mainValue)
        partvalues = []
        for i in range(partcount):
            cachekey = self._getCacheKey(keyname, randomId=randomId, part=i)
            dbkey = self._getDbKey(keyname, randomId=randomId, part=i)
            value = super(ConfigManager, self).getItemValue(
                            cachekey=cachekey, dbkey=dbkey, jsonType=False)
            partvalues.append(value)
        mainstr = ''.join(partvalues)
        return json.loads(mainstr)

    def _removeParts(self, keyname, mainValue):
        if not self._isBigItem(mainValue):
            return True

        partcount = self._getPartCount(mainValue)
        randomId = self._getRandomId(mainValue)
        for i in range(partcount):
            cachekey = self._getCacheKey(keyname, randomId=randomId, part=i)
            dbkey = self._getDbKey(keyname, randomId=randomId, part=i)
            super(ConfigManager, self).removeItem(
                            cachekey=cachekey, dbkey=dbkey)
        return True

    def removeItem(self, keyname):
        mainValue = super(ConfigManager, self).getItemValue(keyname)
        super(ConfigManager, self).removeItem(keyname)
        self._removeParts(keyname, mainValue)
        return True

    def _getPartCountByStr(self, strvalue):
        valuelen = len(strvalue)
        partcount = valuelen / MAX_ITEM_SIZE
        if valuelen % MAX_ITEM_SIZE != 0:
            partcount += 1
        return partcount

    def saveItem(self, keyname, jsonvalue):
        oldMainValue = super(ConfigManager, self).getItemValue(keyname)

        strvalue = json.dumps(jsonvalue)
        newPartCount = self._getPartCountByStr(strvalue)

        success = True
        if self._isBigCount(newPartCount):
            # random id is used to avoid data corruption,
            # (by concurrent visit or failure on some step).
            oldRandomId = None
            if self._isBigItem(oldMainValue):
                oldRandomId = self._getRandomId(oldMainValue)
            while True:
                randomId = random.randint(0, 1000)
                if randomId == oldRandomId:
                    logging.warn('Same random id: %s.' % (oldRandomId, ))
                else:
                    break
            valuelen = len(strvalue)
            mainJson = {
                    'partcount': newPartCount,
                    'size': valuelen,
                    'randomid': randomId,
                }
            for i in range(newPartCount):
                cachekey = self._getCacheKey(keyname, randomId=randomId, part=i)
                dbkey = self._getDbKey(keyname, randomId=randomId, part=i)
                value = strvalue[MAX_ITEM_SIZE * i:
                            min(valuelen, MAX_ITEM_SIZE * (i + 1))]
                if not super(ConfigManager, self).saveItem(cachekey=cachekey,
                                            dbkey=dbkey, strvalue=value):
                    success = False
                    break
            if success:
                if not super(ConfigManager, self).saveItem(keyname, jsonvalue=mainJson):
                    success = False
                    self._removeParts(keyname, mainJson)
        else:
            if not super(ConfigManager, self).saveItem(keyname, jsonvalue=jsonvalue):
                success = False

        # remove the unreferenced part entities.
        if success:
            self._removeParts(keyname, oldMainValue)
        return success

DEFAULT_MANAGER = None
REGISTERED_MODELS = {
}

def registerModel(modelclass):
    global DEFAULT_MANAGER
    manager = ConfigManager(modelclass)
    if not DEFAULT_MANAGER:
        DEFAULT_MANAGER = manager
    REGISTERED_MODELS[modelclass.__name__] = manager

def getModelNames():
    return REGISTERED_MODELS.keys()

def _getManager(modelname):
    if not modelname:
        return DEFAULT_MANAGER
    if not isinstance(modelname, basestring):
        modelname = modelname.__name__
    return REGISTERED_MODELS[modelname]

def getRawItems(modelname=None):
    return _getManager(modelname).getRawItems()

def getModelKeys(modelname=None):
    return _getManager(modelname).getModelKeys()

def getItemValue(keyname, defaultValue=None, modelname=None):
    return _getManager(modelname).getItemValue(keyname, defaultValue)

def saveItem(keyname, jsonvalue, modelname=None):
    return _getManager(modelname).saveItem(keyname, jsonvalue)

def removeItem(keyname, modelname=None):
    return _getManager(modelname).removeItem(keyname)

registerModel(models.ConfigItem)
registerModel(models.RunStatus)

