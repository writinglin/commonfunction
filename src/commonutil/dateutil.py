import datetime

def parseUtc14(utc14):
    return datetime.datetime.strptime(utc14, '%Y%m%d%H%M%S')

def _getUnitMessage(config, value, unit):
    if config.get('plural'):
        if value > 1:
            pluralvalue = 's'
        else:
            pluralvalue = ''
        return config.get(unit) % (value, pluralvalue)
    return config.get(unit) % (value,)

def date2duration(value, messageconfig=None):
    if not messageconfig:
        messageconfig = {
            'plural': True,
            'year': '%s year%s ago',
            'month': '%s month%s ago',
            'week': '%s week%s ago',
            'day': '%s day%s ago',
            'hour': '%s hour%s ago',
            'minute': '%s minute%s ago',
        }
    now = datetime.datetime.utcnow()
    duration = now - value
    if duration.days >= 365:
        return _getUnitMessage(messageconfig, duration.days // 365, 'year')
    if duration.days >= 30:
        return _getUnitMessage(messageconfig, duration.days // 30, 'month')
    if duration.days >= 7:
        return _getUnitMessage(messageconfig, duration.days // 7, 'week')
    if duration.days >= 1:
        return _getUnitMessage(messageconfig, duration.days, 'day')
    minutes = duration.seconds // 60
    hours = minutes // 60
    minutes = minutes % 60
    if hours >= 1:
        return _getUnitMessage(messageconfig, hours, 'hour')
    return _getUnitMessage(messageconfig, minutes, 'minute')

