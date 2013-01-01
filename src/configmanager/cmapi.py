"""
Save item value to memcache to improve performance.

Don't take concurrency into condideration. Please take care.
"""
import logging
from google.appengine.api import memcache
from google.appengine.ext import db

import jsonpickle

from commonutil import jsonutil
from . import models

MAX_ITEM_SIZE = 1024 * 900
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
        if cachevalue is not None:
            return cachevalue
        configitem = self.modelclass.get_by_key_name(dbkey)
        if configitem:
            if jsonType:
                cachevalue = jsonpickle.decode(configitem.value)
            else:
                cachevalue = configitem.value
        logging.info('%s, %s' % (cachevalue, defaultValue))
        if cachevalue is None:
            cachevalue = defaultValue
        memcache.set(cachekey, cachevalue)
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
            cachevalue = jsonvalue
            dbvalue = jsonpickle.encode(jsonvalue)
        memcache.set(cachekey, cachevalue)
        item = self.modelclass(key_name=dbkey, value=dbvalue)
        item.put()
        return True


"""
A class supports a config storing as multi parts.
"""
class ConfigManager(BasicManager):

    def __init__(self, modelclass):
        super(ConfigManager, self).__init__(modelclass)

    def getRawItems(self):
        items = []
        for item in self.modelclass.all():
            dbkey = item.key().name()
            if dbkey.endswith(PART_KEY_SUFFIX):
                continue
            # db key can be used as key name.
            value = self.getItemValue(dbkey)
            fstr = jsonutil.getReadableString(value)
            items.append({'key': dbkey, 'value': fstr,})
        return items

    def _getCacheKey(self, keyname, part=-1):
        cachekey = super(ConfigManager, self)._getCacheKey(keyname)
        if part < 0:
            return cachekey
        return '%s.%s%s' % (cachekey, part, PART_KEY_SUFFIX)

    def _getDbKey(self, keyname, part=-1):
        dbkey = super(ConfigManager, self)._getDbKey(keyname)
        if part < 0:
            return dbkey
        return '%s.%s%s' % (dbkey, part, PART_KEY_SUFFIX)

    def _getPartCount(self, jsonvalue):
        return jsonvalue.get('partcount')

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
        partvalues = []
        for i in range(partcount):
            cachekey = self._getCacheKey(keyname, part=i)
            dbkey = self._getCacheKey(keyname, part=i)
            value = super(ConfigManager, self).getItemValue(
                            cachekey=cachekey, dbkey=dbkey, jsonType=False)
            partvalues.append(value)
        mainstr = ''.join(partvalues)
        return jsonpickle.decode(mainstr)

    def _getPartCountByKey(self, keyname):
        mainValue = super(ConfigManager, self).getItemValue(keyname)
        if not mainValue:
            return 0
        if self._isBigItem(mainValue):
            return self._getPartCount(mainValue)
        return 1

    def _removePartItem(self, keyname, part):
        cachekey = self._getCacheKey(keyname, part=part)
        dbkey = self._getDbKey(keyname, part=part)
        super(ConfigManager, self).removeItem(
                        cachekey=cachekey, dbkey=dbkey)

    def removeItem(self, keyname):
        partcount = self._getPartCountByKey(keyname)
        super(ConfigManager, self).removeItem(keyname)
        if not self._isBigCount(partcount):
            return True
        for i in range(partcount):
            self._removePartItem(keyname, i)
        return True

    def _getPartCountByStr(self, strvalue):
        valuelen = len(strvalue)
        partcount = valuelen / MAX_ITEM_SIZE
        if valuelen % MAX_ITEM_SIZE != 0:
            partcount += 1
        return partcount

    def saveItem(self, keyname, jsonvalue):
        oldPartCount = self._getPartCountByKey(keyname)

        strvalue = jsonpickle.encode(jsonvalue)
        newPartCount = self._getPartCountByStr(strvalue)

        # remove the unreferenced part entities.
        if self._isBigCount(oldPartCount) and newPartCount < oldPartCount:
            if self._isBigCount(newPartCount):
                deleteStart = newPartCount
            else:
                deleteStart = 0
            for i in range(deleteStart, oldPartCount):
                self._removePartItem(keyname, i)

        if not self._isBigCount(newPartCount):
            super(ConfigManager, self).saveItem(keyname, jsonvalue=jsonvalue)
            return True

        valuelen = len(strvalue)

        mainJson = {'partcount': newPartCount, 'size': valuelen}
        super(ConfigManager, self).saveItem(keyname, jsonvalue=mainJson)

        for i in range(newPartCount):
            cachekey = self._getCacheKey(keyname, i)
            dbkey = self._getDbKey(keyname, i)
            value = strvalue[MAX_ITEM_SIZE * i:
                        min(valuelen, MAX_ITEM_SIZE * (i + 1))]
            super(ConfigManager, self).saveItem(cachekey=cachekey,
                                        dbkey=dbkey, strvalue=value)

        return True

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

def getItemValue(keyname, defaultValue=None, modelname=None):
    return _getManager(modelname).getItemValue(keyname, defaultValue)

def saveItem(keyname, jsonvalue, modelname=None):
    return _getManager(modelname).saveItem(keyname, jsonvalue)

def removeItem(keyname, modelname=None):
    return _getManager(modelname).removeItem(keyname)

registerModel(models.ConfigItem)

