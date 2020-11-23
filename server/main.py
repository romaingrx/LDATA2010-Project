import tempfile

from bokeh.models import ColumnDataSource
from bokeh.models.widgets import FileInput
from bokeh.plotting import curdoc, figure


import sys

print(sys.path)


from .io import from_text_to_dict
from .utils import AttrDict
from .templates import void_graph

# this must only be modified from a Bokeh session callback
source = ColumnDataSource(void_graph)

doc = curdoc()

def upload_fit_data(attr, old, new):
    print("fit data upload succeeded")
    #csvpath = base64ToString(file_input.value)
    print(file_input.filename)

    from_text_to_dict(file_input.value)

file_input = FileInput(accept=".csv,.json,.txt") # https://docs.bokeh.org/en/latest/docs/reference/models/widgets.inputs.html#bokeh.models.widgets.inputs.FileInput
file_input.on_change('value', upload_fit_data)

doc.add_root(file_input)