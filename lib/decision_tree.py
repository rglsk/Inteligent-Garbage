import math
from settings import *
from training import trainging_list
from tree import Tree
from state_space_search import simple_astar
from lib.frames import Move


WAY_LIMIT = 5
TOXICITY_LIMIT = 70
TIME_LIMIT = 20

count_entropy = lambda p: 0 if p == 0 or p == 1 else (
    -p * math.log(p, 2) - (1 - p) * math.log(1 - p, 2)
)
count_attr_entropy = lambda l, p: 0 if p == 0 or p == 1 else (
    l * (p*math.log(p, 2) + (1-p) * math.log((1-p), 2))
)


class DecisionTree(object):
    ATTRIBUTE_VALUES = ['duza', 'mala', 'srednia']

    def __init__(self):
        self.decision_tree = Tree()

    def create_identifier(self, *args):
        return ':'.join(args)

    def count_all_attr_entropy(self, maly, sredni, duzy):
        maly_count = count_attr_entropy(*maly)
        srednia_count = count_attr_entropy(*sredni)
        duzy_count = count_attr_entropy(*duzy)
        return math.fabs(sum([maly_count, srednia_count, duzy_count]))

    def entropy_counter(self, atrr_names, training_data=None):
        train_zipped = zip(*training_data)
        result_bools = train_zipped.pop(len(train_zipped)-1)
        train_length = len(train_zipped[0])
        mala_true_count = 0
        sred_true_count = 0
        duza_true_count = 0
        mala_false_count = 0
        sred_false_count = 0
        duza_false_count = 0

        slownik = {}
        for nr, x in enumerate(train_zipped):
            slownik[atrr_names.get(nr)] = zip(x, result_bools)

        results = {}
        for nr, value in enumerate(slownik.values()):
            name = atrr_names.get(nr)
            mala_true_count = value.count(('mala', True))
            sred_true_count = value.count(('srednia', True))
            duza_true_count = value.count(('duza', True))
            mala_false_count = value.count(('mala', False))
            sred_false_count = value.count(('srednia', False))
            duza_false_count = value.count(('duza', False))

            mala_count = float(mala_true_count+mala_false_count)
            sred_count = float(sred_true_count+sred_false_count)
            duza_count = float(duza_true_count+duza_false_count)

            mala_propability = (
                0 if not mala_count else mala_true_count/mala_count
            )
            sred_propability = (
                0 if not sred_count else sred_true_count/sred_count
            )
            duza_propability = (
                0 if not duza_count else duza_true_count/duza_count
            )

            entropy = {}

            entropy['mala'] = count_entropy(mala_propability)
            entropy['srednia'] = count_entropy(sred_propability)
            entropy['duza'] = count_entropy(duza_propability)

            attr_entropy = self.count_all_attr_entropy(
                (mala_count/train_length, mala_propability),
                (sred_count/train_length, sred_propability),
                (duza_count/train_length, duza_propability)
            )

            results[name] = {
                entropy['mala']: 'mala',
                entropy['srednia']: 'srednia',
                entropy['duza']: 'duza',
            }
        return results, attr_entropy

    def get_lower_entropy(self, counted_attribs, attr_names=None):
        if not attr_names:
            return None
        counted_attribs, comp_entropy = counted_attribs
        min_value = 1, '_', '_'
        for key in counted_attribs.keys():
            value_dict = counted_attribs[key]
            if isinstance(value_dict, dict):
                new_value = min(value_dict.keys())
                if new_value < min_value[0]:
                    min_value = (
                        new_value,
                        key,
                        counted_attribs[key].get(new_value),

                    )
        return min_value, comp_entropy

    def generate_tree(
        self, parent=None, atrr_names=None, training_data=None
    ):
        if not atrr_names:
            return self.decision_tree
        counted_attribs = self.entropy_counter(
            atrr_names=atrr_names, training_data=training_data
        )
        lower_entropy, comp_entropy = self.get_lower_entropy(
            counted_attribs,
            attr_names=atrr_names
        )

        if not lower_entropy:
            return self.decision_tree

        ATTRIBUTE_NAMES = {atrr_names[value]: value for value in atrr_names}
        entropy, attribute_name, attribute_value = lower_entropy
        attribute_line = ATTRIBUTE_NAMES.pop(attribute_name)

        if not self.decision_tree.nodes:
            root = self.create_identifier(attribute_name, attribute_name)
            self.decision_tree.create_node(
                name=attribute_name,
                identifier=root
            )
            for attr_value in self.ATTRIBUTE_VALUES:
                name = self.create_identifier(attribute_name, attr_value)
                self.decision_tree.create_node(
                    name=name,
                    identifier=name,
                    parent=root
                )
                if attr_value != attribute_value:
                    victory = self.create_identifier(
                        attribute_name, attr_value, 'True'
                    )
                    self.decision_tree.create_node(
                        name=victory,
                        identifier=victory,
                        parent=name
                    )
            parent = self.create_identifier(attribute_name, attribute_value)

        elif parent:
            if entropy < comp_entropy:
                for attr_value in self.ATTRIBUTE_VALUES:
                    name = self.create_identifier(attribute_name, attr_value)
                    self.decision_tree.create_node(
                        name=name,
                        identifier=name,
                        parent=parent
                    )
                    if attr_value != attribute_value:
                        victory = self.create_identifier(
                            attribute_name, attr_value, 'True'
                        )
                        self.decision_tree.create_node(
                            name=victory,
                            identifier=victory,
                            parent=name
                        )
            else:
                atrr_names.pop(attribute_name)
                self.generate_tree(
                    self.decision_tree,
                    parent=parent,
                    atrr_names=atrr_names,
                    training_data=training_data
                )

                parent = self.create_identifier(attribute_name, attribute_value)

        atrr_names.pop(attribute_line)
        new_attr_names = {}

        for nr, value in enumerate(atrr_names.values()):
            new_attr_names[nr] = value

        new_training_data = [
            filter(
                lambda i: i != 'nie', [
                    y if nr != attribute_line else 'nie'
                    for nr, y in enumerate(x)
                ]
            ) for x in training_data
        ]

        if len(new_training_data) > 1:
            self.generate_tree(
                parent=parent,
                atrr_names=new_attr_names,
                training_data=new_training_data
            )

        return self.decision_tree


def give_way(way_score):
    if 5 >= way_score:
        return 'mala'
    elif 5 < way_score <= 10:
        return 'srednia'
    else:
        return 'duza'


def make_decizion_tree(truck_x, truck_y, trash_dict):
    atrr_names = {2: 'time', 1: 'toxicity', 0: 'way'}
    decision_tree = DecisionTree()
    decision_tree = decision_tree.generate_tree(
        atrr_names=atrr_names,
        training_data=trainging_list[:]
    )
    print '----------------------------'
    decision_tree.show_from_root()
    print '----------------------------'
    root = decision_tree.nodes[0].identifier
    for trash in trash_dict.values():
        way_score = math.fabs(truck_x - trash.x) + math.fabs(truck_y - trash.y)
        trash.way = give_way(way_score)
        decision_tree.predict(position=root, trash=trash)

    decisions = [(trash_dict[key].level, key) for key in trash_dict.keys()]

    for decision in decisions:
        chosen_one = 'Choosed: toxi: {} | time: {} | way: {}'.format(
            trash_dict.get(decision[1]).toxicity,
            trash_dict.get(decision[1]).time,
            trash_dict.get(decision[1]).way
        )
        if decision[0] == 0:
            #Fail ROOT oO
            return None
        elif decision[0] == 1:
            print chosen_one
            return decision[1]
        elif decision[0] == 2:
            print chosen_one
            return decision[1]
        elif decision[0] == 3:
            print chosen_one
            return decision[1]


def go_to_landfill(landfill_pos):
    return landfill_pos


def move_ass_to_trash(truck_x, truck_y, trash_x, trash_y):
    if truck_x > trash_x:
        return Move.west
    if truck_x < trash_x:
        return Move.east
    if truck_y < trash_y:
        return Move.south
    if truck_y > trash_y:
        return Move.north
    else:
        return Move.noop

def decision_tree_search(mape, game_state, landfill_pos):
    taken = False
    pathfinder = simple_astar(mape)
    while True:
        truck_x, truck_y = game_state.truck_pos
        trash_dict = game_state.entities
        if not taken:
            if TRUNK_CAPACITY in game_state.trunk.values():
                trash_pos = go_to_landfill(landfill_pos)
            else:
                trash_list = make_decizion_tree(truck_x, truck_y, trash_dict)
                if trash_list:
                    trash_pos = trash_list
                else:
                    trash_pos = go_to_landfill(landfill_pos)

            trash_x, trash_y = trash_pos
            taken = True
        if truck_x == trash_x and truck_y == trash_y:
            taken = False

        #mv = move_ass_to_trash(truck_x, truck_y, trash_x, trash_y)
        for mv in pathfinder(trash_pos)(game_state):
            yield mv
            game_state = game_state.move(mape, mv)

