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

def init():
    global GRAPH, SOURCE, DOC
    GRAPH = {}
    SOURCE = None
    DOC = None