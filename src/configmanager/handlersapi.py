import json
import logging

import webapp2

from . import cmapi

class ModelData(webapp2.RequestHandler):

    def get(self):
        modelname = self.request.get('model')
        items = cmapi.getRawItems(modelname=modelname)
        data = {
            'model': modelname,
            'items': items,
        }
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(data))

    def post(self):
        data = json.loads(self.request.body)
        modelname = data.get('model')
        items = data.get('items')
        for key, value in items.iteritems():
            cmapi.saveItem(keyname=key, jsonvalue=value, modelname=modelname)
        result = {
            'success': True
        }
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(result))

