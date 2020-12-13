from bokeh.models import ColumnDataSource, Circle, Plot, Div, ColorPicker, Dropdown, Slider, GraphRenderer, MultiLine, HoverTool, Ellipse, Div, Button, Rect, Text
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

plot = figure(toolbar_location="above", tooltips=TOOLTIPS, tools=settings.PLOT_TOOLS, output_backend="webgl",
              sizing_mode="stretch_both")
              #height_policy="fit", width_policy="max", aspect_ratio="auto")
plot.xgrid.visible = False
plot.ygrid.visible = False
#plot.axis.visible = False
plot.title.text = "Graph visualizer"

edges_glyph = MultiLine(
    xs="xs",
    ys="ys",
    line_color="colors",
    line_width="thickness",
    line_alpha=.5
)
plot.add_glyph(CACHE.plot.network.edges.source, edges_glyph)

nodes_glyph = Circle(
    x="x",
    y="y",
    fill_color="colors",
    radius="size",
    #size="size",
    fill_alpha=.75
)

plot.add_glyph(CACHE.plot.nodes.source, nodes_glyph)

CACHE.plot.p = plot

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

file_input = FileInput(accept=".csv") # https://docs.bokeh.org/en/latest/docs/reference/models/widgets.inputs.html#bokeh.models.widgets.inputs.FileInput
file_input.on_change('value', FileInputHandler.callback)
CACHE.widgets.file_input = file_input


renderer_button = Button(label="Statistics visualisation")
renderer_button.on_click(VisualizerHandler.renderer_visualisation_callback)
CACHE.widgets.renderer_button = renderer_button

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

thickness_slider = Slider(title="Edge thickness", start=.05, end=5, value=CACHE.plot.network.edges.thickness, step=.05, **STATIC.widget.slider)
thickness_slider.on_change('value_throttled', VisualizerHandler.thickness_callback)
CACHE.widgets.thickness_slider = thickness_slider

palette_dropdown = Dropdown(label="Palette", menu=from_dict_to_menu(Setter.ALL_PALETTES))
palette_dropdown.on_event('menu_item_click', VisualizerHandler.palette_callback)
CACHE.widgets.palette_dropdown = palette_dropdown

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


# -------------------------------------- Statistics visualisation ----------------------------------------------------

default_stat_tools = "save,hover"

adjacency_tooltips = [
    ("Weight", "@size")
]

p_adjacency = figure(title="Adjacency matrix", toolbar_location="above", tooltips=adjacency_tooltips, tools=default_stat_tools, output_backend="webgl")
#p_adjacency.xgrid.visible = False
#p_adjacency.ygrid.visible = False
p_adjacency.axis.visible = False
matrix_glyph = Circle(
    x="x",
    y="y",
    fill_color="colors",
    radius="size",
    fill_alpha=.75
)
p_adjacency.add_glyph(CACHE.plot.statistics.matrix.source, matrix_glyph)
CACHE.plot.statistics.matrix.p = p_adjacency


degree_distribution_tooltips = [
    ("Degree", "@degree"),
    ("Counts", "@counts"),
]

p_degree_distribution = figure(title="Degree distribution", tooltips=degree_distribution_tooltips, toolbar_location="above", tools=default_stat_tools, output_backend="webgl")
p_degree_distribution.xgrid.visible = False
p_degree_distribution.ygrid.visible = False
p_degree_distribution.axis.visible = False
degree_distribution_glyph = Rect(
    x="x",
    y="y",
    width="width",
    height="counts",
    fill_color="colors",
)
p_degree_distribution.add_glyph(CACHE.plot.statistics.degree_distribution.source, degree_distribution_glyph)
#text_degree_distribution_glyph = Text(x="x", y="y", text="degree", text_color="#000000")
#p_degree_distribution.add_glyph(CACHE.plot.statistics.degree_distribution.source, text_degree_distribution_glyph)
CACHE.plot.statistics.degree_distribution.p = p_degree_distribution


# Layout disposition

#div = Div(text="<hr class=\"solid\">", css_classes=["hr.solid {border-top: 3px solid #bbb;}"])

top_pannel = column(
    row(file_input, renderer_button),
    timestep_slider,
    sizing_mode="scale_width"
)

layout_pannel = column(
    layout_title,
    row(layout_algo_dropdown, palette_dropdown)
)
CACHE.plot.network.widgets["layout_pannel"] = layout_pannel

edges_pannel = column(
   edges_title,
   thickness_slider,
)
CACHE.plot.network.widgets["edges_pannel"] = edges_pannel

nodes_pannel = column(
    nodes_title,
    row(node_size_dropdown, node_size_slider),
    row(node_color_dropdown)
)
CACHE.plot.network.widgets["nodes_pannel"] = nodes_pannel

control_graph = column(
    layout_pannel,
    edges_pannel,
    nodes_pannel
)

control_pannel = column(
    top_pannel,
    control_graph,
    #sizing_mode="scale_both"
    #height_policy="fit",
)

space_layout = row(control_pannel, plot)

# ------------------------------------------------------ #


graphs = row(p_adjacency, p_degree_distribution)

statistics_layout = row(control_pannel, graphs)


# ---------- #

Setter.resize()
CACHE.plot.all_layouts = [space_layout, statistics_layout]
curdoc().add_root(space_layout)
