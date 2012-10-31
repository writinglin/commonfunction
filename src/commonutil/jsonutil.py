import json

def getReadableString(jsonobj):
    return json.dumps(jsonobj, ensure_ascii=False, indent=4, sort_keys=True)

