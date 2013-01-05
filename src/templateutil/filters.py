from commonutil import dateutil

def utc14duration(utc14):
    if not utc14:
        return ''
    value = dateutil.parseUtc14(utc14)
    return dateutil.date2duration(value)

