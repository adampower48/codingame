import sys
import math
import numpy as np
import random

# Bring data on patient samples from the diagnosis machine to the laboratory with enough molecules to produce medicine!

projects = []
players = []
recipes = []
idle_recipes = []
available = []
me = None  # type: Player
enemy = None  # type: Player
ingredients = "ABCDE"

max_costs = {
    1: 5,
    2: 8,
    3: 14
}


class Recipe:
    global me, move_matrix, starts, ends, projects, enemy

    def __init__(self, ID, owner, health, costs, rank, expertise_gain):
        # Owner: Nobody -1, Me 0, Bot 1
        self.ID = ID  # int
        self.owner = owner  # int -1/0/1
        self.health = health  # int
        self.costs = costs  # [int * 5]
        self.rank = rank  # int 1-3
        self.expertise_gain = expertise_gain  # chr A-E

        # Additional stats
        self.is_identified = self.health is not -1
        if self.is_identified:
            self.total_cost = sum(costs)
            self.discounted_costs = self.__discount()
            self.total_discounted_cost = sum(self.discounted_costs)
            self.needed_ingredients = self.__get_needed_ingredients()
            # self.next_needed_ingredient = get_next_available_ingredient(self)
            self.next_needed_ingredient = get_next_available_ingredient_min(self)
            self.is_currently_unavailable = self.__check_unavailable()
            self.is_currently_available = not self.is_currently_unavailable
            self.is_currently_finishable = self.__check_finishable()
            if self.is_currently_finishable: self.is_currently_available = False
            self.for_project = self.__get_for_project()
            if not self.for_project:
                pass
                # self.is_currently_unavailable = True
        else:
            self.is_currently_unavailable, self.is_currently_finishable, self.is_currently_available = False, False, False
            self.discounted_costs = self.costs
            self.total_cost = self.total_discounted_cost = max_costs[rank]
            self.for_project = False

        self.earn_cost_ratio = self.health / max(1, self.total_discounted_cost)
        self.earn_move_ratio = self.health / self.__get_needed_moves()

    def __discount(self):
        np_costs = np.array(self.costs)
        if self.owner != 1:
            np_expertise = np.array(me.expertise)
        else:
            np_expertise = np.array(enemy.expertise)
        np_discounted = np.subtract(np_costs, np_expertise)
        return np.clip(np_discounted, 0, 100000).tolist()

    def __check_unavailable(self):
        np_needed = np.array(self.needed_ingredients)
        np_available = np.array(available)
        np_ingredients_available = np.less_equal(np_needed, np_available)
        return False in np_ingredients_available.tolist() or sum(self.needed_ingredients) > me.free_slots

    def __check_finishable(self):
        np_needed = np.array(self.needed_ingredients)
        np_has_ingredients = np.equal(np_needed, np.array([0, 0, 0, 0, 0]))
        return False not in np_has_ingredients.tolist()

    def __get_needed_ingredients(self):
        np_costs = np.array(self.discounted_costs)
        if self.owner != 1:
            np_inventory = np.array(me.inventory)
        else:
            np_inventory = np.array(enemy.inventory)
        np_needed = np.clip(np.subtract(np_costs, np_inventory), 0, 10000)
        return np_needed.tolist()

    def __get_needed_moves(self):
        me_to_diag = move_matrix[starts[me.module]][ends["DIAGNOSIS"]]
        me_to_mol = move_matrix[starts[me.module]][ends["MOLECULES"]]
        diag_to_mol = move_matrix[starts["DIAGNOSIS"]][ends["MOLECULES"]]
        mol_to_lab = move_matrix[starts["MOLECULES"]][ends["LABORATORY"]]

        if not self.is_identified:
            # goto diag + connect + goto mole + (connect * needed) + goto lab + connect
            return me_to_diag + 1 + diag_to_mol + self.total_discounted_cost + mol_to_lab + 1
        else:
            # goto mol + (connect * needed) + goto lab + connect
            return me_to_mol + len(self.needed_ingredients) + mol_to_lab + 1

    def __get_for_project(self):
        mol_ind = ingredients.find(self.expertise_gain)
        needed = [max(x) for x in zip(*projects)]
        return me.expertise[mol_ind] < needed[mol_ind]

    # Formatting methods
    def __str__(self):
        return str(self.ID)

    def __repr__(self):
        return self.__str__()

    def __str_all__(self):
        return "{} {} {} {} {} U: {} F: {}".format(self.ID, self.owner, self.health, self.discounted_costs,
                                                   self.expertise_gain,
                                                   self.is_currently_unavailable, self.is_currently_finishable)


class Player:
    global recipes, max_costs

    def __init__(self, module, score, _inventory, expertise, eta):
        self.module = module  # String
        self.score = score  # int
        self.inventory = _inventory  # [int * 5]
        self.free_slots = 10 - sum(self.inventory)
        self.expertise = expertise  # [int * 5]
        self.eta = eta - 1  # int

        # Additional Stats
        self.total_expertise = sum(self.expertise)

    # Call once recipes have been read in
    def do_recipe_calculations(self):
        # self.recipes = [x for x in recipes if x.owner is 0]
        self.has_recipe = len(self.recipes) > 0
        self.recipe_ranks = self.__get_recipe_ranks()

        self.unidentified_recipes = [x for x in self.recipes if not x.is_identified]
        self.has_unidentified_recipes = len(self.unidentified_recipes) > 0

        self.unavailable_recipes = [x for x in self.recipes if x.is_currently_unavailable]
        self.has_unavailable_recipes = len(self.unavailable_recipes) > 0

        self.available_recipes = [x for x in self.recipes if x.is_currently_available]
        self.has_available_recipes = len(self.available_recipes) > 0

        self.finishable_recipes = [x for x in self.recipes if x.is_currently_finishable]
        self.has_finishable_recipes = len(self.finishable_recipes) > 0

        self.carrying_total_cost = sum([x.total_discounted_cost for x in self.recipes]) + 5  # What the hell is this for
        self.difficulty = self.__get_difficulty()

        # Not used yet, possibly for taking ingredients for multiple recipes at a time
        self.reserved_inventory = [0, 0, 0, 0, 0]
        if self.has_finishable_recipes:
            d_costs = [x.discounted_costs for x in self.finishable_recipes]
            self.reserved_inventory = [sum(x) for x in zip(*d_costs)]
        self.available_inventory = [i - r for i, r in zip(self.inventory, self.reserved_inventory)]

    def __get_recipe_ranks(self):
        ranks = [0, 0, 0]
        for x in self.recipes:
            ranks[x.rank - 1] += 1
        return ranks

    def __get_difficulty(self):
        if self.total_expertise < 4:
            return 1
        elif self.total_expertise < 7:
            return 2
        elif self.total_expertise < 10 and self.recipe_ranks[2] == 2:
            return 2
        else:
            return 3

    def __str__(self):
        return "{} {} {} {} {}".format(self.module, self.score, self.inventory, self.expertise, self.eta)

    def __repr__(self):
        return self.__str__()


""" Methods for taking ingredients """


def get_greedy_ingredient():
    return [i for i, x in enumerate(available) if x > 0][0]


# prioritises left -> right
def get_next_available_ingredient(recipe):
    needed = [x > 0 for x in recipe.needed_ingredients]
    available_bools = [x > 0 for x in available]
    available_and_needed = [x and y for x, y in zip(needed, available_bools)]
    if True in available_and_needed:
        return [i for i, x in enumerate(available_and_needed) if x][0]
    else:
        return get_random_ingredient()


# prioritises min available ingredient
def get_next_available_ingredient_min(recipe):
    needed = [x > 0 for x in recipe.needed_ingredients]
    available_bools = [x > 0 for x in available]
    available_and_needed = [x and y for x, y in zip(needed, available_bools)]
    if True in available_and_needed:
        to_take = [i for i, x in enumerate(available_and_needed) if x]
        min_ind = to_take[0]
        for i in to_take:
            if available[i] < available[min_ind]:
                min_ind = i

        return min_ind
    else:
        return get_random_ingredient()


def get_random_ingredient():
    ind = random.randint(0, 4)
    while available[ind] == 0:
        ind = random.randint(0, 4)
    return ind


def get_enemy_ingredient_greedy():
    enemy_recipes = [x for x in enemy.recipes if x.is_identified]
    if len(enemy_recipes) > 0:
        return get_next_available_ingredient(enemy_recipes[0])
    return get_greedy_ingredient()


""" End ingredient methods """


def get_idle_recipes():
    idle = [x for x in recipes if x.owner is -1 and not x.is_currently_unavailable]
    idle.sort(key=lambda x: x.earn_cost_ratio, reverse=True)
    return idle


def read_init_data():
    global projects
    # Science Projects
    del projects[:]
    project_count = int(input())
    for i in range(project_count):
        exp_costs = [int(j) for j in input().split()]
        projects.append(exp_costs)


def read_in_round_data():
    global players, available, recipes, me, enemy

    # Players
    del players[:]
    for i in range(2):
        player_params = input().split()
        module = player_params[0]
        eta, score, storage_a, storage_b, storage_c, storage_d, storage_e, expertise_a, expertise_b, expertise_c, expertise_d, expertise_e = map(
            int, player_params[1:])
        inventory = [storage_a, storage_b, storage_c, storage_d, storage_e]
        expertise = [expertise_a, expertise_b, expertise_c, expertise_d, expertise_e]

        player = Player(module, score, inventory, expertise, eta)
        players.append(player)

    me = players[0]
    enemy = players[1]

    # ingredients
    del available[:]
    for i in input().split():
        available.append(int(i))

    # Recipes
    del recipes[:]
    recipe_count = int(input())
    for i in range(recipe_count):  # Recipe details
        recipe_params = input().split()
        recipe_id, carried_by, rank = map(int, recipe_params[:3])
        expertise_gain = recipe_params[3]
        health, cost_a, cost_b, cost_c, cost_d, cost_e = map(int, recipe_params[4:])
        costs = [cost_a, cost_b, cost_c, cost_d, cost_e]

        recipe = Recipe(recipe_id, carried_by, health, costs, rank, expertise_gain)
        recipes.append(recipe)

    me.recipes = [x for x in recipes if x.owner == 0]
    enemy.recipes = [x for x in recipes if x.owner == 1]

    # Sorting
    # recipes.sort(key=lambda x: x.rank, reverse=True)
    # recipes.sort(key=lambda x: x.health, reverse=True)
    # recipes.sort(key=lambda x: x.earn_cost_ratio, reverse=True)
    # recipes.sort(key=lambda x: x.total_discounted_cost, reverse=False)
    # recipes.sort(key=lambda x: x.earn_move_ratio, reverse=True)
    # recipes.sort(key=lambda x: x.for_project, reverse=True)


move_matrix = [[2, 2, 2, 2],  # Start     >   S,D,M,L
               [0, 3, 3, 3],  # Samples
               [3, 0, 3, 4],  # Diagnosis
               [3, 3, 0, 3],  # Molecules
               [3, 4, 3, 0]]  # Laboratory

starts = {
    "START_POS": 0,
    "SAMPLES": 1,
    "DIAGNOSIS": 2,
    "MOLECULES": 3,
    "LABORATORY": 4
}

ends = {
    "SAMPLES": 0,
    "DIAGNOSIS": 1,
    "MOLECULES": 2,
    "LABORATORY": 3
}


# Returns true if at desination, otherwise moves and returns false
def move_to(destination):
    if me.module != destination:
        print("GOTO", destination)
        return False
    else:
        return True


# Init data
read_init_data()

# game loop
while True:
    """ Round Initialisation """
    read_in_round_data()
    me.do_recipe_calculations()
    idle_recipes = get_idle_recipes()
    # me.recipes.sort(key=lambda x: x.total_discounted_cost, reverse=False)

    """ Program begins """
    print("Players:", file=sys.stderr)
    for p in players: print(p, file=sys.stderr)
    print("Available:", available, file=sys.stderr)
    # print("Held recipes:", len(me.recipes), file=sys.stderr)
    print("Recipes:", file=sys.stderr)
    for r in [x for x in recipes if x.owner != -1]: print(r.__str_all__(), file=sys.stderr)
    print("Idle:", file=sys.stderr)
    for r in [x for x in recipes if x.owner == -1]: print(r.__str_all__(), file=sys.stderr)

    exp_need = [max(0, 4 - x) for x in me.expertise]

    # Stuff to do at the stations
    if me.module == "DIAGNOSIS":
        if me.has_unidentified_recipes:
            print("CONNECT", me.unidentified_recipes[0])
            continue

    elif me.module == "LABORATORY":
        if me.has_finishable_recipes:
            print("CONNECT", me.finishable_recipes[0])
            continue
        if True not in [x + me.expertise[i] < 4 for i, x in enumerate(me.inventory)] and len(me.recipes) > 0:
            # if sum(me.expertise) > 10 and len(me.recipes) > 0:
            print("CONNECT", me.recipes[0])
            continue


    elif me.module == "SAMPLES":
        if len(me.recipes) < 3:
            print("CONNECT", 1)
            continue


    elif me.module == "MOLECULES":
        if me.has_available_recipes:
            print("CONNECT", ingredients[get_next_available_ingredient(me.available_recipes[0])])
            continue
        if sum(me.inventory) < 10 and not me.has_finishable_recipes:
            for i, x in enumerate(me.inventory):
                if x + me.expertise[i] < 4 and available[i] > 0:
                    print("CONNECT", ingredients[i])
                    break
            continue


    else:
        print("I GOT TO HERE!", file=sys.stderr)

    # Movement
    if me.module == "SAMPLES":
        if True not in [x + me.expertise[i] < 4 for i, x in enumerate(me.inventory)]:
            move_to("LABORATORY")
            continue
        else:  # sum(me.expertise) < 10:
            move_to("DIAGNOSIS")
            continue



    elif me.module == "DIAGNOSIS":
        if me.has_finishable_recipes:
            move_to("LABORATORY")
            continue
        else:
            move_to("MOLECULES")
            continue



    elif me.module == "MOLECULES":
        if me.has_finishable_recipes:
            move_to("LABORATORY")
            continue
        move_to("SAMPLES")
        continue


    elif me.module == "LABORATORY":
        if me.has_available_recipes:
            move_to("MOLECULES")
            continue
        else:
            move_to("SAMPLES")
            continue

        for i, x in enumerate(me.inventory):
            pass


    elif me.module == "START_POS":
        move_to("MOLECULES")
        continue

    print("WAIT")
