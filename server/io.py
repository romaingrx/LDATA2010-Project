import csv
import numpy as np

from .settings import COLUMNS_NAME
from .templates import void_graph
from .utils import base64ToString

from collections import defaultdict

def from_text_to_dict(raw_data):
    graph = void_graph
    data = base64ToString(raw_data)

    [header, *rows] = data.replace(' ','').split('\n')
    assert len(header.split(',')) == len(COLUMNS_NAME), f"Not the same number of columns in this csv file; expected {COLUMNS_NAME} but got {header.split(',')}" 

    


