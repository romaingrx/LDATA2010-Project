import numpy as np
from sklearn.preprocessing import MinMaxScaler

from .io import JSONHandler
from . import settings, layouts
from .settings import LOGGER, CACHE
from .graphs import EdgesHelper, NodesHelper, GraphHelper
from .utils import AttrDict, cur_graph

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
    def timestep_callback(cls, attr, old, new):
        settings.LOGGER.info(f"Timestep \"{new}\" chosen")
        timestep = int(new)
        CACHE.plot.timestep = timestep
        Setter.all(update=True)


class Setter:
    NODE_BASED_ON = ["None", "Degree"]

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
        G = CACHE.ultra[CACHE.plot.timestep].G
        basedon = CACHE.plot.nodes.basedon
        if basedon == "None":
            new_value = [CACHE.plot.nodes.size * .001] * len(G.nodes)
        elif basedon == "Degree":
            degrees = NodesHelper.get_degree(G)
            ma = 2*CACHE.plot.nodes.size*.0001; mi = .5*CACHE.plot.nodes.size*.0001
            deg_clip = mi + (ma-mi) * (degrees - degrees.min()) / (degrees.max())
            new_value = deg_clip * CACHE.plot.nodes.size
        else:
            return
        if update:
            CACHE.plot.source.data["size"] = new_value
        return new_value
    
    @classmethod
    def node_colors(cls, update):
        G = CACHE.ultra[CACHE.plot.timestep].G
        colors = [CACHE.plot.nodes.color] * len(G.nodes)
        if update:
            CACHE.plot.source.data["colors"] = colors
        return colors
    
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


