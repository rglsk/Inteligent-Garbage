#((x<5, 5<x<10, x>10 ),   (x<40, 40<x<70, x>70), (x<20,   20<x<30, x>30))
#((krotka/srednia/dluga), (mala, srednia, duza), (krotki, sredni, dlugi))
#           way                 toxicity                time

trainging_list = [
    ['srednia', 'duza', 'srednia', True],
    ['duza', 'mala', 'duza', False],
    ['duza', 'srednia', 'duza', False],
    ['mala', 'srednia', 'mala', True],
    ['mala', 'duza', 'mala', True],
    ['duza', 'mala', 'mala', False],
    ['duza', 'mala', 'mala', False],
    ['duza', 'duza', 'mala', True],
    ['mala', 'srednia', 'duza', True],
    ['mala', 'srednia', 'srednia', False],
    ['srednia', 'srednia', 'srednia', False],
    ['srednia', 'duza', 'mala', True],
    ['srednia', 'mala', 'mala', False],
    ['srednia', 'duza', 'duza', True],
    ['srednia', 'duza', 'srednia', True],


]
