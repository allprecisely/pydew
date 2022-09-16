SCREEN_HEIGHT = 720
SCREEN_WIDTH = 1280
TILE_SIZE = 64

OVERLAY_POSITIONS = {
    'tool': (40, SCREEN_HEIGHT - 15),
    'seed': (70, SCREEN_HEIGHT - 5),
}

LAYERS = {
    'water': 0,
    'ground': 1,
    'house bottom': 5,
    'main': 7,
    'house top': 8,
}

TMX_LAYERS = {
    'house bottom': ['HouseFloor', 'HouseFurnitureBottom'],
    'main': ['Fence'],
    'house top': ['HouseWalls', 'HouseFurnitureTop'],
}