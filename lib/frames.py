import random
import math

class MapTile:
    grass = 0
    road = 1
    landfill = 2
    obstacle = 3

class TrashType:
    metal = 0
    paper = 1
    plastic = 2

class Trash(object):
    def __init__(self, x, y, trash_type, toxicity, time, way=0, level=0):
        self.x = x
        self.y = y
        self.trash_type = trash_type
        self.toxicity = toxicity
        self.time = time
        self.way = way
        self.level = level

class Move:
    north = 'n'
    south = 's'
    east = 'e'
    west = 'w'
    noop = 'o'

from lib.utils import go

def make_game_state_class(entity_factor, trunk_capacity):
    class GameState:
        """Represents a game state i.e. a truck position (pair of coords),
        gathered trash (dict from TrashType to trash count)
        and trash positions (entities; dict from pair of coords to TrashType).
        """

        def __init__(self, *args):
            if len(args) == 1:
                self.__with_map_ctor(args[0])
            elif len(args) == 0:
                self.__empty_ctor()

        def __with_map_ctor(self, mape):
            grass_positions = []
            map_height = len(mape)
            map_width = len(mape[0])
            for row in xrange(map_height):
                for col in xrange(map_width):
                    if mape[row][col] == MapTile.grass:
                        grass_positions.append((col, row))
            entity_count = min(
                len(grass_positions),
                int(math.pow(map_width * map_height, entity_factor))
            )

            if entity_count == 0:
                raise RuntimeError("can't place anything on the map")

            entity_positions = random.sample(grass_positions, entity_count)
            self.truck_pos = entity_positions.pop()
            self.entities = {}

            while entity_positions:
                trash_x, trash_y = entity_positions.pop()
                trash_type = random.sample(
                    [TrashType.metal, TrashType.paper, TrashType.plastic], 1
                )[0]
                toxicity = random.sample(['mala', 'srednia', 'duza'], 1)[0]
                time = random.sample(['mala', 'srednia', 'duza'], 1)[0]

                self.entities[trash_x, trash_y] = Trash(
                    x=trash_x,
                    y=trash_y,
                    trash_type=trash_type,
                    toxicity=toxicity,
                    time=time,
                )
            self.trunk = {
                TrashType.metal: 0,
                TrashType.paper: 0,
                TrashType.plastic: 0
            }

        def __empty_ctor(self):
            self.truck_pos = (0, 0)
            self.entities = {}
            self.trunk = {
                TrashType.metal: 0,
                TrashType.paper: 0,
                TrashType.plastic: 0
            }

        def move(self, mape, mv):
            """Given a map and a move, returns new state from current state.
            Raises RuntimeError if the move can't be performed.
            """

            map_height = len(mape)
            map_width = len(mape[0])

            ret_state = GameState()

            new_truck_pos = go[mv](self.truck_pos)
            (x, y) = new_truck_pos

            ret_state.truck_pos = new_truck_pos

            for t in self.trunk:
                ret_state.trunk[t] = self.trunk[t]

            for pos in self.entities:
                ret_state.entities[pos] = self.entities[pos]

            if not (0 <= x < map_width and 0 <= y < map_height):
                raise RuntimeError("invalid move. truck is off the map.")

            if mape[y][x] == MapTile.obstacle:
                raise RuntimeError("invalid move. obstacle in the way.")

            if mape[y][x] == MapTile.landfill:
                for trash_type in ret_state.trunk:
                    ret_state.trunk[trash_type] = 0

            if new_truck_pos in ret_state.entities:
                trash_type = ret_state.entities[new_truck_pos].trash_type
                if ret_state.trunk[trash_type] < trunk_capacity:
                    ret_state.entities.pop(new_truck_pos)
                    ret_state.trunk[trash_type] = ret_state.trunk[trash_type] + 1

            return ret_state

        def is_valid_move(self, mape, mv):
            """checks if a move can be performed"""

            map_height = len(mape)
            map_width = len(mape[0])

            (new_x, new_y) = go[mv](self.truck_pos)

            if not (0 <= new_x < map_width and 0 <= new_y < map_height):
                return False

            if mape[new_y][new_x] == MapTile.obstacle:
                return False

            return True

        def successors(self, mape):
            """returns list of moves that can be performed from current state"""

            return [
                m for m in [Move.north, Move.south, Move.east, Move.west]
                if self.is_valid_move(mape, m)
            ]

        def garbage_fits_to_trunk(self):
            return lambda (trash_pos, trash): self.trunk[trash.trash_type] < trunk_capacity

    return GameState

