import pygame
from lib.frames import MapTile, TrashType

MAX_X_RES = 1340
MAX_Y_RES = 740
MAX_ASPECT_RATIO = float(MAX_X_RES) / MAX_Y_RES

MAP_WIDTH = 30
MAP_HEIGHT = 20
MAP_ASPECT_RATIO = float(MAP_WIDTH) / MAP_HEIGHT

TILE_SIZE = 0
if MAX_ASPECT_RATIO < MAP_ASPECT_RATIO:
    TILE_SIZE = float(MAX_X_RES) / MAP_WIDTH
else:
    TILE_SIZE = float(MAX_Y_RES) / MAP_HEIGHT
TILE_SIZE = int(TILE_SIZE)

RES_X = TILE_SIZE * MAP_WIDTH
RES_Y = TILE_SIZE * MAP_HEIGHT
ASPECT_RATIO = float(RES_X) / RES_Y

ENTITY_SCALE = 0.7

ENTITY_SIZE = int(TILE_SIZE * ENTITY_SCALE)

STEP = 0.334 # truck speed in tiles per frame

ENTITY_FACTOR = 0.6

OBSTACLE_FACTOR = 0.66

class Colors:
    black = (10, 10, 10)
    brown = (153, 76, 0)
    green = (0, 180, 0)
    white = (255, 255, 255)
    pale_white = (240, 240, 240)

colors = {
    MapTile.grass : Colors.green,
    MapTile.road  : Colors.brown,
    MapTile.obstacle : Colors.black,
    MapTile.landfill : Colors.white
}

TEXT_COLOR = Colors.pale_white

class Images:
    load_img = lambda src, size: pygame.transform.scale(
        pygame.image.load(src), (size, size)
    )
    bottle = load_img("resources/bottle.png", ENTITY_SIZE)
    can = load_img("resources/can.png", ENTITY_SIZE)
    glass = load_img("resources/glass.png", ENTITY_SIZE)
    paper = load_img("resources/paper.png", ENTITY_SIZE)
    landfill = load_img("resources/recycle.png", ENTITY_SIZE)
    truck = load_img("resources/truck.png", ENTITY_SIZE)

TRUNK_CAPACITY = 5

trash_image = {
    TrashType.metal: Images.can,
    TrashType.paper: Images.paper,
    TrashType.plastic: Images.bottle
}

