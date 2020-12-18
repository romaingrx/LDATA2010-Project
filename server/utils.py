import base64
import numpy as np
import pandas as pd
import seaborn as sns
from time import time_ns, sleep
from collections import defaultdict
from contextlib import contextmanager
from pyproj import Transformer
from bokeh.models import Div



class AttrDict(dict):
    __setattr__ = dict.__setitem__
    __getattr__ = dict.__getitem__

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

def deep_merge(x, y):
    z = x.copy()
    for key in y.keys():
        if key in x:
            if isinstance(y[key], dict):
                if isinstance(x[key], dict):
                    z[key] = deep_merge(x[key], y[key])
                else:
                    z[key] = y[key]
            else:
                z[key] = y[key]
        else:
            z[key] = y[key]
    return z


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


def create_new_timestep_dict():
    from .settings import CACHE
    from .graphs import GraphHelper
    CACHE.ultra[CACHE.plot.timestep] = AttrDict(
        G=GraphHelper.subgraph_from_timestep(CACHE.graph, CACHE.plot.timestep),
        layouts=AttrDict()
    )
    CACHE.ultra[CACHE.plot.timestep]["W"] = GraphHelper.multigraph_to_weighted_graph(CACHE.ultra[CACHE.plot.timestep]["G"])


def timestep_cache():
    from .settings import CACHE
    timestep = CACHE.plot.timestep
    if timestep not in CACHE.ultra:
        create_new_timestep_dict()
    return CACHE.ultra[timestep]

def cur_graph():
    from .settings import CACHE
    return timestep_cache().G

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

def resize(x, size=None, alpha=1., size_alpha=1.):
    """
    :param x: the space points
    :param size: if each points has a fixed size (node)
    :param alpha: how much we dilate the [min,max] range
    :param size_alpha: how much we dilate the size values
    :return: min, max
    """
    argmin = np.argmin(x)
    argmax = np.argmax(x)
    mi = x[argmin]
    ma = x[argmax]
    midist = abs(ma-mi)/2
    if size is not None:
        mi -= size_alpha * size[argmin]
        ma += size_alpha * size[argmax]
    return mi-(alpha-1.)*midist, ma+(alpha-1.)*midist

def dummy_scale(values, w, z):
    x, y = values.min(), values.max()
    dist_xy = abs(x-y)
    dist_wz = abs(w-z)
    if dist_xy == 0:
        return np.full_like(values, w+dist_wz/2)
    values_01 = (values - x)/dist_xy
    values_scaled = w + dist_wz * values_01
    return values_scaled

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


def from_long_lat_to_mercator(long, lat):
    if isinstance(long, float):
        long = [long]
        lat = [lat]
    _tsf = Transformer.from_crs("EPSG:4326", "EPSG:3857")
    x, y = _tsf.transform(long, lat)
    return x, y

def DEPRECATEDwgs84_to_mercator(long, lat):
    r = 6378137
    y = long * r * np.pi / 180.
    x = np.log(np.tan((90. + lat) * np.pi / 360.)) * r
    return x, y

def tooltips(l, color=None, fontweight="bold"):
    from .settings import COLORS
    color = color or COLORS.purple 
    
    base = """<div>%s</div>"""
    div = f"""<div><span style=\"font-weight: {fontweight}\"><font color={color}>%s</font>: %s</div></span>"""
    stack_div = ""
    for k, v in l:
        stack_div += div%(k, v)
    return base%stack_div


def h1(text):
    from .settings import STATIC
    return Div(text=f"<font color={STATIC.h1}><h1>{text}</h1></font>")

if __name__=='__main__':
    long = 50.8585209256615
    lat = 4.28512395570893


    a_dict = dict(prout=42, dylan=dict(patrick="oui", bob="dylan"))
    b_dict = dict(dylan=dict(bob="kob"))

    z = deep_merge(a_dict, b_dict)
    print(z)
