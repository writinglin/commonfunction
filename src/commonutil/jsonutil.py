import json
import logging

def getReadableString(jsonvalue):
    try:
        # json.dumps only supports basical data type,
        # it doesn't support datetime.datetime
        result = json.dumps(jsonvalue, ensure_ascii=False, indent=4, sort_keys=True)
    except TypeError:
        logging.exception('TypeError: %s.' % (jsonvalue, ))
        result = None
    return result

