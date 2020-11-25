import random
import numpy as np
import pandas as pd
import networkx as nx
from abc import ABC, abstractclassmethod

from .settings import CACHE


def random_layout(G:nx.Graph):
    return dict(zip(G, np.random.random((len(G.nodes), 2))))


# ----------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------

def update_edges():
    # TODO : update edges coords  

    x = CACHE.plot.source.data["x"]
    y = CACHE.plot.source.data["y"]

    [u, v] = np.array(CACHE.graph.edges).T
    
    E = len(CACHE.graph.edges)
    xs = np.zeros((E, 2)) 
    ys = np.zeros((E, 2)) 

    xs[:, 0] = x[u]
    xs[:, 1] = x[v]

    ys[:, 0] = y[u]
    ys[:, 1] = y[v]

    CACHE.plot.edges.source.data.update(
        dict(
            xs = list(xs),
            ys = list(ys)
        )
    )


def apply_on_graph():
    # TODO : a thread to apply a continuous update?  (force layout); if so, share an updater thread in the cache
    G = CACHE.graph
    pos = CACHE.layout(G)

    # TODO : Speedup this shit (no sorting?)
    sorted_pos = sorted(pos.items(), key=lambda x:x[0])
    coords = np.array(list(pos.values())).T # shape (2, V)

    CACHE.plot.source.data.update(
        dict(
            x = coords[0],
            y = coords[1]
        )
    )

    update_edges()

AVAILABLE = dict(
    circular=nx.circular_layout,
    #spectral=nx.drawing.layout.spectral_layout,
    #fruchterman_reingold=nx.layout.fruchterman_reingold_layout
    random=random_layout,
)

def get(key:str):
    return AVAILABLE.get(key, None)

def get_random():
    return random.choice(list(AVAILABLE.values()))