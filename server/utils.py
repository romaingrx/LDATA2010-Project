import base64
import numpy as np
import pandas as pd
import seaborn as sns
from time import time_ns, sleep
from collections import defaultdict
from contextlib import contextmanager

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
    df = pd.DataFrame(lst)
    if idx is not None:
        keys = df.columns.values
        df["idx"] = idx
        df = df.groupby("idx")[keys].agg(list)
    return df.to_dict(orient="list")




def DEPRECATED_list_of_dict_to_dict_of_list(lst, idx=None):
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
    data_collector = [list(d.values()) for d in lst]
    T_collector = [] * len(keys)
    for node in data_collector:
        for idx, v in enumerate(node):
            T_collector[idx].append(v)

    dol = {k:d for k,d in zip(keys, T_collector)}
    return dol

def group_list(lst, idx):
    pass

def cur_graph():
    from .settings import CACHE
    return CACHE.ultra[CACHE.plot.timestep].G

class SnsPalette:
    def __init__(self, color):
        self._color = color
    def __call__(self, n):
        return np.array(sns.color_palette(self._color, n_colors=n).as_hex())

def from_dict_to_menu(d):
    if isinstance(d, dict):
        l = []
        for k,v in d.items():
            if v is None:
                l.append(None)
            else:
                l.append(k)
    else:
        return d
    return l

def ordered(official, toorder, attr=None):
    sidx = np.argsort(toorder)
    s_toorder = toorder[sidx]
    s_attr = attr[sidx]
    index_in_off = np.searchsorted(s_toorder, official)
    return s_attr[index_in_off]

def assign_color_from_class(class_values, palette):
    assert callable(palette)
    uclasses = np.unique(class_values)
    colors = palette(len(uclasses))
    #new_colors = ordered(class_values, uclasses, colors)
    sidx = uclasses.argsort()
    s_uclasses= uclasses[sidx]
    s_colors = colors[sidx]
    new_colors = s_colors[np.searchsorted(s_uclasses, class_values)]
    return new_colors

@contextmanager
def dummy_timelog(desc):
    from .settings import TIMELOGGER
    tic = time_ns()
    yield
    tac = time_ns()
    time_taken = tac -tic
    unities = ["ns", "μs", "ms", "s"]
    for unity in unities:
        if time_taken / 1e3 < 1.:
            break
        time_taken /= 1e3
    TIMELOGGER.info(f"{desc} :: {time_taken:.2f} {unity}")

