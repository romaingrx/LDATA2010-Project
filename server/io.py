import os
import pandas as pd
from io import StringIO
import tempfile

from . import settings
from .settings import COLUMNS_NAME
from .templates import void_graph
from .utils import base64ToString

from collections import defaultdict


class FileInputHandler(object):
    @classmethod 
    def callback(cls, attr, old, new) -> dict:
        settings.GRAPH = cls.from_raw_to_dict(new)
        settings.SOURCE.data = settings.GRAPH

    @classmethod
    def from_raw_to_dict(cls, raw_data)->dict:
        data = base64ToString(raw_data).replace(' ','')

        df = pd.read_csv(StringIO(data))
        assert len(df.columns) == len(COLUMNS_NAME), f"Not the same number of columns in this csv file; expected {COLUMNS_NAME} but got {df.columns}" 

        df.columns = COLUMNS_NAME
        
        graph = df.to_dict(orient='list')

        return graph
