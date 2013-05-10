import logging

from google.appengine.api import users
import webapp2
from webapp2_extras import jinja2

class BasicHandler(webapp2.RequestHandler):
    site = {}
    i18n = {}
    extraValues = {}

    @webapp2.cached_property
    def jinja2(self):
        return jinja2.get_jinja2(app=self.app)

    def dispatch(self):
        self.prepareBaseValues()
        if self.doRedirection():
            return
        if self._redirectByDomain():
            return
        self.prepareValues()
        super(BasicHandler, self).dispatch()

    def render(self, templateValues, template, contentType='text/html'):
        self.response.headers['Content-Type'] = contentType
        templateValues['request'] = self.request
        user = users.get_current_user()
        if user:
            templateValues['user'] = user
        templateValues['site'] = self.site
        templateValues['i18n'] = self.i18n
        if self.extraValues:
            for key, value in self.extraValues.iteritems():
                if key not in templateValues:
                    templateValues[key] = value
        templateValues['request'] = self.request
        content = self.jinja2.render_template(template, **templateValues)
        self.response.out.write(content)

    def doRedirection(self):
        return False

    def prepareBaseValues(self):
        pass

    def prepareValues(self):
        pass

    def _redirectByDomain(self):
        if self.site:
            domain = self.site.get('domain')
        else:
            domain = None
        if domain:
            hosturl = self.request.host_url
            if not hosturl.startswith(domain):
                path = self.request.path
                redirecturl = str(domain) + path
                querystring = self.request.query_string
                if querystring:
                    redirecturl += '?' + querystring
                url = self.request.url
                logging.info('Redirect form %s to %s.' % (url, redirecturl))
                self.redirect(redirecturl, permanent=True)
                return True
        return False

