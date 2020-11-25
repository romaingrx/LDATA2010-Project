from abc import ABC, abstractclassmethod
import pandas as pd
import networkx as nx


class LayoutAlgorithm(ABC):
    @abstractclassmethod
    def __call__(cls, *args, **kwargs):
        return cls.get_nodes(*args, **kwargs)

    @abstractclassmethod
    def get_nodes(cls, df:pd.DataFrame):
        raise NotImplementedError() 

class Basic(LayoutAlgorithm):
    @classmethod
    def get_nodes(cls, df:pd.DataFrame):
        return df[("loc_long", "loc_lat")].values

class ForceLayout(LayoutAlgorithm):
    @classmethod
    def get_nodes(cls, df:pd.DataFrame):
        # TODO
        raise NotImplementedError()

AVAILABLE = dict(
    circular=nx.circular_layout,
    spectral=nx.drawing.layout.spectral_layout,
    fruchterman_reingold=nx.layout.fruchterman_reingold_layout
)

def get(key:str):
    return AVAILABLE.get(key, None)