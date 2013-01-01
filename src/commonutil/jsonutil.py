import json

import jsonpickle

def getReadableString(jsonvalue):
    try:
        # json.dumps only supports basical data type,
        # it doesn't support datetime.datetime
        result = json.dumps(jsonvalue, ensure_ascii=False, indent=4, sort_keys=True)
    except TypeError:
        # use jsonpickle to dumps datetime, and use json.dumps to get control format
        jsonvalue = json.loads(jsonpickle.encode(jsonvalue))
        result = json.dumps(jsonvalue, ensure_ascii=False, indent=4, sort_keys=True)
    return result

