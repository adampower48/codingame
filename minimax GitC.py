class Troop:
    def __init__(self, owner=0):
        self.ID = 0
        self.owner = "me" if owner == 1 else "enemy"
        self.size = 0
        self.target = 0
        self.travel_time = 0


class Factory:
    def __init__(self, owner=0):
        self.ID = 0
        self.owner = "me" if owner == 1 else "enemy"
        self.troops = 0
        self.production = 0


def evaluate(factories, troops):
    troop_weight = 2
    production_weight = 3
    my_troops = 0
    enemy_troops = 0
    my_production = 0
    enemy_production = 0

    for f in factories:
        if f.owner == "me":
            my_troops += f.troops
            my_production += f.production
        elif f.owner == "enemy":
            enemy_troops += f.troops
            enemy_production += f.production

    for t in troops:
        if t.owner == "me":
            my_troops += t.size
        else:
            enemy_troops += t.size

    return (my_troops - enemy_troops) * troop_weight + (my_production - enemy_production) * production_weight
