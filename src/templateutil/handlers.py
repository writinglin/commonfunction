import logging

from google.appengine.api import users
import webapp2
from webapp2_extras import jinja2
from webapp2_extras import sessions

class BasicHandler(webapp2.RequestHandler):
    site = {}
    i18n = {}
    extraValues = {}

    @webapp2.cached_property
    def jinja2(self):
        return jinja2.get_jinja2(app=self.app)

    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)

        try:
            # Dispatch the request.
            self.prepareBaseValues()
            if self.doRedirection():
                return
            if self._redirectByDomain():
                return
            self.prepareValues()
            super(BasicHandler, self).dispatch()
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session()

    def render(self, templateValues, template, contentType='text/html'):
        self.response.headers['Content-Type'] = contentType
        templateValues['request'] = self.request
        user = users.get_current_user()
        analytics_code = self.site.get('analytics_code')
        if user:
            templateValues['user'] = user
            templateValues['user_admin'] = users.is_current_user_admin()
            if users.is_current_user_admin():
                analytics_code = None
            templateValues['logout_url'] = users.create_logout_url('/')
        if self.session.get('ga'):
            analytics_code = None
        elif 'ga' in self.request.GET:
            self.session['ga'] = True
            analytics_code = None
        elif self.request.path.startswith('/admin/'):
            analytics_code = None
        templateValues['site'] = self.site
        templateValues['i18n'] = self.i18n
        templateValues['analytics_code'] = analytics_code
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

