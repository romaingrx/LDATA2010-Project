import random
import cugraph
import numpy as np
import networkx as nx
from bokeh.core.properties import Color
from bokeh.plotting import curdoc
from bokeh.models import Range1d
from bokeh.models import BoxZoomTool

from .io import JSONHandler
from . import settings, layouts, algorithms
from .settings import LOGGER, STATIC, CACHE, COLORS
from .graphs import EdgesHelper, NodesHelper, GraphHelper
from .utils import AttrDict, cur_graph, SnsPalette, assign_color_from_class, dummy_timelog, ordered, resize, dummy_scale, timestep_cache

class VisualizerHandler(object):

    @classmethod
    def color_callback(cls, attr, old, new):
        raise Exception("Replaced by palette choice")
        settings.LOGGER.info(f"Color \"{new}\" chosen")
        # TODO

    @classmethod
    @JSONHandler.update(path="plot.edges.thickness")
    def thickness_callback(cls, attr, old, new):
        settings.LOGGER.info(f"Thickness \"{new}\" chosen")
        CACHE.plot.network.edges.thickness = new
        Setter.edge_thickness(update=True)

    @classmethod
    @JSONHandler.update(path="layout")
    def layout_algo_callback(cls, event):
        settings.LOGGER.info(f"Layout algo \"{event.item}\" chosen")

        CACHE.layout = layouts.get(event.item)
        Setter.graph(update=True)
        layouts.resize_x_y_fig()

    @classmethod
    @JSONHandler.update(path="palette")
    def palette_callback(cls, event):
        CACHE.palette = Setter.ALL_PALETTES.get(event.item)
        Setter.colors(update=True)

    @classmethod
    @JSONHandler.update(path="plot.nodes.size")
    def node_size_callback(cls, attr, old, new):
        print("HERE")
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

    @classmethod
    def renderer_visualisation_callback(cls):
        all_layouts = CACHE.plot.all_layouts
        current_idx = CACHE.renderers.current
        next_idx = (current_idx+1)%len(all_layouts)
        next_next_idx = (current_idx+2)%len(all_layouts)
        curdoc().remove_root(all_layouts[current_idx])
        curdoc().add_root(all_layouts[next_idx])
        CACHE.widgets.renderer_button.label = Setter.RENDERERS[next_next_idx]
        #CACHE.widgets.renderer_button.background = COLORS.white if current_idx == 0 else COLORS.purple
        CACHE.renderers.current = next_idx
        #Setter.change_renderers(current)
    
    @classmethod
    def selected_nodes_callback(cls, attr, old, new):
        Setter.nodes_metrics(update=True, indices=new if new!=[] else None)        



class Setter:
    NODE_BASED_ON = ["Same", None, "Degree","Katz centrality"
                     #"infected"
                     ]
    NODE_COLORS = ["Random", None, "Degree", "Katz centrality", None, "Louvain"]
    __ALL_PALETTES = [SnsPalette("BuPu"), SnsPalette("Blues"), SnsPalette("husl")]
    ALL_PALETTES = {
        "random":lambda size:np.random.choice(Setter.__ALL_PALETTES)(size),
        "None":None,
        "BuPu (purple)":__ALL_PALETTES[0],
        "Blues (blue)":__ALL_PALETTES[1],
        "categorical":None,
        "husl":__ALL_PALETTES[2]
    }
    RENDERERS = ["Network visualisation", "Statistics visualisation", "Maps visualisation"]

    @classmethod
    def all(cls, update=True):
        ga_dict = cls.graph_attribute(update=False)
        g_dict = cls.graph(update=False)
        e_dict = cls.edges(update=False)
        n_dict = cls.nodes(update=False)

        adj_dict = cls.adjacency_metrics(update=False)
        _degree_dist = cls.degree_distribution_metrics(update)
        if update:
            CACHE.plot.network.edges.source.data.update(
                dict(
                    **e_dict,
                    **ga_dict.edges,
                    **g_dict.edges,
                    #xs=g_dict["xs"],
                    #ys=g_dict["ys"],
                )
            )
            CACHE.plot.nodes.source.data.update(
                dict(
                    **n_dict,
                    **ga_dict.nodes,
                    **g_dict.nodes,
                    #x=g_dict["x"],
                    #y=g_dict["y"],
                )
            )
            CACHE.plot.statistics.matrix.source.data.update(
                dict(
                    **adj_dict
                )
            )
            cls.node_sizes(update=True)
            cls.colors(update=True)
            cls.resize()

    @classmethod
    def graph(cls, update=True):
        g_dict = layouts.apply_on_graph(cur_graph())
        if update:
            CACHE.plot.network.edges.source.data.update(
                dict(
                    **g_dict.edges
                )
            )
            CACHE.plot.nodes.source.data.update(
                dict(
                    **g_dict.nodes
                )
            )
            cls.node_sizes(update=True)
        return g_dict

    @classmethod
    def colors(cls, update):
        nodes = cls.node_colors(update=update)
        adjacency = cls.adjacency_colors(update=update)
        degree_distribution = cls.degree_distribution_colors(update=update)
        return dict(nodes=nodes, adjacency=adjacency, degree_distribution=degree_distribution)

    @classmethod
    def resize(cls):
        cls.degree_distribution_resize()
        cls.adjacency_resize()
        cls.maps_resize()
        layouts.resize_x_y_fig()


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
        # Hyperparams
        FACTOR = 5
        NODE_SIZE_MAX = .0025
        NODE_SIZE_MIN = NODE_SIZE_MAX/FACTOR

        G = cur_graph()
        basedon = CACHE.plot.nodes.basedon
        if "x" in CACHE.plot.nodes.source.data:
            x = CACHE.plot.nodes.source.data["x"]
            y = CACHE.plot.nodes.source.data["y"]
            surface = (x.max() - x.min())*(y.max() - y.min())
        else:
            surface = 1
        if basedon == "Same":
            new_value = 2. * np.ones(len(G.nodes))
        elif basedon == "Degree":
            degrees = NodesHelper.get_degree(G)
            new_value = degrees
        elif basedon == "Katz centrality":
            W = timestep_cache().W
            katz_centrality = algorithms.katz_centrality(W)
            new_value = katz_centrality
        else:
            LOGGER.warning(f"Size of nodes based on {basedon} not known")
            return []

        #new_value = 1.5e-3 * np.sqrt(surface) * CACHE.plot.nodes.size * new_value / new_value.max() # WORKING BEST
        new_value = CACHE.plot.nodes.size * np.sqrt(surface) * dummy_scale(new_value, NODE_SIZE_MIN, NODE_SIZE_MAX)
        if update:
            CACHE.plot.nodes.source.data["size"] = new_value
        return new_value
    
    @classmethod
    def node_colors(cls, update):
        def color_from_layout(G, layout, palette):
            partition = layout(G)
            new_colors = assign_color_from_class(partition, palette)
            return new_colors

        G = cur_graph()
        based_on = CACHE.plot.nodes.color_based_on
        palette = CACHE.get("palette", Setter.ALL_PALETTES["random"])
        n_nodes = NodesHelper.length(G)
        if based_on == "Random":
            new_colors = np.array(palette(n_nodes))
        elif based_on == "Degree":
            degrees = NodesHelper.get_degree(G)
            new_colors = assign_color_from_class(degrees, palette)
        elif based_on in ("Louvain", "Katz centrality"):
            new_colors = color_from_layout(G, algorithms.get(based_on), palette)
        else:
            LOGGER.warning(f"Color of nodes based on {based_on} not possible! Please choose between these types {cls.NODE_COLORS}")

        if update:
            CACHE.plot.nodes.source.data["colors"] = new_colors
        return new_colors
    
    @classmethod
    def edge_thickness(cls, update):
        G = cur_graph()
        slider_thickness = CACHE.plot.network.edges.thickness
        thickness = [slider_thickness] * EdgesHelper.length(G)
        if update:
            CACHE.plot.network.edges.source.data["thickness"] = thickness
        return thickness
    
    @classmethod
    def edge_colors(cls, update):
        G = cur_graph()
        colors = [CACHE.plot.network.edges.color] * EdgesHelper.length(G)
        if update:
            CACHE.plot.network.edges.source.data["colors"] = colors
        return colors

    @classmethod
    def graph_attribute(cls, update):
        G = cur_graph()
        nodes_attr = NodesHelper.get_all_attributes(G)
        edges_attr = EdgesHelper.get_all_attributes(G)
        return AttrDict(nodes=nodes_attr, edges=edges_attr)

    @classmethod
    def change_renderers(cls, current):
        raise Exception("DEPRECATED")
        if current == 0:
            for wid in CACHE.plot.network.widgets.values():
                wid.visible = True
        else:
            for wid in CACHE.plot.network.widgets.values():
                wid.visible = False
        return


    @classmethod
    def adjacency(cls, update):
        metrics = cls.adjacency_metrics(update=False)
        colors = cls.adjacency_colors(update=False)
        ret_dict = dict(**metrics, **colors)
        if update:
            CACHE.plot.statistics.matrix.source.data.update(ret_dict)
        return ret_dict

    @classmethod
    def adjacency_resize(cls):
        p = CACHE.plot.statistics.matrix.get("p", False)
        if p:
            #counts = CACHE.plot.statistics.degree_distribution.source.data["counts"]
            size = CACHE.plot.statistics.matrix.source.data["size"]
            x = CACHE.plot.statistics.matrix.source.data["x"]
            y = CACHE.plot.statistics.matrix.source.data["y"]
            x_range = resize(x, size, alpha=1.1)
            y_range = resize(y, size, alpha=1.1)
            [p.x_range.start, p.x_range.end] = x_range
            [p.y_range.start, p.y_range.end] = y_range
            LOGGER.info(f"Resized adjacency graph :: x_range {x_range} :: y_range {y_range}")
            return True
        return False

    @classmethod
    def adjacency_metrics(cls, update):
        G = cur_graph()
        M = nx.adjacency_matrix(G).tocoo()

        data = M.data
        x = M.row
        y = M.col
        size = .45 * data / data.max()

        ret_dict = dict(x=x, y=y, size=size)
        if update:
            CACHE.plot.statistics.matrix.source.data.update(
                ret_dict
            )
        return ret_dict

    @classmethod
    def adjacency_colors(cls, update):
        palette = CACHE.get("palette", Setter.ALL_PALETTES["random"])
        size = CACHE.plot.statistics.matrix.source.data["size"]
        colors = assign_color_from_class(size, palette)
        ret_dict = dict(colors=colors)
        if update:
            CACHE.plot.statistics.matrix.source.data.update(ret_dict)
        return ret_dict

    @classmethod
    def degree_distribution(cls, update):
        metrics = cls.degree_distribution_metrics(False)
        colors = cls.degree_distribution_colors(False)
        ret_dict = AttrDict(**metrics, **colors)
        if update:
            CACHE.plot.statistics.degree_distribution.p.xaxis.major_label_overrides = dict(zip(np.arange(len(ret_dict.degree)), ret_dict.degree+1))
            CACHE.plot.statistics.degree_distribution.source.data.update(ret_dict)
            return ret_dict

    @classmethod
    def degree_distribution_metrics(cls, update):
        G = cur_graph()
        nodes_degrees = dict(G.degree())
        degrees = list(nodes_degrees.values())
        udegrees, counts = np.unique(degrees, return_counts=True)
        sidx = np.argsort(counts)
        udegrees, counts = udegrees[sidx], counts[sidx]

        x = np.arange(len(counts))
        x = udegrees        
        y = counts / 2


        width = .85 * np.ones_like(udegrees)

        ret_dict = dict(degree=udegrees, counts=counts, x=x, y=y, width=width)

        if update:
            CACHE.plot.statistics.degree_distribution.source.data.update(ret_dict)
        return ret_dict

    @classmethod
    def degree_distribution_resize(cls):
        p = CACHE.plot.statistics.degree_distribution.get("p", False)
        if p:
            LOGGER.info("Resized degree distribution graph")
            counts = CACHE.plot.statistics.degree_distribution.source.data["counts"]
            x = CACHE.plot.statistics.degree_distribution.source.data["x"]
            width = CACHE.plot.statistics.degree_distribution.source.data["width"]
            p.y_range.start = -.01; p.y_range.end = 1.05 * np.max(counts)
            p.x_range.start = np.min(x)-.75*width[0]; p.x_range.end = np.max(x)+.75*width[-1]
            return True
        return False

    @classmethod
    def degree_distribution_colors(cls, update):
        palette = CACHE.get("palette", Setter.ALL_PALETTES["random"])
        counts = CACHE.plot.statistics.degree_distribution.source.data["counts"]
        #colors = palette(len(counts))[::-1]
        colors = assign_color_from_class(counts, palette)
        ret_dict = dict(colors=colors)
        if update:
            CACHE.plot.statistics.degree_distribution.source.data.update(ret_dict)
        return ret_dict


    @classmethod
    def maps_resize(cls, *args, **kwargs):
        p = CACHE.plot.maps.get("p_maps", False)
        if p:
            home_x, home_y = NodesHelper.get_attributes(cur_graph(), ["home_x", "home_y"])
            x_merc_range = resize(home_x, alpha=1.2)
            y_merc_range = resize(home_y, alpha=1.2)
            p.x_range.start, p.x_range.end = x_merc_range
            p.y_range.start, p.y_range.end = y_merc_range
            LOGGER.info(f"Resized maps :: x_range {x_merc_range} :: y_range {y_merc_range}")
            return True
        return False

    @classmethod
    def nodes_metrics(cls, update, indices=None):
        G = cur_graph()
        degrees = NodesHelper.get_degree(G)
        if indices is not None:
            indices = np.array(indices)
            degrees = degrees[indices]
        mean_degree = np.mean(degrees)
        s = STATIC.nodes_info%(mean_degree)
        if update:
            CACHE.plot.nodes_info.text = s
        return s

