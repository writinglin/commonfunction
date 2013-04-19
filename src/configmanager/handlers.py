import json
import logging
import os

from google.appengine.ext.webapp import template
import webapp2

from . import cmapi

class MainPage(webapp2.RequestHandler):

    def _render(self, templateValues):
        self.response.headers['Content-Type'] = 'text/html'
        path = os.path.join(os.path.dirname(__file__), 'templates', 'index.html')
        self.response.out.write(template.render(path, templateValues))

    def get(self, message='', key=''):
        if not key:
            key = self.request.get('selectedkey')
        value = ''

        modelname = self.request.get('modelname')
        if modelname:
            items = cmapi.getRawItems(modelname=modelname)
            if key:
                for item in items:
                    if item['key'] == key:
                        value = item['value']
                        break
        else:
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
            'items': items,
            'message': message,
        }
        self._render(templateValues)

    def post(self):
        modelname = self.request.get('modelname')
        if not modelname:
            self.get()
            return

        action = self.request.get('action')

        if action == 'Save':
            key = self.request.get('key')
        else:
            key = self.request.get('selectedkey')

        if not key:
            message = 'Key must not be empty.'
            return self.get(message=message)

        value = self.request.get('value')
        message = ''
        try:
            if action == 'Remove':
                if not cmapi.removeItem(key, modelname=modelname):
                    message = 'Failed to delete value from cache and db.'
                key = ''
            elif action == 'Save':
                jsonvalue = json.loads(value)
                if not cmapi.saveItem(key, jsonvalue, modelname=modelname):
                    message = 'Failed to put value into cache and db.'
        except ValueError:
            message = 'Failed to decode the input value.'
        self.get(message=message, key=key)

