from .io import JSONHandler
from . import settings, layouts
from .settings import LOGGER, CACHE

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
        JSONHandler.update_last_config(
            dict(
                layout=event.item
            )
        )

        CACHE.layout = layouts.get(event.item)
        layouts.apply_on_graph()

    
    @classmethod
    def timestep_callback(cls, attr, old, new):
        settings.LOGGER.info(f"Timestep \"{new}\" chosen")
        #TODO