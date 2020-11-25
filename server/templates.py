from . import settings
from .settings import COLUMNS_NAME
from .utils import AttrDict
from .graphs import GraphHelper

import random
import numpy as np


random_size = 24
random_people = 28
random_graph = {
    "timestep": np.random.randint(low=0, high=20, size=random_size),
    "person1" : np.random.randint(low=0, high=random_people, size=random_size),
    "person2" : np.random.randint(low=0, high=random_people, size=random_size),
    "infected1" : np.random.randint(1, size=random_size),
    "infected2" : np.random.randint(1, size=random_size),
    "loc_lat" : 40. + 5.*np.random.random(size=random_size),
    "loc_long" : 40. + 5.*np.random.random(size=random_size),
    "home1_lat" : 40. + 5.*np.random.random(size=random_size),
    "home1_long" : 40. + 5.*np.random.random(size=random_size),
    "home2_lat" : 40. + 5.*np.random.random(size=random_size),
    "home2_long" : 40. + 5.*np.random.random(size=random_size),
}

zero_graph = AttrDict(**{name:[0] for name in COLUMNS_NAME})

__AVAILABLES = (
    #zero_graph,
    random_graph,
)

def get_random():
    graph_dict = random.choice(__AVAILABLES)
    graph = GraphHelper.from_dict_to_graph(graph_dict)
    return graph_dict

