import re
import lxml
import lxml.html.clean
import pyquery

utf8parser = lxml.etree.XMLParser(encoding='utf-8')

"""
lxml.etree can not work with unicode
Using specified parser can ignore the declared encoding in string.
"""
def parseFromUnicode(unicodeStr):
    s = unicodeStr.encode('utf-8')
    return lxml.etree.fromstring(s, parser=utf8parser)

"""
json.dumps(lxml.etree._ElementUnicodeResult) works fine.
lxml.etree._ElementUnicodeResult.strip() return basestring
"""
def getPureString(value):
    if not value:
        return ''
    if not isinstance(value, lxml.etree._ElementUnicodeResult):
        return value.strip()
    return (value + ' ').strip()

def getFullPrevious(element):
    previous = None
    while previous is None and element is not None:
        previous = element.getprevious()
        if previous is None:
            element = element.getparent()
    return previous

def getFullNext(element):
    next = None
    while next is None and element is not None:
        next = element.getnext()
        if next is None:
            element = element.getparent()
    return next

"""
text node can be attached as tail of comment or script node,
this kind of text node is visible to user.
"""
def isVisibleElement(element):
    if isinstance(element, lxml.html.HtmlComment):
        return False
    tags = ['script', 'style', 'meta', 'link']
    if isinstance(element, lxml.html.HtmlElement) and element.tag in tags:
        return False
    return True

def getBlockParent(element):
    parent = element
    blocktags = ['div', 'p', 'td']
    while parent is not None:
        if parent.tag in blocktags:
            return parent
        parent = parent.getparent()
    return None
"""
a"b"c"d"e
0:a, 1:b, 2:c, 3:d, 4:e
1, 3 is in quote
"""
def _getConstantString(text, c):
    parts = text.split(c)
    i = 1
    maxstr = None
    size = len(parts)
    if size % 2 == 0:# prevent unclose quote
        size -= 1
    if size < 3:
        return None
    while i < size:
        if not maxstr:
            maxstr = parts[i]
        elif len(parts[i]) > len(maxstr):
            maxstr = parts[i]
        i += 2
    if maxstr:
        maxstr = maxstr.strip()
    return maxstr

"""
Some page use script to protect content.
For example:
<script>
document.write(view("content content"))
</script>
"""
def _getScriptConstantString(element):
    match = pyquery.PyQuery(element)('script')
    if not match:
        return None
    script = match[0]
    content = script.text_content()
    if not content:
        return None
    maxstr = _getConstantString(content, '"')
    if not maxstr:
        maxstr = _getConstantString(content, '\'')
    return maxstr

"""
lxml.html.clean.Cleaner has a bug.
See "773715 lxml".
"""
def _getVisibleText(element):
    result = ''
    if not isVisibleElement(element):
        return result
    if element.text:
        result += element.text
    for childElement in element.getchildren():
        result += _getVisibleText(childElement)
        if childElement.tail:
            result += childElement.tail
    return result

def getCleanText(element):
    content = _getVisibleText(element)
    if content:
        return getPureString(content)
    content = _getScriptConstantString(element)
    if content:
        return content.strip()
    return content

def removeEncodingDeclaration(content):
    return re.sub(r'<?xml[^>]+?>', '', content, 1)

