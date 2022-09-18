from pygame import Vector2

SCREEN_HEIGHT = 720
SCREEN_WIDTH = 1280
TILE_SIZE = 64

OVERLAY_POSITIONS = {
    'tool': (40, SCREEN_HEIGHT - 15),
    'seed': (70, SCREEN_HEIGHT - 5),
}

PLAYER_TOOL_OFFSET = {
    'left': Vector2(-50, 40),
    'right': Vector2(50, 40),
    'up': Vector2(0, -10),
    'down': Vector2(0, 50),
}

LAYERS = {
    'water': 0,
    'ground': 1,
    'soil': 2,
    'soil water': 3,
    'rain floor': 4,
    'house bottom': 5,
    'ground plant': 6,
    'main': 7,
    'house top': 8,
    'fruit': 9,
    'rain drops': 10,
}

TMX_LAYERS = {
    'house bottom': ['HouseFloor', 'HouseFurnitureBottom'],
    'main': ['HouseWalls', 'HouseFurnitureTop'],
}

APPLE_POS = {
    'Small': [(18, 17), (30, 37), (12, 50), (30, 45), (20, 30), (30, 10)],
    'Large': [(30, 24), (60, 65), (50, 50), (26, 40), (45, 50), (42, 70)],
}

SOIL_MAP = {(0, 1): 'b', (-1, 0): 'l', (1, 0): 'r', (0, -1): 't'}

GROW_SPEED = {'corn': 1, 'tomato': 0.7}

PLANT_Y_OFFSET = {'corn': -16, 'tomato': -8}
