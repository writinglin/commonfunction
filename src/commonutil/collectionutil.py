"""
Judge wether all criterions are matched.
"""
def fullContains(parent, item):
    matched = True
    for tag in item:
        if tag not in parent:
            matched = False
            break
    return matched

