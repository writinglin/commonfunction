import datetime

from pytz.gae import pytz

from configmanager import cmapi

def increaseIncomingBandwidth(bytes):
    inbandwidth = cmapi.getItemValue('inbandwidth', {})

    allband = inbandwidth.get('all')
    if not allband:
        allband = {}
        inbandwidth['all'] = allband
    allband['bytes'] = allband.get('bytes', 0) + bytes
    allband['fetch'] = allband.get('fetch', 0) + 1

    timezonename = inbandwidth.get('tz')
    if not timezonename:
        timezonename = 'US/Pacific'
        inbandwidth['tz'] = timezonename

    date_format = '%Y%m%d'
    date = datetime.datetime.now(tz=pytz.utc)
    date = date.astimezone(pytz.timezone(timezonename))
    key = date.strftime(date_format)

    current = inbandwidth.get('current')
    if not current or current.get('key') != key:
        historycount = inbandwidth.get('historycount')
        if not historycount:
            historycount = 7
            inbandwidth['historycount'] = historycount
        if current:
            history = inbandwidth.get('history')
            if not history:
                history = []
            history.insert(0, current)
            history = history[:historycount]
            inbandwidth['history'] = history
        current = {'key': key, 'bytes': bytes, 'fetch': 1}
        inbandwidth['current'] = current
    else:
        current['fetch'] += 1
        current['bytes'] += bytes

    cmapi.saveItem('inbandwidth', inbandwidth)

