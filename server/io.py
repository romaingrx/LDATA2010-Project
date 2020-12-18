import os
import json
import pandas as pd
import networkx as nx
from io import StringIO
from typing import Any, Tuple
from functools import wraps
from threading import Thread
import tempfile

from . import settings, layouts
from .settings import COLUMNS_NAME, CACHE, LOGGER
from .graphs import GraphHelper
from .utils import base64ToString, dic_from_string, deep_merge

from collections import defaultdict




class JSONHandler(object):
    @classmethod
    def ensure_created(cls):
        if not os.path.exists(settings.LAST_CONFIG_FILE):
            cls.clear()
            return False
        return True

    @classmethod
    def clear(cls) -> None:
        with open(settings.LAST_CONFIG_FILE, 'w+') as fd_json:
            json.dump({}, fd_json)
    
    @classmethod
    def get_current_config(cls) -> dict:
        cls.ensure_created()
        with open(settings.LAST_CONFIG_FILE, 'r') as fp:
            data = json.load(fp)
        return data
    
    @classmethod
    def get(cls, keys:Tuple) -> Any:
        if not isinstance(keys, tuple) and not isinstance(keys, list):
            keys = [keys] 
        current_config = cls.get_current_config()

        swim_value = current_config
        for key in keys:
            if not isinstance(swim_value, dict) or swim_value is None:
                break
            swim_value = swim_value.get(key, None)
        return swim_value
            

    @classmethod
    def update_last_config(cls, new_settings:dict) -> None:
        LOGGER.info(f"Update json config with {new_settings}")
        current_settings = cls.get_current_config()
        with open(settings.LAST_CONFIG_FILE, 'w+') as fd_json:
            updated_settings = deep_merge(current_settings, new_settings)
            json.dump(updated_settings, fd_json)
    
    @classmethod
    def _update(cls, path, item, sep):
        json_dir = dic_from_string(path, item, sep)
        cls.update_last_config(json_dir)
        return 
    
    @classmethod
    def update(cls, path, sep='.'):
        def stocker(f):
            @wraps(f)
            def wrapper(c, *args):
                if len(args) == 1:
                    item = args[-1].item
                elif len(args) == 3:
                    item = args[-1]
                else:
                    pass
                Thread(target=cls._update, args=(path, item, sep)).start()
                return f(c, *args)
            return wrapper
        return stocker
        
class FileInputHandler(object):
    @classmethod 
    @JSONHandler.update(path="source.raw_data")
    def callback(cls, attr, old, new) -> dict:
        CACHE.graph = cls.from_raw_to_graph(new, based64=True)
    
    @classmethod
    def from_raw64_to_dict(cls, raw_data)->dict:
        data = base64ToString(raw_data).replace(' ','')

        df = pd.read_csv(StringIO(data), 
        dtype={
            'person1': str,
            'person2': str,
            })
        assert len(df.columns) == len(COLUMNS_NAME), f"Not the same number of columns in this csv file; expected {COLUMNS_NAME} but got {df.columns}" 

        df.columns = COLUMNS_NAME
        graph = df.to_dict(orient='list')

        return graph
    
    @classmethod
    def from_raw_to_graph(cls, graph_dict, based64=True) -> nx.Graph:
        if based64:
            graph_dict = cls.from_raw64_to_dict(graph_dict)
        graph = GraphHelper.from_dict_to_graph(graph_dict)
        return graph