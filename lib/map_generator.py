import math

from lib.frames import MapTile
from lib.utils import rnd

def generate_road(map_width, map_height, turns):
    """Returns generator of (x, y) pairs."""
    x = rnd(map_width)
    y = rnd(map_height)
    pos = (x, y)

    direction = 0 # horizontal
    move_pos = [
        [lambda (x, y): (x + 1, y), lambda (x, y): (x - 1, y)],
        [lambda (x, y): (x, y + 1), lambda (x, y): (x, y - 1)]
    ]
    for turn in xrange(turns):
        target = (pos[0], rnd(map_height)) if direction else (rnd(map_width), pos[1])
        positive_dir = pos[1] <= target[1] if direction else pos[0] <= target[0]

        while pos != target:
            pos = move_pos[direction][not positive_dir](pos)
            yield pos

        direction = not direction

def generate_map(width, height, obstacle_factor):
    mape = [[MapTile.grass for y in xrange(width)] for x in xrange(height)]

    for (road_x, road_y) in generate_road(
            width,
            height,
            int(math.sqrt(width * height))
        ):
        mape[road_y][road_x] = MapTile.road

    for obstacle_nr in xrange(int(math.pow(width * height, obstacle_factor))):
        mape[rnd(height)][rnd(width)] = MapTile.obstacle

    landfill_pos = (rnd(width), rnd(height))
    mape[landfill_pos[1]][landfill_pos[0]] = MapTile.landfill

    return (mape, landfill_pos)

