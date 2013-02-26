import lxml.html
import lxml.html.clean
import pyquery

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

def getCleanText(element):
    cleaner = lxml.html.clean.Cleaner()
    celement = cleaner.clean_html(element)
    content = celement.text_content()
    if content:
        return content.strip()
    content = _getScriptConstantString(element)
    if content:
        return content.strip()
    return content

