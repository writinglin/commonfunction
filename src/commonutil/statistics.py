import datetime

from pytz.gae import pytz

from configmanager import cmapi

def increaseIncomingBandwidth(bytes):
    itemKey = '~.inbandwidth'
    inbandwidth = cmapi.getItemValue(itemKey, {})

    allband = inbandwidth.get('all')
    if not allband:
        allband = {}
        # astimezone() cannot be applied to a naive datetime
        # jsonpickle does not support timezone
        # so we use utcnow to generate naive datetime
        allband['start'] = datetime.datetime.utcnow()
        inbandwidth['all'] = allband
    allband['bytes'] = allband.get('bytes', 0) + bytes
    allband['fetch'] = allband.get('fetch', 0) + 1

    timezonename = inbandwidth.get('tz')
    if not timezonename:
        timezonename = 'US/Pacific'
        inbandwidth['tz'] = timezonename

    nnow = datetime.datetime.now(tz=pytz.utc)
    tzdate = nnow.astimezone(pytz.timezone(timezonename))
    key = tzdate.strftime('%Y%m%d')

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

    cmapi.saveItem(itemKey, inbandwidth)

