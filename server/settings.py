import os
import logging

from bokeh.models import ColumnDataSource
from dask.distributed import Client
from dask_cuda import LocalCUDACluster

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

COLORS = AttrDict(
    black="#191a1a",
    white="#000000",
    purple="#c08bc7",
)

STATIC = AttrDict(
    background=AttrDict(
        color=COLORS.black,
    ),
    widget=AttrDict(
        slider=AttrDict(
            bar_color=COLORS.purple,
            #text_color=COLORS.white
        )
    )
)

DEFAULT = AttrDict(
    plot=AttrDict(
        edges=AttrDict(
           thickness=.2,
            color="#060606"
        ),
        nodes=AttrDict(
            basedon="Same",
            size=20,
            color="#FF00FF",
            color_based_on="random"
        ),
    ),
    palette="random",
    layout="random",
    renderers=AttrDict(
        current=0,
    )
)

TITLE = "Graph visualizer"

PLOT_TOOLS = "undo,redo,reset,hover,box_select,box_zoom,pan,wheel_zoom,save"

CACHE_DIR = os.path.join(os.curdir, ".cache_server")
LOGFILE = os.path.join(CACHE_DIR, "server.log")
TIMELOGFILE = os.path.join(CACHE_DIR, "timeserver.log")
LAST_CONFIG_FILE = os.path.join(CACHE_DIR, "config.json")

def get_logger(logfile, level):
    open(logfile, 'w').close()
    FORMATTER = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
    handler = logging.FileHandler(logfile)
    handler.setFormatter(FORMATTER)

    logger = logging.getLogger(logfile)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

class RetrieveLastConfig(object):
    @classmethod
    def main(cls, apply_on_cache=False):
        cls.retrieve_defaults()
        return dict(
            edges=cls.retrieve_edges(apply_on_cache),
            nodes=cls.retrieve_nodes(apply_on_cache),
            layout=cls.retrieve_layout_algo(apply_on_cache),
            graph=cls.retrieve_graph(apply_on_cache),
        )
    
    @classmethod
    def retrieve_graph(cls, apply_on_cahe=False):
        from . import io
        from . import templates
        raw_data = io.JSONHandler.get(('source', 'raw_data'))
        #LOGGER.info(f"raw data : {raw_data}")
        graph = io.FileInputHandler.from_raw_to_graph(raw_data) if raw_data != None else templates.get_random()
        #LOGGER.info(f"graph : {graph}")

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
        for key in DEFAULT.plot.edges.keys():
            value = io.JSONHandler.get(("plot", "edges", key)) or DEFAULT.plot.edges[key]
            edges_values[key] = value
            if apply_on_cache:
                CACHE.plot.edges[key] = value

        return edges_values

    @classmethod 
    def retrieve_nodes(cls, apply_on_cache=False):
        from . import io
        nodes_values = AttrDict()
        for key in DEFAULT.plot.nodes.keys():
            value = io.JSONHandler.get(("plot", "nodes", key)) or DEFAULT.plot.nodes[key]
            nodes_values[key] = value
            if apply_on_cache:
                CACHE.plot.nodes[key] = value

        return nodes_values

    @classmethod
    def retrieve_defaults(cls):
        CACHE.renderers = DEFAULT.renderers

def reset_plot_dict():
    CACHE.plot.source.data = {}
    CACHE.plot.edges.source.data = {}
    CACHE.plot.layouts = AttrDict()
    CACHE.ultra = AttrDict()


def create_globals():
    global INITIALIZED, LOGGER, CACHE
    if "INITIALIZED" not in globals():
        INITIALIZED = True

        # Globals
        CACHE = AttrDict()
        CACHE.plot = AttrDict()

        # Network
        CACHE.graph_attr = AttrDict()
        CACHE.renderers = AttrDict()
        CACHE.ultra = AttrDict()
        CACHE.plot.edges = AttrDict()
        CACHE.plot.nodes = AttrDict()
        CACHE.plot.source = ColumnDataSource({})
        CACHE.plot.edges.source = ColumnDataSource({})

        # Statistics

        #CACHE.widgets = AttrDict()
        CACHE.plot.network = AttrDict()
        CACHE.plot.statistics = AttrDict()
        CACHE.plot.network.widgets = AttrDict()
        CACHE.plot.statistics.widgets = AttrDict()

        reset_plot_dict()

def init(level=logging.DEBUG):
    global LOGGER, TIMELOGGER, CACHE
    # DISABLED
    #cluster = LocalCUDACluster(
    #    protocol="ucx",
    #    enable_tcp_over_ucx=True,
    #    enable_infiniband=False
    #)
    #client = Client(cluster)
    #CACHE.cluster = cluster
    #CACHE.client = client
    LOGGER = get_logger(LOGFILE, level)
    TIMELOGGER = get_logger(TIMELOGFILE, level)
    RetrieveLastConfig.main(apply_on_cache=True)

if "INITIALIZED" not in globals():
    create_globals()
    init()