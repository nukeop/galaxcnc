import string

def filter_str(s):
    """Filters everything that isn't a letter or a number out.
    """
    return "".join([x for x in s if x in string.digits or x in
                    string.ascii_letters]) 
def chunks(msg, n):
    for i in range(0, len(msg), n):
        yield msg[i:i+n]
