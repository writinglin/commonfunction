import lxml.html

def getTextContent(strValue):
    return lxml.html.fromstring(strValue).text_content()
