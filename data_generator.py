import random, math
from math import sin

tests = 10000
topology = [1, 10, 1]
file_name = "training_data_xor.txt"

out_file = open(file_name, mode="w")
print("topology:", " ".join(map(str, topology)), file=out_file)


def get_rand_bin():
    return float(random.randint(0, 1))


def xor(a, b):
    a = int(a)
    b = int(b)

    return "1.0" if a != b else "0.0"


def gen_xor_data():
    in1, in2 = get_rand_bin(), get_rand_bin()
    print("in:", in1, in2, file=out_file)
    print("out:", xor(in1, in2), file=out_file)


def gen_add_data(_min, _max, n):
    inputs = [random.randint(_min, _max) for i in range(n)]
    print("in:", *inputs, file=out_file)
    print("out:", sum(inputs), file=out_file)


def gen_power_data(_min, _max, n):
    inputs = random.uniform(_min, _max)
    print("in:", inputs, file=out_file)
    print("out:", inputs ** n, file=out_file)


def gen_trig_data(func):
    inputs = random.uniform(0, 2 * math.pi)
    print("in:", inputs, file=out_file)
    print("out:", func(inputs), file=out_file)


for i in range(tests):
    # gen_add_data(0, 10, 5)
    # gen_xor_data()
    # gen_power_data(1, 4, 2)
    gen_trig_data(sin)
