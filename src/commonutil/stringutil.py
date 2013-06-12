
from md5 import md5
import logging
import re

def calculateHash(values):
    lines = []
    for value in values:
        if not value:
            continue
        if type(value) == unicode:
            lines.append(value.encode('utf-8','ignore'))
        else:
            lines.append(value)
    return md5(''.join(lines)).hexdigest()

def getMaxOrder():
    return chr(126) # ~

def contains(content, keyword):
    pattern = re.escape(keyword)
    return bool(re.search(pattern, content, re.IGNORECASE|re.DOTALL))

def getFirstSentence(sentenceSeparators, content):
    if not sentenceSeparators:
        return ''
    for separator in sentenceSeparators:
        sentences = re.split(separator, content, 1)
        if sentences:
            return sentences[0] + sentenceSeparators[0]
    return ''

def parseUnicode(rawValue, encodings=[]):
    defaultEncodings = ['utf8', 'gb2312', 'gbk']
    for encoding in encodings + defaultEncodings:
        try:
            return rawValue.decode(encoding)
        except UnicodeDecodeError:
            pass
    return None

def transformSeparators(key):
    return key.replace('-', '.')

