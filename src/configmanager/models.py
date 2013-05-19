from google.appengine.ext import db

class ConfigItem(db.Model):
    """Models a Config Item entry."""
    value = db.TextProperty()

class RunStatus(db.Model):
    """Models a Run Status entry."""
    value = db.TextProperty()

