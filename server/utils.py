import base64
import numpy as np
from collections import defaultdict

class AttrDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__

def stringToBase64(s):
    return base64.b64encode(s.encode('utf-8'))

def base64ToString(b):
    return base64.b64decode(b).decode('utf-8')

def dic_from_string(path_string, item, sep):
    def recursive_boy(elems, item):
        if len(elems) == 1:
            return {elems[0]:item}
        else:
            return {elems[0]:recursive_boy(elems[1:], item)}
    
    elems = path_string.split(sep)
    dic = recursive_boy(elems, item)
    return dic

def list_of_dict_to_dict_of_list(lst, idx=None):
    if len(lst) < 1:
        return {}

    if idx is not None:
        assert len(lst) == len(idx)
        d = defaultdict(lambda:defaultdict(list))
        sorted_idx = np.argsort(idx)
        values = np.array(lst)[sorted_idx]
        idx = idx[sorted_idx]
        for i, e in zip(idx, values):
            for k,v in e.items():
                d[i][k].append(v)
        for k,v in d.items():
            d[k] = dict(v)
        d = dict(d)
        lst = list(d.values())

    keys = list(lst[0].keys())
    data_collector = np.array([list(d.values()) for d in lst]).T
    dol = {k:d for k,d in zip(keys, data_collector)}
    return dol

def group_list(lst, idx):
    pass

def cur_graph():
    from .settings import CACHE
    return CACHE.ultra[CACHE.plot.timestep].G

if __name__ == "__main__":
    d = dic_from_string("A", 42, '.')
    print(d)