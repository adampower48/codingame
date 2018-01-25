import sys
from math import cos, sin, tan, acos, atan, sqrt, degrees, radians
from copy import deepcopy


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def distance2(self, p):
        return (self.x - p.x) ** 2 + (self.y - p.y) ** 2

    def distance(self, p):
        return sqrt(self.distance2(p))


class Pod(Point):
    def __init__(self, x, y, angle, vx, vy, shield=False, timeout=200):
        Point.__init__(self, x, y)
        self.angle = self.get_angle(Point(x - 1000, y))
        # self.angle = angle
        self.vx = vx
        self.vy = vy
        self.shield = shield
        self.timeout = timeout

    def get_angle(self, p):
        d = self.distance(p)
        dx = (p.x - self.x) / d
        dy = (p.y - self.y) / d

        a = degrees(acos(dx))

        return 360 - a if dy < 0 else a

    def diff_angle(self, p):
        a = self.get_angle(p)

        right = a - self.angle if self.angle <= a else 360 - self.angle + a
        left = self.angle - a if self.angle >= a else 360 + self.angle - a

        return right if right < left else - left

    def rotate(self, p):
        a = self.diff_angle(p)

        # Clamp to +/- 18
        if a > 18:
            a = 18
        elif a < -18:
            a = -18

        self.angle += a

        # Wraparound
        if self.angle >= 360:
            self.angle -= 360
        elif self.angle < 0:
            self.angle += 360

    def boost(self, thrust):
        if self.shield: return

        ra = radians(self.angle)

        self.vx += cos(ra) * thrust
        self.vy += sin(ra) * thrust

    def move(self, t=1):
        # t:time  used for collision detection
        self.x += self.vx * t
        self.y += self.vy * t

    def end(self):
        self.x = int(self.x)
        self.y = int(self.y)
        self.vx = int(self.vx)
        self.vy = int(self.vy)

        self.timeout -= 1

    def play(self, p, thrust):
        self.rotate(p)
        self.boost(thrust)
        self.move()
        self.end()

    def get_rel_point(self, a):
        x = cos(radians(self.angle + a)) * 1000 + self.x
        y = sin(radians(self.angle + a)) * 1000 + self.y
        return Point(int(x), int(y))


def get_inputs():
    me = [int(x) for x in input().split()]
    enemy = [int(x) for x in input().split()]
    return me + enemy


def get_best_point(pod, checkpoint):
    test_pod = deepcopy(pod)

    best_angle = 0
    best_thrust = 0
    best_score = 10000000000000000000000000000

    for angle in move_angles:
        for thrust in move_thrusts:
            point = test_pod.get_rel_point(angle)
            test_pod.play(point, thrust)

            score = test_pod.distance(checkpoint) + abs(
                test_pod.diff_angle(checkpoint)) * 1  # - sqrt(abs(test_pod.vx)**2 + abs(test_pod.vy)**2)*3
            print("Angle:", angle, "Thrust:", thrust, "Score", score, file=sys.stderr)
            if score < best_score:
                best_score = score
                best_angle = angle
                best_thrust = thrust

            test_pod = deepcopy(pod)

    return test_pod.get_rel_point(best_angle), best_thrust


move_angles = [-18, -9, 0, 9, 18]
move_thrusts = [0, 100]
friction = 0.85

prev_pod = Pod(0, 0, 0, 0, 0)

turn = 0
while True:
    turn += 1
    x, y, cp_x, cp_y, cp_dist, cp_angle, opp_x, opp_y = get_inputs()
    vel_x = x - prev_pod.x
    vel_y = y - prev_pod.y
    cur_pod = Pod(x, y, cp_angle, vel_x, vel_y)
    checkpoint = Point(cp_x, cp_y)
    print(cur_pod.x, y, cp_x, cp_y, cp_dist, cur_pod.angle, opp_x, opp_y, vel_x, vel_y, file=sys.stderr)
    target_point, target_thrust = get_best_point(cur_pod, checkpoint)
    if turn == 1:
        print(checkpoint.x, checkpoint.y, 0)
        continue
    print(target_point.x, target_point.y, target_thrust)
    prev_pod = cur_pod
