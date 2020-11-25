from . import settings, layouts
from .settings import LOGGER, CACHE

from holoviews.element.graphs import layout_nodes

class VisualizerHandler(object):

    @classmethod
    def color_callback(cls, attr, old, new):
        settings.LOGGER.info(f"Color \"{new}\" chosen")
        # TODO

    @classmethod
    def thickness_callback(cls, attr, old, new):
        settings.LOGGER.info(f"Thickness \"{new}\" chosen")
        # TODO
    
    @classmethod
    def layout_algo_callback(cls, event):
        settings.LOGGER.info(f"Layout algo \"{event.item}\" chosen")

        #TODO
    
    @classmethod
    def timestep_callback(cls, attr, old, new):
        settings.LOGGER.info(f"Timestep \"{new}\" chosen")
        layout_nodes(CACHE.plot.graph, layouts.get(new))
        #TODO