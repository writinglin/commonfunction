from configmanager import cmapi

DEFAULT_ROBOTS = [
    {
        "encoding": "utf8", 
        "parameter": "q", 
        "referer": "google", 
        "slug": "google"
    },
    {
        "encoding": "utf8", 
        "parameter": "q", 
        "referer": "youdao", 
        "slug": "youdao"
    },
    {
        "encoding": "utf8", 
        "parameter": "wd", 
        "referer": "baidu", 
        "slug": "baidu"
    },
    {
        "encoding": "GBK", 
        "parameter": "w", 
        "referer": "soso", 
        "slug": "soso"
    },
    {
        "encoding": "utf8", 
        "parameter": "query", 
        "referer": "sogou", 
        "slug": "sogou"
    }
]

def getRobots():
    return cmapi.getItemValue('robots', DEFAULT_ROBOTS)

