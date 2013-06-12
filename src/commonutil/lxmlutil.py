import logging
import re

import lxml
import lxml.html.clean
import pyquery

INLINE_TAGS = [
'a', 'abbr', 'acronym', 'b', 'basefont',
'bdo', 'big', 'br', 'cite', 'code', 'dfn',
'em', 'font', 'i', 'img', 'input', 'kbd',
'label', 'q', 's', 'samp', 'select', 'small',
'span', 'strike', 'strong', 'sub', 'sup',
'textarea', 'tt', 'u', 'var'
]

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

def _hasHiddenStyle(element):
    style = element.get('style')
    if style and re.search(r'display:\s*none', style, flags=re.IGNORECASE):
        return True
    return False

"""
text node can be attached as tail of comment or script node,
this kind of text node is visible to user.
"""
def isVisibleElement(element):
    if isinstance(element, lxml.etree._Comment):
        return False
    tags = ['script', 'style', 'meta', 'link']
    if isinstance(element,  lxml.etree._Element) and element.tag in tags:
        return False
    if _hasHiddenStyle(element):
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
    maxstr = ''
    size = len(parts)
    if size % 2 == 0:# prevent unclose quote
        size -= 1
    if size < 3:
        return ''
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
def getScriptConstantString(element):
    match = pyquery.PyQuery(element)('script')
    if not match:
        return ''
    script = match[0]
    content = script.text_content()
    if not content:
        return ''
    maxstr = _getConstantString(content, '"')
    if not maxstr:
        maxstr = _getConstantString(content, '\'')
    if maxstr:
        return maxstr.strip()
    return maxstr

"""
lxml.html.clean.Cleaner has a bug.
See "773715 lxml".
return tail text event if the element is not visible, it
is a bit wierd, but it is the only way tail can be found.
tail is alway visible.
"""
def _getVisibleText(element, withTail=False):
    result = ''
    if isVisibleElement(element):
        if element.text:
            result += element.text
        for childElement in element.getchildren():
            result += _getVisibleText(childElement, withTail=True)
    if element.tail:
        result += element.tail
    return result

"""
getCleanText should behave like text_content()
"""
def getCleanText(element):
    content = _getVisibleText(element)
    if content:
        return getPureString(content)
    return content

def removeEncodingDeclaration(content):
    return re.sub(r'<?xml[^>]+?>', '', content, 1)

def findAllVisibleMatched(result, element, textFunc=None, tailFunc=None, funcResult=None, includeSelf=False):
    added = False
    visible = isVisibleElement(element)
    if includeSelf and visible:
        if not textFunc:
            result.append(element)
            added = True
        elif textFunc and element.text:
            testResult = textFunc(element.text)
            if testResult:
                result.append(element)
                added = True
                if funcResult is not None:
                    funcResult.append(testResult)
    if includeSelf and not added and tailFunc and element.tail:
        testResult = tailFunc(element.tail)
        if testResult:
            result.append(element)
            if funcResult is not None:
                funcResult.append(testResult)
    if not visible:
        return
    for child in element.getchildren():
        findAllVisibleMatched(result, child, textFunc, tailFunc, funcResult,
                                includeSelf=True)

