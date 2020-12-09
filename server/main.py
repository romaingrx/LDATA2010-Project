from bokeh.models import ColumnDataSource, Circle, Plot, Div, ColorPicker, Dropdown, Slider, GraphRenderer, MultiLine, HoverTool, Ellipse
from bokeh.models.widgets import FileInput, Panel
from bokeh.plotting import curdoc, figure, show, from_networkx
from bokeh.layouts import row, column, layout
from bokeh.palettes import Spectral8
from bokeh.resources import Resources
from bokeh.io.state import curstate
import networkx as nx


from . import settings, layouts
from .io import FileInputHandler
from .utils import AttrDict
from .visualizer import VisualizerHandler, Setter

#settings.init()
from .settings import CACHE

# GLOBAL VARIABLES

curdoc().title = "Graph visualizer server"

#---------------------------------------------------------------------------------------------------- 

# --------- Display points -------- #

TOOLTIPS = [
    ("person", "@name"),
    ("home latitude", "@home_lat"),
    ("home longitude", "@home_long"),
]

plot = figure(width=1200, height=900, toolbar_location="above", tooltips=TOOLTIPS, tools=settings.PLOT_TOOLS, output_backend="webgl") 
plot.xgrid.visible = False
plot.ygrid.visible = False
plot.axis.visible = False
plot.title.text = "Graph visualizer"
CACHE.plot.p = plot

edges_glyph = MultiLine(
    xs="xs",
    ys="ys",
    line_color="colors",
    line_width="thickness",
    line_alpha=.5
)
plot.add_glyph(CACHE.plot.edges.source, edges_glyph)

nodes_glyph = Circle(
    x="x",
    y="y",
    fill_color="colors",
    radius="size",
    #size="size",
    fill_alpha=.5
)

plot.add_glyph(CACHE.plot.source, nodes_glyph)

#plot.select_one(HoverTool).tooltips = TOOLTIPS



#graph_plot = from_networkx(nx.karate_club_graph(), nx.circular_layout, scale=2, center=(0,0))
#CACHE.plot.graph = graph_plot
#plot.renderers.append(graph_plot)


""" holoview
renderer = hv.renderer('bokeh').instance(mode='server')
plot_graph = hv.Graph.from_networkx(CACHE.graph, nx.layout.fruchterman_reingold_layout).opts(toolbar="above", width=800, height=800, xaxis=None, yaxis=None)
CACHE.plot.graph = plot_graph
hvplot = renderer.get_plot(plot_graph, curdoc())
plot=hvplot.state
"""

# ---------- Set all callbacks and buttons ---------- # 

CACHE.widgets = AttrDict()

file_input = FileInput(accept=".csv") # https://docs.bokeh.org/en/latest/docs/reference/models/widgets.inputs.html#bokeh.models.widgets.inputs.FileInput
file_input.on_change('value', FileInputHandler.callback)
CACHE.widgets.file_input = file_input

timestep_slider = Slider(title="Timestep ", start=0, end=CACHE.graph_attr.timesteps, value=CACHE.plot.timestep, step=1)
timestep_slider.on_change('value_throttled', VisualizerHandler.timestep_callback)
CACHE.widgets.timestep_slider = timestep_slider

color_picker = ColorPicker(title="Color picker")
color_picker.on_change('color', VisualizerHandler.color_callback)
CACHE.widgets.color_picker = color_picker

thickness_slider = Slider(title="Edge thickness", start=.1, end=20, value=CACHE.plot.edges.thickness, step=.1)
thickness_slider.on_change('value', VisualizerHandler.thickness_callback)
CACHE.widgets.thickness_slider = thickness_slider

node_size_slider = Slider(title="Node size", start=1, end=50, value=CACHE.plot.nodes.size, step=1)
node_size_slider.on_change('value', VisualizerHandler.node_size_callback)
CACHE.widgets.node_size_slider = node_size_slider

layout_algo_dropdown = Dropdown(label="Layout algorithm", menu=list(layouts.AVAILABLE.keys()))
layout_algo_dropdown.on_event('menu_item_click', VisualizerHandler.layout_algo_callback)
CACHE.widgets.layout_algo_dropdown = layout_algo_dropdown

node_size_dropdown = Dropdown(label="Node size based on", menu=Setter.NODE_BASED_ON)
node_size_dropdown.on_event('menu_item_click', VisualizerHandler.node_size_based_callback)
CACHE.widgets.node_size_dropdown = node_size_dropdown

control_pannel = column(file_input, 
                        timestep_slider,
                        row(layout_algo_dropdown, node_size_dropdown),
                        row(node_size_slider, thickness_slider),
                        )
# ---------- #  

layout = row(plot, control_pannel)
curdoc().add_root(layout)