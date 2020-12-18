import os
import yaml
import logging

FILEPATH = os.path.realpath(__file__)
SERVERDIR = os.path.dirname(FILEPATH)
CONFIGYAML = os.path.join(SERVERDIR, "static", "theme.yaml")

from bokeh.io import curdoc
from bokeh.themes import Theme
from bokeh.models import ColumnDataSource
from dask.distributed import Client
from dask_cuda import LocalCUDACluster

from .utils import AttrDict, deep_merge


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
    white="#ffffff",

    purple="#c08bc7",
    dark_purple="#330066",

    light_gb="#d1e0e0",
    very_light_gb="#f0f5f5"
)

STATIC = AttrDict(
    theme=AttrDict(
        attrs=AttrDict(
            Figure=AttrDict(
                background_fill_color=COLORS.very_light_gb,
                #background_fill_color=COLORS.white,
                border_fill_color=COLORS.light_gb,
                background_fill_alpha=1.0
            ),
        ),
    ),
    h1=COLORS.dark_purple,
    background=AttrDict(
        color=COLORS.black,
    ),
    widget=AttrDict(
        slider=AttrDict(
            bar_color=COLORS.purple,
            #text_color=COLORS.white
        )
    ),
    figure=AttrDict(
        x_range=[0, 1], # Needed to update the range later (why???)
        y_range=[0, 1],
    ),
    label=AttrDict(
        border_line_color=COLORS.dark_purple,
        background_fill_color=COLORS.light_gb,
        background_fill_alpha=.75,
    ),
    nodes_info="""mean degree : %.2f"""
)

DEFAULT = AttrDict(
    plot=AttrDict(
        network=AttrDict(
            edges=AttrDict(
               thickness=.2,
                color="#060606"
            )),
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
        for key in DEFAULT.plot.network.edges.keys():
            value = io.JSONHandler.get(("plot", "network", "edges", key)) or DEFAULT.plot.network.edges[key]
            edges_values[key] = value
            if apply_on_cache:
                CACHE.plot.network.edges[key] = value

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
    CACHE.ultra = AttrDict()
    CACHE.plot.layouts = AttrDict()

    CACHE.plot.nodes.source.data = {}
    CACHE.plot.network.edges.source.data = {}

    CACHE.plot.statistics.matrix.source.data = {}
    CACHE.plot.statistics.degree_distribution.source.data = {}


def create_globals():
    global INITIALIZED, LOGGER, CACHE
    if "INITIALIZED" not in globals():
        INITIALIZED = True

        # Globals
        CACHE = AttrDict()
        CACHE.plot = AttrDict()
        CACHE.renderers = AttrDict()
        CACHE.widgets = AttrDict()

        # Network
        CACHE.plot.network = AttrDict()
        CACHE.plot.network.widgets = AttrDict()
        CACHE.graph_attr = AttrDict()
        CACHE.ultra = AttrDict()
        CACHE.plot.network.edges = AttrDict()
        CACHE.plot.nodes = AttrDict()
        CACHE.plot.nodes.source = ColumnDataSource({})
        CACHE.plot.network.edges.source = ColumnDataSource({})

        # Statistics

        CACHE.plot.statistics = AttrDict()
        CACHE.plot.statistics.matrix = AttrDict()
        CACHE.plot.statistics.degree_distribution = AttrDict()
        CACHE.plot.statistics.matrix.source = ColumnDataSource({})
        CACHE.plot.statistics.degree_distribution.source = ColumnDataSource({})
        CACHE.plot.statistics.widgets = AttrDict()


        # Maps

        CACHE.plot.maps = AttrDict()
        CACHE.plot.maps.widgets = AttrDict()

        reset_plot_dict()

def update_theme():
    theme = yaml.load(open(CONFIGYAML, 'r'))
    to_update_theme = deep_merge(theme, STATIC.theme)
    yaml_theme_str = yaml.dump(to_update_theme, default_flow_style=False, sort_keys=False)
    LOGGER.info(f"Updated config to ::\n{yaml_theme_str}")
    with open(CONFIGYAML, 'w') as fd:
        fd.write(yaml_theme_str)
    curdoc().theme = Theme(filename=CONFIGYAML)
    return to_update_theme
    

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