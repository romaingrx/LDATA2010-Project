from bokeh.models import ColumnDataSource, Circle, Plot, Div, ColorPicker, Dropdown, Slider, GraphRenderer, MultiLine
from bokeh.models.widgets import FileInput, Panel
from bokeh.plotting import curdoc, figure, show 
from bokeh.layouts import row, column, layout
from bokeh.palettes import Spectral8
import networkx as nx


from . import settings, layouts
from .io import FileInputHandler
from .utils import AttrDict
from .visualizer import VisualizerHandler

settings.init()
from .settings import CACHE

# GLOBAL VARIABLES

DOC = curdoc()
DOC.title = "Graph visualizer server"

#---------------------------------------------------------------------------------------------------- 

# --------- Display points -------- #

TOOLTIPS = [
    ("person", "@name")
]

plot = figure(width=800, height=800, toolbar_location="above", tooltips=None, tools=settings.PLOT_TOOLS) 
CACHE.plot.p = plot

edges_glyph = MultiLine(
    xs="xs",
    ys="ys",
)
plot.add_glyph(CACHE.plot.edges.source, edges_glyph)

nodes_glyph = Circle(
    x="x",
    y="y",
    size=20
)

plot.add_glyph(CACHE.plot.source, nodes_glyph)





#graph_plot = from_networkx(nx.karate_club_graph(), nx.circular_layout, scale=2, center=(0,0))
#CACHE.plot.graph = graph_plot
#plot.renderers.append(graph_plot)


""" holoview
renderer = hv.renderer('bokeh').instance(mode='server')
plot_graph = hv.Graph.from_networkx(CACHE.graph, nx.layout.fruchterman_reingold_layout).opts(toolbar="above", width=800, height=800, xaxis=None, yaxis=None)
CACHE.plot.graph = plot_graph
hvplot = renderer.get_plot(plot_graph, DOC)
plot=hvplot.state
"""

# ---------- Set all callbacks and buttons ---------- # 

CACHE.widgets = AttrDict()

file_input = FileInput(accept=".csv") # https://docs.bokeh.org/en/latest/docs/reference/models/widgets.inputs.html#bokeh.models.widgets.inputs.FileInput
file_input.on_change('value', FileInputHandler.callback)
CACHE.widgets.file_input = file_input

timestep_slider = Slider(title="Timestep ", start=0, end=CACHE.graph_attr.timesteps, value=CACHE.graph_attr.timesteps, step=1)
timestep_slider.on_change('value', VisualizerHandler.timestep_callback)
CACHE.widgets.timestep_slider = timestep_slider

color_picker = ColorPicker(title="Color picker")
color_picker.on_change('color', VisualizerHandler.color_callback)
CACHE.widgets.color_picker = color_picker

thickness_slider = Slider(title="Thickness", start=1, end=50, value=20, step=1)
thickness_slider.on_change('value', VisualizerHandler.thickness_callback)
CACHE.widgets.thickness_slider = thickness_slider

layout_algo_dropdown = Dropdown(label="Layout algorithm", menu=list(layouts.AVAILABLE.keys()))
layout_algo_dropdown.on_event('menu_item_click', VisualizerHandler.layout_algo_callback)
CACHE.widgets.file_input = file_input

control_pannel = column(file_input, 
                        timestep_slider,
                        row(color_picker, thickness_slider),
                        layout_algo_dropdown
                        )
# ---------- #  


layout = row(plot, control_pannel)
DOC.add_root(layout)