import lxml.html

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

