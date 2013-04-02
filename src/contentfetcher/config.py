from configmanager import cmapi

_FETCH_TIMEOUT = 10
_USER_AGENT = 'Googlebot/2.1 (+http://www.googlebot.com/bot.html)'
_USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:19.0) Gecko/20100101 Firefox/19.0'

def getFetchTimeout():
    return cmapi.getItemValue('~.fetchtimeout', _FETCH_TIMEOUT)

def getUserAgent():
    return cmapi.getItemValue('~.useragent', _USER_AGENT)

