import logging
import re
import urllib2

from commonutil import stringutil
from .import config

def _getRawParameter(querystr, parametername):
    begin = querystr.find(parametername + '=')
    keyword = ''
    if begin >= 0:
        begin = begin + len(parametername) + 1
        end = querystr.find('&', begin)
        if end > 0:
            keyword = querystr[begin:end]
        else:
            keyword = querystr[begin:]
    return keyword

def _getUnquotedParameter(querystr, parametername):
    try:
        keyword = _getRawParameter(querystr, parametername)
        return urllib2.unquote(keyword)
    except Exception:
        logging.exception('Error happened on _getUnquotedParameter: %s.' % (type(querystr),))
        return None

def getRefererKeyword(referer):
    if not referer:
        return None
    matched = None
    for robot in config.getRobots():
        if re.search(robot.get('referer'), referer, re.IGNORECASE|re.DOTALL):
            matched = robot
            break
    if not matched:
        return None
    parameter = matched.get('parameter', 'q')
    encoding = matched.get('encoding', 'utf8')
    keyword = _getUnquotedParameter(referer, parameter)
    if keyword:
        keyword = stringutil.parseUnicode(keyword, encodings=[encoding])
    return keyword

