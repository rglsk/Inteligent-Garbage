import random

from lib.frames import Move

rnd = lambda x: random.randint(0, x - 1)

go = {
    Move.north: lambda (x, y): (x, y - 1),
    Move.south: lambda (x, y): (x, y + 1),
    Move.east: lambda (x, y): (x + 1, y),
    Move.west: lambda (x, y): (x - 1, y),
    Move.noop: lambda (x, y): (x, y)
}

def lerp((start_x, start_y), (end_x, end_y)):
    """For two vectors v, w, return function returning
    a vector inbetween them based on scalar. fac = 0
    returns v, fac = 1 return w.
    """
    def ret(fac):
        return (
            (1.0 - fac) * start_x + fac * end_x,
            (1.0 - fac) * start_y + fac * end_y
        )
    return ret

def taxi_dist((x1, y1)):
    def ret((x2, y2)):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx + dy
    return ret

