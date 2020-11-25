import base64

class AttrDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__

def stringToBase64(s):
    return base64.b64encode(s.encode('utf-8'))

def base64ToString(b):
    return base64.b64decode(b).decode('utf-8')

