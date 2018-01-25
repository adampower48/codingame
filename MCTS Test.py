import math, cProfile
from time import time
from random import choice, randint

# s0 = grandaddy node
# s1 = node
# wj = wins for node j
# nj = num of playouts for node j
# ns1 = num of playouts for node s1
#     = sum of all nj
# K = exploration parameter
# Cs1 = set of child nodes of s1
# j = child node in set Cs1

# selection -> expansion -> simulation -> backpropagation
K = 0.5  # exploration parameter
R = 0.5  # Some parameter


class Node:
    # children = [nodes]
    # parent = node
    # n = playouts
    # n = sum(c.n for c in children)
    # w = wins
    # w = sum(c.w for c in children)

    def __init__(self):
        self.parent = None
        self.children = []
        self.n = 0
        self.w = 0
        self.bandit = 0.5
        self.rave_stats = {}
        for m in range(5): self.rave_stats[m] = [0, 0]  # Initialise moves
        self.move = None
        self.parent_moves = []

    def __str__(self):
        return str(self.children)

    def __repr__(self):
        return str(self.children)


def formula(parent, child):
    # B -> 0 as n -> infinity
    B = math.sqrt(R / (R + 3 * child.n))
    w_ = child.rave_stats[child.move][0]  # wins for move leading parent -> child
    n_ = child.rave_stats[child.move][1]  # playouts for move leading parent -> child
    try:
        return (1 - B) * child.w / child.n + (B * w_ / n_) + K * math.sqrt(math.log(parent.n) / child.n)
    except OverflowError:
        print("B:", B, "w_:", w_, "n_:", n_, "child.w:", child.w, "child.n:", child.n, "parent.n:", parent.n)


def select_node(parent):
    if len(parent.children) > 0:
        child = max(parent.children, key=lambda c: c.bandit)
        if child.bandit > parent.bandit: return select_node(child)

    return parent


def expand_node(node):
    child = Node()
    child.parent = node
    child.move = randint(0, 4)
    child.parent_moves = node.parent_moves + [child.move]

    # RAVE
    for k in range(5):
        child.rave_stats[k][0] = 0
        child.rave_stats[k][1] = 0

    node.children.append(child)

    return child


def simulate(node):
    result = choice([True, False])
    return result


def back_prop(node, result, rave_results=None):
    node.n += 1
    if result == True:
        node.w += 1

    if rave_results is None:
        node.rave_stats[node.move][1] += 1
        if result == True: node.rave_stats[node.move][0] += 1
        rave_results = {}
        for m in node.parent_moves:
            if m not in rave_results: rave_results[m] = [0, 0]
            node.rave_stats[m][1] += 1
            rave_results[m][1] += 1
            if result == True:
                node.rave_stats[m][0] += 1
                rave_results[m][0] += 1

    else:
        # Update parent RAVE stats
        for k, v in rave_results.items():
            node.rave_stats[k][0] += v[0]
            node.rave_stats[k][1] += v[1]

    if node.parent != None:
        back_prop(node.parent, result, rave_results)
        node.bandit = formula(node.parent, node)


def print_nodes(node, i=0):
    print(*["  "] * i, node.bandit)
    for c in node.children:
        print_nodes(c, i + 1)


def min_run():
    _base_node = Node()

    for i in range(50000):
        _selection = select_node(_base_node)
        _expansion = expand_node(_selection)
        _result = simulate(_expansion)
        back_prop(_expansion, _result)


def debug_run():
    base_node = Node()

    runs = 0
    #
    start = time()
    # for i in range(1000):
    while time() < start + 0.04:
        runs += 1
        selection = select_node(base_node)
        expansion = expand_node(selection)
        result = simulate(expansion)
        back_prop(expansion, result)

    # print(base_node.w, "/", base_node.n)
    print_nodes(base_node)
    print(runs, "runs")
    print(base_node.rave_stats)


cProfile.run("min_run()", sort="cumulative")

# debug_run()
