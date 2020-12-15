import cugraph
import numpy as np

from .utils import dummy_timelog, ordered, timestep_cache
from .graphs import GraphHelper
from .settings import CACHE, LOGGER, TIMELOGGER


def louvain_partition(G, as_dict=False):
    W = timestep_cache().W
    nodes_cluster, score = cugraph.louvain(W)
    nodes = np.array(list(nodes_cluster.keys()))
    off_nodes = np.array(G.nodes)
    clusters = np.array(list(nodes_cluster.values()))
    s_clusters = ordered(off_nodes, nodes, clusters) # Need to sort the cluster cause the order is not keeped from louvain algo
    if as_dict:
        return dict(zip(off_nodes, s_clusters))
    return s_clusters

def katz_centrality(G, as_dict=False):
    W = timestep_cache().W
    nodes_centrality = cugraph.katz_centrality(W)
    nodes = np.array(list(nodes_centrality.keys()))
    off_nodes = np.array(G.nodes)
    clusters = np.array(list(nodes_centrality.values()))
    s_clusters = ordered(off_nodes, nodes, clusters) # Need to sort the cluster cause the order is not keeped from louvain algo
    if as_dict:
        return dict(zip(off_nodes, s_clusters))
    return s_clusters

AVAILABLE = {
    "louvain":louvain_partition,
    "katz_centrality":katz_centrality
}

def get(key:str):
    return AVAILABLE.get(key, None)
