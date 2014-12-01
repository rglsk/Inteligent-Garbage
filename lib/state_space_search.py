from heapq import heappop, heappush

from lib.frames import MapTile
from lib.utils import taxi_dist

def game_state_cmp(gs1, gs2):
    if gs1.truck_pos[0] < gs2.truck_pos[0]:
        return True
    if gs2.truck_pos[0] < gs1.truck_pos[0]:
        return False
    if gs1.truck_pos[1] < gs2.truck_pos[1]:
        return True
    if gs2.truck_pos[1] < gs1.truck_pos[1]:
        return False
    for tt in gs1.trunk:
        if gs1.trunk[tt] < gs2.trunk[tt]:
            return True
        if gs2.trunk[tt] < gs1.trunk[tt]:
            return False
    return gs1.entities < gs2.entities

def game_state_eq(gs1, gs2):
    return not (game_state_cmp(gs1, gs2) or game_state_cmp(gs2, gs1))

class PairCmp:
    def __init__(self, order, elem):
        self.order = order
        self.elem = elem

    def __lt__(self, other):
        if not isinstance(other, PairCmp):
            raise BaseException("cannot compare " + str(type(other)))
        else:
            return self.order < other.order

    def __gt__(self, other):
        return other < self

    def __ne__(self, other):
        return self < other or other < self

    def __eq__(self, other):
        return not self != other

    def __ge__(self, other):
        return not self < other

    def __le__(self, other):
        return not other < self

    def __repr__(self):
        return "PairCmp(" + repr(self.order) + ": " + repr(self.elem) + ")"

    def __hash__(self):
        return hash(self.__repr__())

def make_generic_search(push, pop, is_empty=lambda arry: arry == [], empty=lambda: []):
    def generic_search(successors, final, cutoff=lambda x: False):
        def search(state, to_yield=lambda x: x):
            to_visit = empty()
            push(to_visit, state)
            while not is_empty(to_visit):
                new_state = pop(to_visit)
                if not cutoff(new_state):
                    if final(new_state):
                        yield to_yield(new_state)
                    for successor in successors(new_state):
                        push(to_visit, successor)
        return search
    return generic_search

bfs = make_generic_search(
    lambda arry, elem: heappush(arry, PairCmp(len(arry), elem)),
    lambda arry: heappop(arry).elem)

dfs = make_generic_search(
    lambda arry, elem: arry.append(elem),
    lambda arry: arry.pop())

dfs_limit = lambda n: make_generic_search(
    lambda arry, elem: arry.append(elem) if len(arry) < n else None,
    lambda arry: arry.pop())

ufs = lambda cost: make_generic_search(
    lambda arry, elem: heappush(arry, PairCmp(cost(elem), elem)),
    lambda arry: heappop(arry).elem)

astar = lambda f, g: ufs(lambda state: f(state) + g(state))

# -------------------------------

def make_finder(mape):
    road_count = 0
    grass_count = 0
    for row in mape:
        for tile in row:
            if tile == MapTile.road:
                road_count = road_count + 1
            elif tile == MapTile.grass:
                grass_count = grass_count + 1
    grass_road_mult = 3.0
    road_cost = (road_count + grass_count) / (grass_count * grass_road_mult + road_count)
    grass_cost = (road_count + grass_count - road_cost * road_count) / grass_count

    def find_path(target):
        def successor((game_state, prev_state, path_cost)):
            def succ(mv):
                (x, y) = game_state.truck_pos
                delta_cost = road_cost if mape[y][x] == MapTile.road else grass_cost
                return (game_state.move(mape, mv),
                        (game_state, prev_state, mv),
                        path_cost + delta_cost)
            return succ

        def cutoff((game_state, prev_state, path_cost)):
            state = prev_state
            while state:
                if state[0].truck_pos == game_state.truck_pos:
                #if game_state_eq(state[0], game_state):
                    return True
                state = state[1]
            return False

        def successors(comp_state):
            return map(successor(comp_state), comp_state[0].successors(mape))

        def cost((game_state, prev_state, path_cost)):
            return path_cost

        def heur((game_state, prev_state, path_cost)):
            return taxi_dist(game_state.truck_pos)(target)

        def final((game_state, prev_state, path_cost)):
            return game_state.truck_pos == target

        return astar(cost, heur)(successors, final, cutoff)
    return find_path

def state_space_search(mape, initial_state, landfill_pos):

    find_path = make_finder(mape)

    game_state = initial_state

    while game_state.entities != {} or game_state.truck_pos != landfill_pos:
        garbage = filter(
            game_state.garbage_fits_to_trunk(),
            game_state.entities.items()
        )
        garbage = [pos for (pos, trash) in garbage]

        target = landfill_pos

        if garbage != []:
            closest_pos = min(garbage, key=taxi_dist(game_state.truck_pos))
            target = closest_pos

        for (target_state, prev_state, path_cost) in find_path(target)((game_state, None, 0)):
            path = []
            state = prev_state
            while state:
                path.append(state[2]) #append move
                state = state[1]
            path.reverse()
            for mv in path:
                yield mv
            game_state = target_state
            break # only best solution matters

def simple_astar(mape):
    find_path = make_finder(mape)
    def to_target(target):
        with_target = find_path(target)
        def with_initial_state(game_state):

            for (target_state, prev_state, path_cost) in with_target((game_state, None, 0)):
                path = []
                state = prev_state
                while state:
                    path.append(state[2])
                    state = state[1]
                path.reverse()
                for mv in path:
                    yield mv
                break
        return with_initial_state
    return to_target

