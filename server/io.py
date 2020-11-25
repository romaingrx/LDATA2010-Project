import os
import json
import pandas as pd
import networkx as nx
from io import StringIO
from typing import Any, Tuple
import tempfile

from . import settings, layouts
from .settings import COLUMNS_NAME, CACHE
from .graphs import GraphHelper
from .utils import base64ToString

from collections import defaultdict


class FileInputHandler(object):
    @classmethod 
    def callback(cls, attr, old, new) -> dict:
        CACHE.plot.source.data = {}
        CACHE.graph = cls.from_raw_to_graph(new)
        JSONHandler.update_last_config(dict(
            source=dict(
                raw_data=new
            )
        ))
    
    @classmethod
    def from_raw64_to_dict(cls, raw_data)->dict:
        data = base64ToString(raw_data).replace(' ','')

        df = pd.read_csv(StringIO(data))
        assert len(df.columns) == len(COLUMNS_NAME), f"Not the same number of columns in this csv file; expected {COLUMNS_NAME} but got {df.columns}" 

        df.columns = COLUMNS_NAME
        graph = df.to_dict(orient='list')

        CACHE.df = df

        return graph
    
    @classmethod
    def from_raw_to_graph(cls, raw_data) -> nx.Graph:
        graph_dict = cls.from_raw64_to_dict(raw_data)
        graph = GraphHelper.from_dict_to_graph(graph_dict)
        layouts.apply_on_graph()
        return graph

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
        current_settings = cls.get_current_config()
        with open(settings.LAST_CONFIG_FILE, 'w+') as fd_json:
            updated_settings = {**current_settings, **new_settings}
            json.dump(updated_settings, fd_json)
