import networkx as nx
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder


from .utils import AttrDict, list_of_dict_to_dict_of_list, group_list
from .settings import CACHE


class GraphHelper(object):
    @classmethod
    def DEPRECATED_dict_to_graph(cls, raw_dict:dict) -> nx.Graph:
        """
            raw_dict: a dict with the columns values (list)
            :return: a nx.Graph with all information stock either in the nodes or the edges
        """
        from .layouts import apply_on_graph 
        from .visualizer import Setter
        from .settings import reset_plot_dict

        reset_plot_dict()

        df = pd.DataFrame(raw_dict)
        CACHE.df = df

        max_timestep = df['timestep'].max()
        if "timestep_slider" in CACHE.widgets:
            CACHE.widgets.timestep_slider.end = max_timestep
            CACHE.widgets.timestep_slider.value = max_timestep
        CACHE.graph_attr.timesteps = max_timestep
        CACHE.plot.timestep = max_timestep
        if "widgets" in CACHE:
            CACHE.widgets.timestep_slider.end = CACHE.graph_attr.timesteps
            CACHE.widgets.timestep_slider.value = CACHE.graph_attr.timesteps
 
        G = nx.from_pandas_edgelist(df, "person1", "person2", ("timestep", "infected1", "infected2", "loc_lat", "loc_long"), nx.OrderedMultiDiGraph())
 
        h1 = df[["person1", "home1_lat", "home1_long"]].rename({"person1":"person", "home1_lat":"home_lat", "home1_long":"home_long"}, axis='columns').set_index("person")
        h2 = df[["person2", "home2_lat", "home2_long"]].rename({"person2":"person", "home2_lat":"home_lat", "home2_long":"home_long"}, axis='columns').set_index("person")
 
        nodes_attr = pd.concat([h1, h2])
        nodes_attr = nodes_attr[~nodes_attr.index.duplicated()]
        #nodes_attr.sort_index(inplace=True)
        nodes_attr["name"] = G.nodes
        nodes_attr_dict = nodes_attr.to_dict(orient="index")
        nx.set_node_attributes(G, nodes_attr_dict)

        G = nx.relabel_nodes(G, dict(zip(G.nodes, np.arange(len(G.nodes)))), copy=False)
        degree = NodesHelper.get_degree(G, timestep=CACHE.plot.timestep)

        #nodes_attr["person"] = nodes_attr.index
        CACHE.graph = G
        CACHE.plot.source.data.update({
            **nodes_attr.to_dict(orient="list"),
            "degree": degree
        })
        
        #xs, ys, data = list(zip(*G.edges(data=True)))
        #timestep = list(zip(*G.edges.data("timestep")))[2]
        #EdgesHelper.count_attribute(G, "timestep", 10000)
        
        # reset all previous computed layouts

        Setter.all()
        
        return G

    @classmethod
    def from_dict_to_graph(cls, raw_dict):
        """
            raw_dict: a dict with the columns values (list)
            :return: a nx.Graph with all information stock either in the nodes or the edges
        """
        from .layouts import apply_on_graph
        from .visualizer import Setter
        from .settings import reset_plot_dict

        reset_plot_dict()

        df = pd.DataFrame(raw_dict)
        CACHE.df = df

        max_timestep = df['timestep'].max()
        if "widgets" in CACHE:
            CACHE.widgets.timestep_slider.end = max_timestep
            CACHE.widgets.timestep_slider.value = max_timestep
        CACHE.graph_attr.timesteps = max_timestep
        CACHE.plot.timestep = max_timestep

        all_nodes = np.r_[df.person1.values, df.person2.values].astype(np.str_)
        le = LabelEncoder()
        le.fit(all_nodes)

        for p in ("person1", "person2"):
            df[p] = le.transform(df[p].values.astype(str))

        G = nx.from_pandas_edgelist(df, source="person1", target="person2", edge_attr=("timestep", "infected1", "infected2", "loc_lat", "loc_long"), create_using=nx.OrderedMultiGraph)

        for n in (1, 2):
            nodes = df["person%d"%n].values
            home_lat = df["home%d_lat"%n].values
            home_long = df["home%d_long"%n].values
            people = le.inverse_transform(nodes)
            for n, p, lo, la in zip(nodes, people, home_long, home_lat):
                G.nodes[n]["name"] = str(p)
                G.nodes[n]["home_long"] = lo
                G.nodes[n]["home_lat"] = la

        CACHE.graph = G
        CACHE.plot.source.data.update({
            "home_lat":list(dict(G.nodes.data("home_lat")).values()),
            "home_long":list(dict(G.nodes.data("home_long")).values()),
            "name":list(dict(G.nodes.data("name")).values()),
            "degree": list(dict(G.degree).values())
        })

        Setter.all()

        return G
    @classmethod
    def subgraph_from_timestep(cls, G, timestep):
        nodes_to_keep = NodesHelper.get_unique_nodes(G, timestep)
        return G.subgraph(nodes_to_keep)

class EdgesHelper:
    @classmethod
    def get_unique_edges(cls, G, timestep=None):
        if timestep is not None:
            return cls.count_attribute(G, "timestep", timestep)[:2]
        else:
            edges = list(G.edges())
            u_edges = np.unique(edges, axis=0).T

        return u_edges

    @classmethod
    def get_attribute_list(cls, G, attr):
        [u, v, data] = np.array(list(G.edges.data(attr))).T
        return data

    @classmethod
    def get_all_attributes(cls, G, sort=True):
        [u, v, data] = np.array(list(zip(*G.edges(data=True))))

        edges, idx, inv = np.unique(np.c_[u, v].astype(int), axis=0, return_inverse=True, return_index=True)

        if sort:
            _, indexes = cls.sort(edges.T, return_indexes=True)
            inv = indexes[inv]

        dict_of_list = list_of_dict_to_dict_of_list(data, idx=inv)

        return dict_of_list

    @classmethod
    def count_attribute(cls, G, attr, leq=None, sort=False):
        edges_data = np.array(list(G.edges.data(attr))).T

        if leq is not None:
            cdt = edges_data[-1] <= leq
            adj_edges = edges_data[0:2, cdt].T
        else:
            adj_edges = edges_data[0:2].T

        edges, counts = np.unique(adj_edges, axis=0, return_counts=True)

        if sort:
            [u, v], indexes = cls.sort(edges.T, return_indexes=True)
            counts = counts[indexes]
        else:
            [u, v] = edges.T

        gather_count = np.c_[u, v, counts].T

        return gather_count # u, v, counts

    @classmethod
    def count_edges(cls, G, timestep=None):
        timestep = timestep or np.int64.max()
        raise Exception("Not implemented")

    @classmethod
    def length(cls, G):
        [u, v, c] = np.array(G.edges).T
        #edges = np.c_[u,v]
        #edges = np.sort(edges, axis=-1)
        #edges = np.unique(edges, axis=0)
        #return edges.shape[0]
        return np.sum(c==0)

    @classmethod
    def DEPRECATED_length(cls, G, timestep=None):
        edges = cls.get_unique_edges(G, timestep)
        return edges.shape[-1]

    @classmethod
    def sort(cls, edges, return_indexes=False):
        [u, v] = edges
        indexes = np.lexsort((v, u))
        sorted_edges = edges[:,indexes]
        if return_indexes:
            return sorted_edges, indexes
        return sorted_edges



class NodesHelper:

    @classmethod
    def get_unique_nodes(cls, G, timestep, with_degree=False):
        [u, v] = EdgesHelper.get_unique_edges(G, timestep)
        unique_nodes, degrees = np.unique(np.r_[u, v], return_counts=True)
        if with_degree:
            return unique_nodes, degrees
        return unique_nodes

    @classmethod
    def get_degree(cls, G, *args, **kwargs):
        nodes, degrees = np.array(list(zip(*G.degree)))
        return degrees

    @classmethod
    def DEPRECATED_get_degree(cls, G, timestep, directed=True):
        _, degrees = cls.get_unique_nodes(G, timestep, with_degree=True)
        return degrees

    @classmethod
    def get_all_attributes(cls, G):
        nodes_data = G.nodes(data=True)
        nodes, data = list(zip(*nodes_data))

        dict_of_list = list_of_dict_to_dict_of_list(data)
        degrees = cls.get_degree(G, int(2e32-1))
        dict_of_list["degree"] = degrees

        return dict_of_list

    @classmethod
    def length(cls, G, timestep):
        return len(GraphHelper.subgraph_from_timestep(G, timestep).nodes)



