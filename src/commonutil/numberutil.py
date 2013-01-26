
def parseInt(value):
    while value:
        try:
            return int(value)
        except ValueError:
            value = value[:-1]
    return None

