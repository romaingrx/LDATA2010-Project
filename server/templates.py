from .settings import COLUMNS_NAME
from .utils import AttrDict

void_graph = AttrDict(**{name:[] for name in COLUMNS_NAME})

zero_graph = AttrDict(**{name:[0.] for name in COLUMNS_NAME})