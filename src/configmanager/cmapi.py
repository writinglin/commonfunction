"""
Save item value to memcache to improve performance.
"""
import logging
from google.appengine.api import memcache
from google.appengine.ext import db

import jsonpickle

from . import models

class ConfigManager(object):

    def __init__(self, modelclass):
        self.modelclass = modelclass

    def getRawItems(self):
        items = []
        for item in self.modelclass.all():
            items.append({'key': item.key().name(), 'value': item.value,})
        return items

    def _getCacheKey(self, keyname):
        return '%s-%s' % (self.modelclass.kind(), keyname)

    # thread safe visit to cache
    def _setCache(self, cachekey, jsonvalue):
        client = memcache.Client()
        oldvalue = client.gets(cachekey)
        success = False
        if not oldvalue:
            memcache.set(cachekey, jsonvalue)
            success = True
        else:
            if client.cas(cachekey, jsonvalue):
                success = True
        return success

    def getItemValue(self, keyname, defaultValue=None):
        cachekey = self._getCacheKey(keyname)
        jsonvalue = memcache.get(cachekey)
        if not jsonvalue:
            configitem = self.modelclass.get_by_key_name(keyname)
            if not configitem:
                return defaultValue
            jsonvalue = jsonpickle.decode(configitem.value)
            self._setCache(cachekey, jsonvalue)
        return jsonvalue

    def saveItem(self, keyname, jsonvalue):
        cachekey = self._getCacheKey(keyname)
        if not jsonvalue:
            return True
        success = self._setCache(cachekey, jsonvalue)
        if success:# if we fail to save value to cache, we should not put it into db.
            strvalue = jsonpickle.encode(jsonvalue)
            item = self.modelclass(key_name=keyname, value=strvalue)
            item.put()
        return success

    def removeItem(self, keyname):
        cachekey = self._getCacheKey(keyname)
        memcache.delete(cachekey)
        keyobj = db.Key.from_path(self.modelclass.kind(), keyname)
        db.delete(keyobj)
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

