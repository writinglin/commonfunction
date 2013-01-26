
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

