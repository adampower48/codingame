import cProfile
from sys import float_info
from random import random, randrange, choice
import numpy
from math import sqrt, log
from time import time

R = 130
K = 0
Tn = 0.01
Tw = 0.25
P = 0.7
epsilon = float_info.epsilon


class Node:
    possible_moves = ["UP", "DOWN", "LEFT", "RIGHT"]

    def __init__(self):
        self.parent = None
        self.children = []
        self.w = 0
        self.n = 0
        self.lead_move = None
        self.bandit = 0.5
        # self.move_stats = {key: [0, 0] for key in Node.possible_moves}
        self.move_stats = {
            "UP": [0, 0],
            "DOWN": [0, 0],
            "LEFT": [0, 0],
            "RIGHT": [0, 0],
        }


def bandit_function(parent, node):
    wj = node.w
    nj = node.n + epsilon
    w_s1 = parent.move_stats[node.lead_move][0]
    n_s1 = parent.move_stats[node.lead_move][1] + epsilon
    ns1 = parent.n
    B = sqrt(R / (R + 3 * nj))

    return (1 - B) * wj / nj + B * w_s1 / n_s1 + K * sqrt(log(ns1) / nj)


def create_node(parent=None, lead_move=None, children=None):
    new_node = Node()
    if parent is not None:
        new_node.parent = parent
        parent.children.append(new_node)
    if lead_move is not None:
        new_node.lead_move = lead_move
    else:
        new_node.lead_move = choice(Node.possible_moves)
    if children is not None: new_node.children = children

    return new_node


def print_nodes(node, i=0):
    print("  " * i, node.w, "/", node.n, ":", node.bandit)
    for c in node.children:
        print_nodes(c, i + 1)


def prof_run():
    s0 = create_node()

    for z in range(1000):
        # Selection
        s1 = s0
        for i in range(10):  # while all possible decisions of s1 have been considered do
            Cs1 = s1.children
            if len(Cs1) == 0: break
            for x in Cs1: x.bandit = bandit_function(s1, x)
            s_1 = max(Cs1, key=lambda x: x.bandit)
            if s_1.bandit > s1.bandit:
                s1 = s_1
            else:
                break

        # Expansion
        s2 = create_node(s1)  # create a child node of s1 from a possible decision of s1 not yet considered

        # Pruning
        sppr = s2
        while sppr.n / (s0.n + epsilon) < Tn:  # while nsPPR < Tn do
            if sppr.parent is None or s0.n == 0: break
            sppr = sppr.parent

        PPR = [j for j in sppr.move_stats if
               sppr.move_stats[sppr.lead_move][0] > Tw]  # PPR ← { j | w_sPPR,j / n_sPPR,j > Tw_ }

        # Simulation / Playout

        s3 = s2
        for i in range(1):
            E = random()
            if E <= P and len(PPR) > 0:
                s3 = create_node(s3, lead_move=choice(PPR))  # randomly choose next state in PPR
            else:
                s3 = create_node(s3, lead_move=choice(
                    Node.possible_moves))  # randomly choose next state in the (1 − ξ) last part of the possible moves
        reward = randrange(2)  # Result of terminal state s3

        # Backpropagation
        s4 = s2
        while s4 != s0:
            s4.w += reward
            s4.n += 1

            while s3 is not None:
                s4.move_stats[s3.lead_move][0] += reward
                s4.move_stats[s3.lead_move][1] += 1
                s3 = s3.parent

            s4 = s4.parent

        s0.w += reward
        s0.n += 1

    print_nodes(s0)
    print(s0.w, s0.n)


# cProfile.run("prof_run()", sort="time")
prof_run()
# my_node = Node()
# cProfile.run("for i in range(1000000): create_node()", sort="cumulative")
