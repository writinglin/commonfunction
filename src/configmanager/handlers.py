import logging
import os

from google.appengine.ext.webapp import template
import webapp2

import jsonpickle

from . import cmapi

class MainPage(webapp2.RequestHandler):

    def _render(self, templateValues):
        self.response.headers['Content-Type'] = 'text/html'
        path = os.path.join(os.path.dirname(__file__), 'templates', 'index.html')
        self.response.out.write(template.render(path, templateValues))

    def get(self, message=''):
        if self.request.get('action') == 'Add':
            key = self.request.get('key')
        else:
            key = self.request.get('selectedkey')
        value = ''

        modelname = self.request.get('modelname')
        if modelname:
            items = cmapi.getRawItems(modelname=modelname)
            keys = []
            for item in items:
                keys.append(item['key'])
                if key and item['key'] == key:
                    value = item['value']
            keys.sort()
        else:
            keys = []
            items = []
            message = 'Please select a model'


        if self.request.get('action') == 'Remove':
            key = ''
            value = ''

        modelnames = cmapi.getModelNames()

        templateValues = {
            'modelname': modelname,
            'modelnames': modelnames,
            'key': key,
            'value': value,
            'keys': keys,
            'items': items,
            'message': message,
        }
        self._render(templateValues)

    def post(self):
        modelname = self.request.get('modelname')
        if not modelname:
            self.get()
            return

        if self.request.get('action') == 'Add':
            key = self.request.get('key')
        else:
            key = self.request.get('selectedkey')

        value = self.request.get('value')
        message = ''
        action = self.request.get('action')
        try:
            if action == 'Remove':
                if not cmapi.removeItem(key, modelname=modelname):
                    message = 'Failed to delete value from cache and db.'
            elif action in ['Add', 'Update', ]:
                jsonvalue = jsonpickle.decode(value)
                if not cmapi.saveItem(key, jsonvalue, modelname=modelname):
                    message = 'Failed to put value into cache and db.'
        except ValueError:
            message = 'Failed to decode the input value.'
        self.get(message=message)

