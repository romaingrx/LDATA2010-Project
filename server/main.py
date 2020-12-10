from bokeh.models import ColumnDataSource, Circle, Plot, Div, ColorPicker, Dropdown, Slider, GraphRenderer, MultiLine, HoverTool, Ellipse, Div
from bokeh.models.widgets import FileInput
from bokeh.plotting import curdoc, figure
from bokeh.layouts import row, column

#import holoviews as hv
#hv.extension('bokeh')


from . import settings, layouts
from .io import FileInputHandler
from .utils import AttrDict, from_dict_to_menu
from .visualizer import VisualizerHandler, Setter
from .settings import CACHE, STATIC

# GLOBAL VARIABLES

curdoc().title = "Graph visualizer server"

#---------------------------------------------------------------------------------------------------- 

# --------- Display points -------- #

TOOLTIPS = [
    ("person", "@name"),
    ("home latitude", "@home_lat"),
    ("home longitude", "@home_long"),
    ("degree", "@degree")
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
    fill_alpha=.75
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

timestep_slider = Slider(title="Timestep", start=1, end=CACHE.graph_attr.timesteps, value=CACHE.plot.timestep, step=1, **STATIC.widget.slider)
timestep_slider.on_change('value_throttled', VisualizerHandler.timestep_callback)
CACHE.widgets.timestep_slider = timestep_slider

# ------------------ Layouts widgets ------------------- #

layout_title = Div(text="<h1>Layout settings</h1>")

layout_algo_dropdown = Dropdown(label="Layout algorithm", menu=from_dict_to_menu(layouts.AVAILABLE))
layout_algo_dropdown.on_event('menu_item_click', VisualizerHandler.layout_algo_callback)
CACHE.widgets.layout_algo_dropdown = layout_algo_dropdown

# ------------------ Edges widgets ------------------- #

edges_title = Div(text="<h1>Edges settings</h1>")

thickness_slider = Slider(title="Edge thickness", start=.05, end=5, value=CACHE.plot.edges.thickness, step=.05, **STATIC.widget.slider)
thickness_slider.on_change('value_throttled', VisualizerHandler.thickness_callback)
CACHE.widgets.thickness_slider = thickness_slider

# ------------------ Nodes widgets ------------------- #

nodes_title = Div(text="<h1>Nodes settings</h1>")

node_size_slider = Slider(title="Node size", start=1, end=50, value=CACHE.plot.nodes.size, step=1, **STATIC.widget.slider)
node_size_slider.on_change('value_throttled', VisualizerHandler.node_size_callback)
CACHE.widgets.node_size_slider = node_size_slider

node_size_dropdown = Dropdown(label="Node size based on", menu=Setter.NODE_BASED_ON)
node_size_dropdown.on_event('menu_item_click', VisualizerHandler.node_size_based_callback)
CACHE.widgets.node_size_dropdown = node_size_dropdown


node_color_dropdown = Dropdown(label="Node color based on", menu=Setter.NODE_COLORS)
node_color_dropdown.on_event('menu_item_click', VisualizerHandler.node_color_callback)
CACHE.widgets.node_color_dropdown = node_color_dropdown

# ------------------ Other widgets ------------------- #

color_picker = ColorPicker(title="Color picker")
color_picker.on_change('color', VisualizerHandler.color_callback)
CACHE.widgets.color_picker = color_picker


# Layout disposition

#div = Div(text="<hr class=\"solid\">", css_classes=["hr.solid {border-top: 3px solid #bbb;}"])

top_pannel = column(
    file_input,
    timestep_slider,
    sizing_mode="scale_width"
)

layout_pannel = column(
    layout_title,
    layout_algo_dropdown,
)

edges_pannel = column(
   edges_title,
   thickness_slider,
)

nodes_pannel = column(
    nodes_title,
    row(node_size_dropdown, node_size_slider),
    row(node_color_dropdown)
)


control_pannel = column(
    top_pannel,
    layout_pannel,
    edges_pannel,
    nodes_pannel
)

layout = row(control_pannel, plot)

# ---------- #

curdoc().add_root(layout)