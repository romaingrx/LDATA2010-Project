import cugraph
import numpy as np

from .utils import dummy_timelog, ordered
from .graphs import GraphHelper
from .settings import CACHE, LOGGER, TIMELOGGER


def louvain_partition(G, as_dict=False):
    with dummy_timelog("multigraph to weighted"):
        M = GraphHelper.multigraph_to_weighted_graph(G)
    nodes_cluster, score = cugraph.louvain(M)
    nodes = np.array(list(nodes_cluster.keys()))
    off_nodes = np.array(G.nodes)
    clusters = np.array(list(nodes_cluster.values()))
    s_clusters = ordered(off_nodes, nodes, clusters) # Need to sort the cluster cause the order is not keeped from louvain algo
    if as_dict:
        return dict(zip(off_nodes, s_clusters))
    return s_clusters
