entities = []
barrels = []
mines = []
my_ships = []
enemy_ships = []


class Cube:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        return "({}, {}, {})".format(self.x, self.y, self.z)


class Hex:
    def __init__(self, row, col):
        self.row = row
        self.col = col

    def __repr__(self):
        return "({}, {})".format(self.row, self.col)


class Entity:
    def __init__(self, _id, _type, x, y, *args):
        self.ID = _id
        self.etype = _type
        self.x = x
        self.y = y
        self.pos_hex = Hex(x, y)
        self.pos_cube = oddr_to_cube(self.pos_hex)

        self.args = args


class Ship:
    def __init__(self, _id, _type, x, y, *args):
        self.ID = _id
        self.etype = _type
        self.x = x
        self.y = y
        self.pos_hex = Hex(x, y)
        self.pos_cube = oddr_to_cube(self.pos_hex)

        self.orientation, self.speed, self.rum, self.owner = args

    def calc_barrel_distances(self):
        self.barrel_distances = []
        for b in barrels:
            self.barrel_distances.append((b.ID, get_distance(self.pos_cube, b.pos_cube)))
        self.barrel_distances.sort(key=lambda x: x[1])

    def calc_enemy_distances(self):
        self.enemy_distances = []
        for s in enemy_ships:
            self.enemy_distances.append((s.ID, get_distance(self.pos_cube, s.pos_cube)))
        self.enemy_distances.sort(key=lambda x: x[1])


# Helpers #

# a & b are Cubes
def get_distance(a, b):
    return (abs(a.x - b.x) + abs(a.y - b.y) + abs(a.z - b.z)) / 2


def cube_to_oddr(cube):
    col = cube.x + (cube.z - (cube.z & 1)) / 2
    row = cube.z
    return Hex(col, row)


def oddr_to_cube(_hex):
    x = _hex.col - (_hex.row - (_hex.row & 1)) / 2
    z = _hex.row
    y = -x - z
    return Cube(x, y, z)


def get_entity_by_id(ID):
    for e in entities:
        if e.ID == ID:
            return e


def get_barrel_by_id(ID):
    for e in barrels:
        if e.ID == ID:
            return e


# End Helpers #

# game loop
while True:
    del entities[:]
    del barrels[:]
    del mines[:]
    del my_ships[:]
    del enemy_ships[:]

    # Inputs #
    my_ship_count = int(input())  # the number of remaining ships
    entity_count = int(input())  # the number of entities (e.g. ships, mines or cannonballs)
    for i in range(entity_count):
        entity_inputs = input().split()
        entity_type = entity_inputs.pop(1)
        entity_id, x, y, arg_1, arg_2, arg_3, arg_4 = [int(i) for i in entity_inputs]

        if entity_type == "SHIP":
            if arg_4 == 1:
                my_ships.append(Ship(entity_id, entity_type, x, y, arg_1, arg_2, arg_3, arg_4))
            if arg_4 == 0:
                enemy_ships.append(Ship(entity_id, entity_type, x, y, arg_1, arg_2, arg_3, arg_4))

        if entity_type == "BARREL":
            barrels.append(Entity(entity_id, entity_type, x, y, arg_1, arg_2, arg_3, arg_4))

        if entity_type == "MINE":
            mines.append(Entity(entity_id, entity_type, x, y, arg_1, arg_2, arg_3, arg_4))

    # End Inputs #

    enemy_ships.sort(key=lambda x: x.rum)

    for i in range(my_ship_count):
        ship = my_ships[i]
        ship.calc_barrel_distances()
        ship.calc_enemy_distances()

        if ship.rum > 50 and ship.speed > 0 and ship.enemy_distances[0][1] < 7:
            print("FIRE", enemy_ships[0].x, enemy_ships[0].y)

        elif len(barrels) > 0:
            closest_barrel = get_barrel_by_id(ship.barrel_distances[0][0])
            print("MOVE", closest_barrel.x, closest_barrel.y)
        else:
            print("FIRE", enemy_ships[0].x, enemy_ships[0].y)
