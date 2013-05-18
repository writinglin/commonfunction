import json
import logging

from commonutil import jsonutil
from templateutil.handlers import BasicHandler
from . import cmapi

class MainPage(BasicHandler):

    def prepareBaseValues(self):
        self.site = cmapi.getItemValue('site', {'name': 'Site Name'})
        self.i18n = cmapi.getItemValue('i18n', {'home': 'Home'})

    def get(self, message='', key=''):
        modelnames = cmapi.getModelNames()
        modelnames.sort()

        if not key:
            key = self.request.get('selectedkey')

        modelname = self.request.get('modelname')
        if modelname:
            modelkeys = cmapi.getModelKeys(modelname=modelname)
            modelkeys.sort()
            if key:
                value = cmapi.getItemValue(key, modelname=modelname)
                value = jsonutil.getReadableString(value)
            else:
                value = ''
        else:
            modelkeys = []
            value = ''
            message = 'Please select a model'


        if self.request.get('action') == 'Remove':
            key = ''
            value = ''

        templateValues = {
            'modelname': modelname,
            'modelnames': modelnames,
            'modelkeys': modelkeys,
            'key': key,
            'value': value,
            'message': message,
        }
        self.render(templateValues, 'index.html')

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

