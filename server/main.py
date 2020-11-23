import tempfile

from bokeh.models import ColumnDataSource, Circle, Plot
from bokeh.models.widgets import FileInput
from bokeh.plotting import curdoc, figure, show
from bokeh.layouts import row, column, layout

from . import settings
from .io import FileInputHandler
from .utils import AttrDict
from .templates import void_graph, zero_graph

settings.init()

# GLOBAL VARIABLES

settings.GRAPH = zero_graph
settings.SOURCE = ColumnDataSource(settings.GRAPH)
DOC = curdoc()

#---------------------------------------------------------------------------------------------------- 

# ---------- Set all callbacks and buttons ---------- # 

file_input = FileInput(accept=".csv") # https://docs.bokeh.org/en/latest/docs/reference/models/widgets.inputs.html#bokeh.models.widgets.inputs.FileInput
file_input.on_change('value', FileInputHandler.callback)

control_pannel = file_input

# --------- Display points -------- #

plot = figure()
plot.circle(x="loc_lat",
            y="loc_long",
            source=settings.SOURCE)


layout = row(control_pannel, plot)
DOC.add_root(layout)