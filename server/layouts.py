import random
import numpy as np
import numpy_indexed as npi
import pandas as pd
import networkx as nx
from bokeh.models import Range1d
from abc import ABC, abstractclassmethod
from threading import Thread
from multiprocessing import Process

from .settings import CACHE, LOGGER
from .graphs import EdgesHelper, NodesHelper, GraphHelper
from .utils import AttrDict

from fa2 import ForceAtlas2

def random_layout(G:nx.Graph):
    return dict(zip(G, np.random.random((len(G.nodes), 2))))


class Layout:
    def __name__(self):
        return self.__class__.__name__

class ForceLayout(Layout):
    def __init__(self):
        self.fa2 = ForceAtlas2(
                          # Behavior alternatives
                          outboundAttractionDistribution=True,  # Dissuade hubs
                          linLogMode=False,  # NOT IMPLEMENTED
                          adjustSizes=False,  # Prevent overlap (NOT IMPLEMENTED)
                          edgeWeightInfluence=3.0,

                          # Performance
                          jitterTolerance=1.0,  # Tolerance
                          barnesHutOptimize=True,
                          barnesHutTheta=1.4,
                          multiThreaded=False,  # NOT IMPLEMENTED

                          # Tuning
                          scalingRatio=3.0,
                          strongGravityMode=True,
                          gravity=1.0,

                          # Log
                          verbose=True)
    
    
    def __call__(self, G):
        layout = self.fa2.forceatlas2_networkx_layout(CACHE.graph, pos=None, iterations=100)
        return layout



# ----------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------

def update_edges(G, nodes, x, y):
    # TODO : update edges coords  

    #x = CACHE.plot.source.data["x"]
    #y = CACHE.plot.source.data["y"]

    #[u, v, count] = EdgesHelper.count_attribute(CACHE.graph, "timestep", leq=CACHE.plot.timestep, sort=True)
    [u, v, c] = np.array(G.edges).T
    [u, v] = np.unique(np.c_[u, v], axis=0).T

    u_idx = npi.indices(nodes, u)
    v_idx = npi.indices(nodes, v)

    xs = np.c_[x[u_idx], x[v_idx]]
    ys = np.c_[y[u_idx], y[v_idx]]

    return xs, ys


def apply_on_nodes(x, y):
    CACHE.plot.source.data["x"] = x
    CACHE.plot.source.data["y"] = y

def apply_on_edges(xs, ys):
    CACHE.plot.edges.source.data["xs"] = xs #np.array(xs, dtype=np.float)
    CACHE.plot.edges.source.data["ys"] = ys # np.array(ys, dtype=np.float)
    #CACHE.plot.edges.source.data.update(
    #    dict(
    #        xs=xs,
    #        ys=ys
    #    )
    #)
        #CACHE.plot.edges.source.data['xs'] = xs
        #CACHE.plot.edges.source.data['ys'] = ys

def resize_x_y_fig(x, y):
    CACHE.plot.p.x_range = Range1d(x.min(), x.max())
    CACHE.plot.p.y_range = Range1d(y.min(), y.max())

def apply_on_graph(G, update=False):
    # TODO : a thread to apply a continuous update?  (force layout); if so, share an updater thread in the cache
    #G = GraphHelper.subgraph_from_timestep(CACHE.graph, CACHE.plot.timestep)

    # Try getting it from the cache
    #if CACHE.layout.__name__ in CACHE.plot.layouts:
    if False:
        computed_layout = CACHE.plot.layouts[CACHE.layout.__name__]
        x, y = computed_layout.x, computed_layout.y
        xs, ys = computed_layout.xs, computed_layout.ys
    else: # Compute the new layout
        pos = CACHE.layout(G)
        # TODO : Speedup this shit (no sorting?)
        #sorted_pos = sorted(pos.items(), key=lambda x:x[0])
        nodes, pos = list(zip(*pos.items()))
        pos = np.array(pos); nodes = np.array(nodes)

        [x, y] = pos.T # shape (2, V)
        xs, ys = update_edges(G, nodes, x, y)

        # Save the computed layout in the cache in order to compute only once
        xs, ys = list(xs), list(ys)
        CACHE.plot.layouts[CACHE.layout.__name__] = AttrDict(
            x=x,
            y=y,
            xs=xs,
            ys=ys
            )

    if update:
         te = Thread(target=apply_on_edges, args=(xs, ys))
         te.start()
         tn = Thread(target=apply_on_nodes, args=(x, y))
         tn.start()
         if "p" in CACHE.plot:
             resize_x_y_fig(x, y)

         te.join(); tn.join()


    return AttrDict(nodes=nodes, x=x, y=y, xs=xs, ys=ys)


AVAILABLE = dict(
    # Simple layouts
    random=random_layout,
    circular=nx.circular_layout,

    # Networkx layouts
    spectral=nx.drawing.layout.spectral_layout,
    fruchterman_reingold=nx.layout.fruchterman_reingold_layout,
    kamada_kawai=nx.layout.kamada_kawai_layout,

    # Force layouts
    forceatlas2=ForceLayout(),
)

def get(key:str):
    return AVAILABLE.get(key, None)

def get_random():
    return random.choice(list(AVAILABLE.values()))
