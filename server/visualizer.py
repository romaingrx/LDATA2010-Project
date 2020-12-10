import random
import numpy as np
from bokeh.palettes import Spectral10, viridis

from .io import JSONHandler
from . import settings, layouts
from .settings import LOGGER, CACHE
from .graphs import EdgesHelper, NodesHelper, GraphHelper
from .utils import AttrDict, cur_graph, SnsPalette

def minmaxscale(x, min, max):
    assert max >= min
    x = np.array(x)
    x01 = (x-np.min(x))/(np.max(x)-np.min(x))
    print(x01)
    print(x01.min(), x01.max())
    y = (max-min)*x+min
    return y

class VisualizerHandler(object):

    @classmethod
    def color_callback(cls, attr, old, new):
        settings.LOGGER.info(f"Color \"{new}\" chosen")
        # TODO

    @classmethod
    @JSONHandler.update(path="plot.edges.thickness")
    def thickness_callback(cls, attr, old, new):
        settings.LOGGER.info(f"Thickness \"{new}\" chosen")
        CACHE.plot.edges.thickness = new
        Setter.edge_thickness(update=True)
    
    @classmethod
    @JSONHandler.update(path="layout")
    def layout_algo_callback(cls, event):
        settings.LOGGER.info(f"Layout algo \"{event.item}\" chosen")

        CACHE.layout = layouts.get(event.item)
        Setter.graph(update=True) 

    @classmethod
    @JSONHandler.update(path="plot.nodes.size")
    def node_size_callback(cls, attr, old, new):
        settings.LOGGER.info(f"Node size {new} chosen")
        CACHE.plot.nodes.size = int(new)
        Setter.node_sizes(update=True)

    @classmethod
    @JSONHandler.update(path="plot.nodes.basedon")
    def node_size_based_callback(cls, event):
        settings.LOGGER.info(f"Node size based on \"{event.item}\"")
        CACHE.plot.nodes.basedon = event.item 
        Setter.node_sizes(update=True)
        
    @classmethod
    @JSONHandler.update(path="plot.nodes.color_based_on")
    def node_color_callback(cls, event):
        CACHE.plot.nodes.color_based_on = event.item
        Setter.node_colors(update=True)
        

    @classmethod
    def timestep_callback(cls, attr, old, new):
        settings.LOGGER.info(f"Timestep \"{new}\" chosen")
        timestep = int(new)
        CACHE.plot.timestep = timestep
        Setter.all(update=True)


class Setter:
    NODE_BASED_ON = ["None", "Degree"]
    NODE_COLORS = ["random", "degree", "cluster"]
    __ALL_PALETTES = [viridis, SnsPalette("BuPu"), SnsPalette("Blues")]

    @classmethod
    def all(cls, update=True):
        if CACHE.plot.timestep not in CACHE.ultra:
            CACHE.ultra[CACHE.plot.timestep] = AttrDict(G=GraphHelper.subgraph_from_timestep(CACHE.graph, CACHE.plot.timestep))
        ga_dict = cls.graph_attribute(update=False)
        g_dict = cls.graph(update=False)
        e_dict = cls.edges(update=False)
        n_dict = cls.nodes(update=False)
        if update:
            CACHE.plot.edges.source.data.update(
                dict(
                    **e_dict,
                    **ga_dict.edges,
                    xs=g_dict["xs"],
                    ys=g_dict["ys"],
                )
            )
            CACHE.plot.source.data.update(
                dict(
                    **n_dict,
                    **ga_dict.nodes,
                    x=g_dict["x"],
                    y=g_dict["y"],
                )
            )
            cls.node_sizes(update=True)
            layouts.resize_x_y_fig()

    @classmethod
    def graph(cls, update=True):
        g_dict = layouts.apply_on_graph(CACHE.ultra[CACHE.plot.timestep].G)
        if update:
            CACHE.plot.edges.source.data.update(
                dict(
                    xs=g_dict["xs"],
                    ys=g_dict["ys"],
                )
            )
            CACHE.plot.source.data.update(
                dict(
                    x=g_dict["x"],
                    y=g_dict["y"],
                )
            )
            cls.node_sizes(update=True)
        return g_dict

    @classmethod
    def nodes(cls, update):
        sizes = cls.node_sizes(update)
        colors = cls.node_colors(update)
        return AttrDict(size=sizes, colors=colors)

    @classmethod
    def edges(cls, update):
        thickness = cls.edge_thickness(update)
        colors = cls.edge_colors(update)
        return AttrDict(thickness=thickness, colors=colors)


    @classmethod
    def node_sizes(cls, update):
        # TODO : adjust node size based on max x,y values (surface covered)
        # Hyperparams
        NODE_SIZE_MIN = 1e-3 * .05
        NODE_SIZE_MAX = 1e-3 * .1

        G = CACHE.ultra[CACHE.plot.timestep].G
        basedon = CACHE.plot.nodes.basedon
        if "x" in CACHE.plot.source.data:
            x = CACHE.plot.source.data["x"]
            y = CACHE.plot.source.data["y"]
            surface = (x.max() - x.min())*(y.max() - y.min())
        #    surface = max(100, surface)
        #    print(f"Surface {surface}")
        else:
            surface = 1
        if basedon == "None":
            new_value = np.ones(len(G.nodes))
        elif basedon == "Degree":
            degrees = NodesHelper.get_degree(G)
            #print(degrees)
            #ma = 2; mi = .5
            #deg_clip = mi + (ma-mi) * (degrees - degrees.min()) / (degrees.max())
            new_value = degrees
        else:
            return
        #new_value = MinMaxScaler().fit_transform([new_value]).reshape(-1)
        #new_value = .0001 * surface * NODE_SIZE_MAX * new_value / (NODE_SIZE_MIN * new_value.max())
        #print(new_value.min(), new_value.max())
        #new_value = minmaxscale(new_value, NODE_SIZE_MIN, NODE_SIZE_MAX)
        new_value = .001*np.sqrt(surface) * CACHE.plot.nodes.size * new_value / new_value.max()
        if update:
            CACHE.plot.source.data["size"] = new_value
        return new_value
    
    @classmethod
    def node_colors(cls, update):
        # TODO : degree : In progress
        # TODO : cluster :
        G = CACHE.ultra[CACHE.plot.timestep].G
        based_on = CACHE.plot.nodes.color_based_on
        data = CACHE.plot.source.data
        n_nodes = NodesHelper.length(G)
        if based_on == "random":
            palette = random.choice(cls.__ALL_PALETTES)
            new_colors = np.array(palette(n_nodes))
        elif based_on == "degree":
            degrees = NodesHelper.get_degree(G)
            udegrees = np.unique(degrees)
            colors = np.random.choice(cls.__ALL_PALETTES)(len(udegrees))
            sidx = udegrees.argsort()
            s_udegrees= udegrees[sidx]
            s_colors = colors[sidx]
            new_colors = s_colors[np.searchsorted(s_udegrees, degrees)]
        elif based_on == "cluster":
            new_colors = np.full(n_nodes, "#000000")
        else:
            LOGGER.warning(f"Color of nodes based on {based_on} not possible! Please choose between these types {cls.NODE_COLORS}")

        if update:
            print(new_colors)
            CACHE.plot.source.data["colors"] = new_colors
        return new_colors
    
    @classmethod
    def edge_thickness(cls, update):
        G = cur_graph()
        slider_thickness = CACHE.plot.edges.thickness
        thickness = [slider_thickness] * EdgesHelper.length(G)
        if update:
            CACHE.plot.edges.source.data["thickness"] = thickness
        return thickness
    
    @classmethod
    def edge_colors(cls, update):
        G = cur_graph()
        colors = [CACHE.plot.edges.color] * EdgesHelper.length(G)
        if update:
            CACHE.plot.edges.source.data["colors"] = colors
        return colors

    @classmethod
    def graph_attribute(cls, update):
        #G = GraphHelper.subgraph_from_timestep(CACHE.graph, CACHE.plot.timestep)
        G = CACHE.ultra[CACHE.plot.timestep].G
        nodes_attr = NodesHelper.get_all_attributes(G)
        edges_attr = EdgesHelper.get_all_attributes(G)
        return AttrDict(nodes=nodes_attr, edges=edges_attr)


