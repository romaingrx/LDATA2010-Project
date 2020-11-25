import os
import logging
import random

from bokeh.models import ColumnDataSource

from .utils import AttrDict

COLUMNS_NAME = (
    "timestep",
    "person1",
    "person2",
    "infected1",
    "infected2",
    "loc_lat",
    "loc_long",
    "home1_lat",
    "home1_long",
    "home2_lat",
    "home2_long",
)

TITLE = "Graph visualizer"

PLOT_TOOLS = "undo,redo,reset,hover,box_select,box_zoom,pan,wheel_zoom,save"

CACHE_DIR = os.path.join(os.curdir, ".cache_server")
LOGFILE = os.path.join(CACHE_DIR, "server.log")
LAST_CONFIG_FILE = os.path.join(CACHE_DIR, "config.json")

def get_logger(logfile, level):
    open(logfile, 'w').close()
    FORMATTER = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
    handler = logging.FileHandler(logfile)
    handler.setFormatter(FORMATTER)

    logger = logging.getLogger()
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

class RetrieveLastConfig(object):
    @classmethod
    def main(cls):
        graph = cls.retrieve_graph()
        return dict(
            graph=graph
        )
    
    @classmethod
    def retrieve_graph(cls):
        from . import io
        from . import templates
        raw_data = io.JSONHandler.get(('source', 'raw_data'))
        LOGGER.info(f"raw data : {raw_data}")
        graph = io.FileInputHandler.from_raw_to_graph(raw_data=raw_data) if raw_data != None else templates.get_random()
        LOGGER.info(f"graph : {graph}")
        return graph

def create_globals():
    global INITIALIZED, GRAPH, SOURCE, DOC, LOGGER, CACHE
    if not globals().get("INITIALIZED", False):
        INITIALIZED = True
        CACHE = AttrDict()
        CACHE.graph_attr = AttrDict()
        CACHE.plot = AttrDict()
        CACHE.plot.source = ColumnDataSource({})
        LOGGER = None

def init(level=logging.DEBUG):
    global GRAPH, SOURCE, DOC, LOGGER, CACHE
    LOGGER = get_logger(LOGFILE, level)
    GRAPH = RetrieveLastConfig.retrieve_graph()

create_globals()