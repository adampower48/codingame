import math
import random
import sys

# CONSTS #
GRAVITY = -3.711
WIDTH = 7000
HEIGHT = 3000
MIN_ANGLE = -90
MAX_ANGLE = 90
MIN_POWER = 0
MAX_POWER = 4

# SHIP #
power = 0
angle = 0
fuel = 0
x = 0
y = 0
vx = 0
vy = 0


class Genome:
    def __init__(self, cur_stats):
        self.x, self.y, self.vx, self.vy, self.fuel, self.angle, self.power = cur_stats
        self.powers = []
        self.rotations = []

    def get_stats(self):
        return self.x, self.y, self.vx, self.vy, self.fuel, self.angle, self.power

    def __repr__(self):
        return "{} {}".format(self.powers, self.rotations)


def create_genome(depth, cur_stats):
    g = Genome(cur_stats)

    for i in range(depth):
        g.powers.append(random.randint(MIN_POWER, MAX_POWER))
        g.rotations.append(0)
        # g.rotations.append(random.randint(MIN_ANGLE, MAX_ANGLE))

    return g


def apply_genome(g, step):
    if g.powers[step] > g.power: g.power += 1
    if g.powers[step] < g.power: g.power -= 1
    if g.rotations[step] > g.angle: g.angle += min(15, g.rotations[step] - g.angle)
    if g.rotations[step] < g.angle: g.angle -= min(15, g.angle - g.rotations[step])
    g.fuel -= g.power
    ax = math.cos(math.radians(g.angle)) * g.power
    ay = math.sin(math.radians(g.angle)) * g.power + GRAVITY

    prev_x = g.x
    prev_y = g.y
    g.x += g.vx + ax * 0.5
    g.y += g.vy + ay * 0.5
    g.vx += ax
    g.vy += ay


def validate_genome(g):
    return 0 <= g.power <= 4 and -90 <= g.angle <= 90 and 0 <= g.x < WIDTH and 0 <= g.y <= HEIGHT and g.fuel >= 0


# INIT #
surface_point_count = int(input())
surface_points = [tuple(map(int, input().split())) for i in range(surface_point_count)]
# print(surface_points, file=sys.stderr)

while True:
    inputs = list(map(int, input().split()))

    best_genome = None
    best_score = 0
    for i in range(4):
        depth = 10
        genome = create_genome(depth, inputs)
        print(i, "\t", genome)

        for k in range(depth):
            apply_genome(genome, k)

            if not validate_genome(genome):
                if k > best_score:
                    best_genome = genome
                    best_score = k
                break
            print(k, *genome.get_stats())

    print(best_genome, best_score)
