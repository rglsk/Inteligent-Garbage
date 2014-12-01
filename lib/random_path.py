import random

def random_path(mape, game_state, landfill_pos):
    gs = game_state
    while True:
        mv = random.sample(gs.successors(mape), 1)[0]
        gs = gs.move(mape, mv)
        yield mv

