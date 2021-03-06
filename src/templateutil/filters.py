import json

from commonutil import dateutil

def utc14duration(utc14, durationconfig=None):
    if not utc14:
        return ''
    value = dateutil.parseDate14(utc14)
    return dateutil.date2duration(value, durationconfig)

def d14format(date14):
    if not date14:
        return ''
    value = dateutil.parseDate14(date14)
    if value.hour == 0 and value.minute == 0:
        format = '%Y-%m-%d'
    else:
        format = '%Y-%m-%d %H:%M:%S'
    return value.strftime(format)

def tojson(value):
    return json.dumps(value)

