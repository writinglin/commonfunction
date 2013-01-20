import webapp2
from webapp2_extras import jinja2

class BasicHandler(webapp2.RequestHandler):

    @webapp2.cached_property
    def jinja2(self):
        return jinja2.get_jinja2(app=self.app)

    def getExtraValues(self):
        return None

    def render(self, templateValues, template, contentType='text/html'):
        self.response.headers['Content-Type'] = contentType
        extraValues = self.getExtraValues()
        if extraValues:
            for key, value in extraValues.iteritems():
                if key not in templateValues:
                    templateValues[key] = value
        content = self.jinja2.render_template(template, **templateValues)
        self.response.out.write(content)

