import networkx as nx
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder


from .utils import AttrDict, list_of_dict_to_dict_of_list, dummy_timelog, from_long_lat_to_mercator
from .settings import CACHE


class GraphHelper(object):

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
        min_timestep = df['timestep'].min()+1
        if "timestep_slider" in CACHE.widgets:
            CACHE.widgets.timestep_slider.start = min_timestep
            CACHE.widgets.timestep_slider.end = max_timestep
            CACHE.widgets.timestep_slider.value = max_timestep
        CACHE.graph_attr.min_timestep = min_timestep
        CACHE.graph_attr.timesteps = max_timestep
        CACHE.plot.timestep = max_timestep

        all_nodes = np.r_[df.person1.values, df.person2.values].astype(np.str_)
        le = LabelEncoder()
        le.fit(all_nodes)

        for p in ("person1", "person2"):
            df[p] = le.transform(df[p].values.astype(str))

        # df["loc_long"], df["loc_lat"] = df["loc_lat"], df["loc_long"]
        df["loc_x"], df["loc_y"] = from_long_lat_to_mercator(df["loc_long"].values, df["loc_lat"].values)
        df["infected1"], df["infected2"] = df["infected1"].values.astype(bool), df["infected2"].values.astype(bool)

        with dummy_timelog("from pandas edges list"):
            G = nx.from_pandas_edgelist(df, source="person1", target="person2", edge_attr=("timestep", "infected1", "infected2", "loc_lat", "loc_long", "loc_x", "loc_y"), create_using=nx.OrderedMultiGraph)

        with dummy_timelog("set each person value per nodes"):
            for n in (1, 2):
                nodes = df["person%d"%n].values
                home_lat = df["home%d_lat"%n].values
                home_long = df["home%d_long"%n].values
                people = le.inverse_transform(nodes)
                home_x, home_y = from_long_lat_to_mercator(home_long, home_lat)
                for n, p, lo, la, x, y in zip(nodes, people, home_long, home_lat, home_x, home_y):
                    G.nodes[n]["name"] = str(p)
                    G.nodes[n]["home_long"] = lo
                    G.nodes[n]["home_lat"] = la
                    G.nodes[n]["home_x"] = float(x)
                    G.nodes[n]["home_y"] = float(y)

        with dummy_timelog("update cache in graph"):
            CACHE.graph = G
            CACHE.plot.nodes.source.data.update({
                "home_x":list(dict(G.nodes.data("home_x")).values()),
                "home_y":list(dict(G.nodes.data("home_y")).values()),
                "home_lat":list(dict(G.nodes.data("home_lat")).values()),
                "home_long":list(dict(G.nodes.data("home_long")).values()),
                "name":list(dict(G.nodes.data("name")).values()),
                "degree": list(dict(G.degree).values())
            })

        with dummy_timelog("setter all"):
            Setter.all()
        
        return G


    @classmethod
    def subgraph_from_timestep(cls, G, timestep):
        g = G.copy()
        nodes_count = dict(G.degree())
        for u, v, key, data in G.edges(data=True, keys=True):
            if data['timestep'] > timestep:
                nodes_count[u] -= 1
                nodes_count[v] -= 1
                g.remove_edge(u, v, key=key)
        nodes, counts = list(zip(*nodes_count.items()))
        nodes = np.array(nodes); counts = np.array(counts)
        nodes_to_keep = nodes[counts>0]
        return g.subgraph(nodes_to_keep)

    @classmethod
    def multigraph_to_weighted_graph(cls, M):
        G = nx.Graph()
        for u,v,data in M.edges(data=True):
            w = data['weight'] if 'weight' in data else 1.0
            if G.has_edge(u, v):
                G[u][v]['weight'] += w
            else:
                G.add_edge(u, v, weight=w)
        return G



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
        [u, v, data] = list(zip(*G.edges(data=True)))

        edges, idx, inv = np.unique(np.c_[u, v].astype(int), axis=0, return_inverse=True, return_index=True)

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
        nodes, degrees = list(zip(*G.degree))
        return np.array(degrees)

    @classmethod
    def get_all_attributes(cls, G):
        nodes_data = G.nodes(data=True)
        nodes, data = list(zip(*nodes_data))

        dict_of_list = list_of_dict_to_dict_of_list(data)
        degrees = cls.get_degree(G)
        dict_of_list["degree"] = degrees

        return dict_of_list

    @classmethod
    def length(cls, G, timestep=None):
        if timestep is None:
            return len(G.nodes)
        return len(GraphHelper.subgraph_from_timestep(G, timestep).nodes)

    @classmethod
    def get_ordered(cls, G, nodes_attr_dict=None, nodes=None, attr=None):
        assert not ((nodes_attr_dict is not None) ^ (nodes is not None and attr is not None)), "Need either nodes and attr or a dict with nodes::attr"
        if nodes_attr_dict is not None:
            nodes = np.array(list(nodes_attr_dict.keys()))
            attr = np.array(list(nodes_attr_dict.values()))

        off_nodes = np.array(list(G.nodes))

    @classmethod
    def _get_attribute(cls, G, attr):
        attrlist = list(dict(G.nodes.data(attr)).values())
        return np.array(attrlist)

    @classmethod
    def get_attributes(cls, G, attrs):
        if isinstance(attrs, str):
            attrs = [attrs]
        answer = tuple()
        for attr in attrs:
            answer += (cls._get_attribute(G, attr),)
        return answer if len(answer) > 1 else answer[0]

    #@classmethod
    #def get_mid_long_lat(cls, G):
    #    home_long = cls.get_attribute(G, "home_long")
    #    home_lat = cls.get_attribute(G, "home_lat")
    #    return np.mean(home_long),
        



