from bokeh.plotting import ColumnDataSource
import networkx as nx
import pandas as pd
import numpy as np

from .utils import AttrDict
from .settings import CACHE


class GraphHelper(object):
    @classmethod
    def from_dict_to_graph(cls, raw_dict:dict) -> nx.Graph:
        """
            raw_dict: a dict with the columns values (list)
            :return: a nx.Graph with all information stock either in the nodes or the edges
        """
        df = pd.DataFrame(raw_dict)
        CACHE.df = df

        CACHE.graph_attr.timesteps = df['timestep'].max()
        if "widgets" in CACHE:
            CACHE.widgets.timestep_slider.end = CACHE.graph_attr.timesteps
            CACHE.widgets.timestep_slider.value = CACHE.graph_attr.timesteps
 
        G = nx.from_pandas_edgelist(df, "person1", "person2", ("timestep", "infected1", "infected2", "loc_lat", "loc_long"), nx.Graph())
 
        h1 = df[["person1", "home1_lat", "home1_long"]].rename({"person1":"person", "home1_lat":"home_lat", "home1_long":"home_long"}, axis='columns').set_index("person")
        h2 = df[["person2", "home2_lat", "home2_long"]].rename({"person2":"person", "home2_lat":"home_lat", "home2_long":"home_long"}, axis='columns').set_index("person")
 
        nodes_attr = pd.concat([h1, h2])
        nodes_attr = nodes_attr[~nodes_attr.index.duplicated()]
        nodes_attr.sort_index(inplace=True)
        nodes_attr["name"] = G.nodes
        nodes_attr_dict = nodes_attr.to_dict(orient="index")
        nx.set_node_attributes(G, nodes_attr_dict)

        G = nx.relabel_nodes(G, dict(zip(G.nodes, np.arange(len(G.nodes)))), copy=False)

        nodes_attr["person"] = nodes_attr.index
        CACHE.graph = G
        CACHE.plot.source.data.update({
            **nodes_attr.to_dict(orient="list"),
        })
 
        return G
