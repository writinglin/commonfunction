import datetime
import re

def parseDate14(date14):
    return datetime.datetime.strptime(date14, '%Y%m%d%H%M%S')

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

def getDateAs14(value=None):
    if not value:
        value = datetime.datetime.utcnow()
    return value.strftime('%Y%m%d%H%M%S')

def getHoursAs14(hours):
    start = datetime.datetime.utcnow() - datetime.timedelta(hours=hours)
    return getDateAs14(start)

ZERO = datetime.timedelta(0)

class UTC(datetime.tzinfo):
    """UTC"""

    def utcoffset(self, dt):
        return ZERO

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return ZERO

def _matchDateformat1(value):
    # 'Sat Feb 26 08:43:46 +0000 2011'
    match_ptn = r'^[a-zA-Z]{3} (?P<month>[a-zA-Z]{3}) (?P<date>\d{2}) (?P<hour>\d{2}):(?P<minute>\d{2}):(?P<second>\d{2}) (?P<timezone>[+-]\d{4}) (?P<year>\d{4})$'
    return re.match(match_ptn, value)

def _matchDateformat2(value):
    # "Fri, 25 Feb 2011 21:33:54 -0800"
    # "Fri, 13 Aug 2010 10:21:45 PDT"
    # "Fri, 26 Jan 2007 14:28:14 PST"
    match_ptn = r'^[a-zA-Z]{3}, (?P<date>\d{2}) (?P<month>[a-zA-Z]{3}) (?P<year>\d{4}) (?P<hour>\d{2}):(?P<minute>\d{2}):(?P<second>\d{2}) (?P<timezone>[+-]\d{4}|[a-zA-Z]{3})$'
    return re.match(match_ptn, value)

TIMEZONES = {'PST': -8,
             'PDT': -7,
             'GMT': 0,
             }

def jsDate2utc14(date_str):
    m = _matchDateformat1(date_str)
    if not m:
        m = _matchDateformat2(date_str)
    if not m:
        return None
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    date = int(m.group('date'), 10)
    month = months.index(m.group('month')) + 1
    year = int(m.group('year'), 10)
    hour = int(m.group('hour'), 10)
    minute = int(m.group('minute'), 10)
    seconds = int(m.group('second'), 10)
    tz = TIMEZONES.get(m.group('timezone'))
    if tz is not None:
        offset = tz * 60
    else:
        try:
            tz = int(m.group('timezone'), 10)
            if tz < 0:
                offset = -(-tz // 100 * 60 + (- tz % 100))
            else:
                offset = tz // 100 * 60 + tz % 100
        except:
            return None
    utc = datetime.datetime(year, month, date,
                             hour, minute, seconds, 0, UTC()) - datetime.timedelta(minutes=offset)
    return utc.strftime('%Y%m%d%H%M%S')

def getTodayStartAs14(timezone):
    now = datetime.datetime.utcnow()
    now += datetime.timedelta(hours=timezone)
    now = datetime.datetime(now.year, now.month, now.day)
    now -= datetime.timedelta(hours=timezone)
    return now.strftime('%Y%m%d%H%M%S')

