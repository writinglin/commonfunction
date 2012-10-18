from google.appengine.ext import db

class ConfigItem(db.Model):
    """Models a Config Item entry."""
    value = db.TextProperty()

