import webapp2
import os
import sys

_ROOT_SRC = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(os.path.join(_ROOT_SRC, 'library'))

import configmanager.handlers
import configmanager.handlersapi

try:
    import cmadmin
except ImportError:
    pass

config = {}
config['webapp2_extras.jinja2'] = {
    'template_path': os.path.join(_ROOT_SRC, 'html', 'templates-config'),
}

config['webapp2_extras.sessions'] = {
    'secret_key': 'dsdfsdfdsffds',
}

app = webapp2.WSGIApplication([
('/admin/config/', configmanager.handlers.MainPage),
('/admin/config/api/', configmanager.handlersapi.ModelData),
],
debug=os.environ['SERVER_SOFTWARE'].startswith('Dev'), config=config)

