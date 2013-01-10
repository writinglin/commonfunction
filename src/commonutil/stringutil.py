
from md5 import md5

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

