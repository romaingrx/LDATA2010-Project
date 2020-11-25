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

DEFAULT = AttrDict(
    plot=AttrDict(
        edges=AttrDict(
            thickness=20,
            color="#FFFFFF"
        ),
        nodes=AttrDict(
            size=20,
            color="#FFFFFF"
        ),
    ),
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
    def main(cls, apply_on_cache=False):
        return dict(
            layout=cls.retrieve_layout_algo(apply_on_cache),
            graph=cls.retrieve_graph(apply_on_cache),
            edges=cls.retrieve_edges(apply_on_cache),
            nodes=cls.retrieve_nodes(apply_on_cache),
        )
    
    @classmethod
    def retrieve_graph(cls, apply_on_cahe=False):
        from . import io
        from . import templates
        raw_data = io.JSONHandler.get(('source', 'raw_data'))
        LOGGER.info(f"raw data : {raw_data}")
        graph = io.FileInputHandler.from_raw_to_graph(raw_data=raw_data) if raw_data != None else templates.get_random()
        LOGGER.info(f"graph : {graph}")

        if apply_on_cahe:
            CACHE.graph = graph
            CACHE.raw_data = raw_data

        return graph
    
    @classmethod
    def retrieve_layout_algo(cls, apply_on_cache=False):
        from . import io
        from . import layouts
        layout_string = io.JSONHandler.get("layout")
        layout = layouts.get(layout_string) if layout_string != None else layouts.get_random()

        if apply_on_cache:
            CACHE.layout = layout

        return layout

    @classmethod 
    def retrieve_edges(cls, apply_on_cache=False):
        from . import io
        edges_values = AttrDict()
        for key in ("thickness", "color"):
            value = io.JSONHandler.get(("plot", "edges", key)) or DEFAULT.plot.edges[key]
            edges_values[key] = value
            if apply_on_cache:
                CACHE.plot.edges[key] = value

        return edges_values

    @classmethod 
    def retrieve_nodes(cls, apply_on_cache=False):
        from . import io
        nodes_values = AttrDict()
        for key in ("size", "color"):
            value = io.JSONHandler.get(("plot", "nodes", key)) or DEFAULT.plot.nodes[key]
            nodes_values[key] = value
            if apply_on_cache:
                CACHE.plot.nodes[key] = value

        return nodes_values

#def create_void_cache(swimming_keys):
#    CACHE = AttrDict()
#    def recursive_creator(cache, keys):
#        if isinstance(keys, tuple):
#            for key in keys:
#                recursive_creator(cache, key)
#        else:
#            cache[keys] = AttrDict()


def create_globals():
    global INITIALIZED, LOGGER, CACHE
    if not globals().get("INITIALIZED", False):
        INITIALIZED = True
        CACHE = AttrDict()
        CACHE.graph_attr = AttrDict()
        CACHE.plot = AttrDict()
        CACHE.plot.control = AttrDict()
        CACHE.plot.edges = AttrDict()
        CACHE.plot.nodes = AttrDict()
        CACHE.plot.source = ColumnDataSource({})
        CACHE.plot.edges.source = ColumnDataSource({})
        LOGGER = None

def init(level=logging.DEBUG):
    global LOGGER, CACHE
    LOGGER = get_logger(LOGFILE, level)
    RetrieveLastConfig.main(apply_on_cache=True)

create_globals()