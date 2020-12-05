from .io import JSONHandler
from . import settings, layouts
from .settings import LOGGER, CACHE

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
        Setter.edge_thickness()
    
    @classmethod
    @JSONHandler.update(path="layout")
    def layout_algo_callback(cls, event):
        settings.LOGGER.info(f"Layout algo \"{event.item}\" chosen")
        

        CACHE.layout = layouts.get(event.item)
        layouts.apply_on_graph()
    
    @classmethod
    @JSONHandler.update(path="plot.nodes.size")
    def node_size_callback(cls, attr, old, new):
        settings.LOGGER.info(f"Node size {new} chosen")
        CACHE.plot.nodes.size = int(new)
        Setter.node_sizes() 

    @classmethod
    @JSONHandler.update(path="plot.nodes.basedon")
    def node_size_based_callback(cls, event):
        settings.LOGGER.info(f"Node size based on \"{event.item}\"")
        CACHE.plot.nodes.basedon = event.item 
        Setter.node_sizes()

    @classmethod
    def timestep_callback(cls, attr, old, new):
        settings.LOGGER.info(f"Timestep \"{new}\" chosen")
        #TODO


class Setter:

    NODE_BASED_ON = ["None", "Degree"]

    @classmethod
    def main(cls):
        cls.node_sizes()
        cls.node_colors()
        cls.edge_thickness()
        cls.edge_colors()

    @classmethod
    def node_sizes(cls):
        basedon = CACHE.plot.nodes.basedon
        if basedon == "None":
            new_value = [CACHE.plot.nodes.size] * len(CACHE.graph.nodes())
        elif basedon == "Degree":
            ma = 2; mi = .25
            deg_clip = CACHE.plot.source.data["degree"]
            deg_clip = mi + (deg_clip - deg_clip.min()) / (deg_clip.max()/(ma-mi))
            new_value = deg_clip * CACHE.plot.nodes.size
        else:
            pass
        CACHE.plot.source.data["size"] = new_value
    
    @classmethod
    def node_colors(cls):
        CACHE.plot.source.data["colors"] = [CACHE.plot.nodes.color] * len(CACHE.graph.nodes())
    
    @classmethod
    def edge_thickness(cls):
        thickness = CACHE.plot.edges.thickness
        CACHE.plot.edges.source.data["thickness"] = [thickness] * len(CACHE.graph.edges())
    
    @classmethod
    def edge_colors(cls):
        CACHE.plot.edges.source.data["colors"] = [CACHE.plot.edges.color] * len(CACHE.graph.edges())
