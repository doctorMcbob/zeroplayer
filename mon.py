"""
Zero Player Mons!
Legally Destinct From Pokemon

a Mon has an elemental type and an animal type, think class/race from DnD
a Mon has two moves, one selected from its elements pool and one from its animals pool
a Mon has 4 stats, SPeed, ATtack, DeFence, Hit Points. 
Modifiers associated with the Mons animal determine stats at level 1 as well as level scaling

a Team has 3 Mons. They will rotate so whichever Mon last attacking is in the front
   with the other two in the back. basically triple rotation battles...

a Mons attacks might hit all three, or just the front and left, or maybe just the two in the back
a Mons attack might boost its own stats or the stats of the whole team. 

damage is determined as 
   (the base attack of the move * the attack stat) * (1 / the defence)

speed stat determines which Mon goes first

a battle turn goes like this, 
+---
|   Each team selects a Mon and move
|   Each team rotates that mon to the front of the team
|   Speed stat determines which Mon goes first
|   That Mon resolves move
|   check if any Mons have died
|   The other Mon resolves move
|   check if any Mons have died
+---

When a Mon is reduced to 0 HP it is dead and removed from the team
if the Team has an open slot then a defeated Wild Mon has a chance to join the team (?)

at the end of the run, the team is saved, then the following run will have to defeat the "champion"
if the champion is defeated, the new team becomes the champion

maybe the old champion will become a gym leader or something, idk ill get there when i get there
"""
from random import randint, choice

ELEMENTS = {
    "fire": {"weak":["water"], "res":["wind"]},
    "water": {"weak":["plant"], "res":["fire"]},
    "wind": {"weak":["wind"], "res":[]},
    "earth": {"weak":["plant"], "res":["fire", "wind", "water"]},
    "plant": {"weak":["fire", "wind"], "res":["earth", "water"]},
}

ANIMALS = {
    "bird": {"weak":["snake"], "res":["rodent"]},
    "ape": {"weak":["monster", "snake"], "res":["bird"]},
    "rodent": {"weak":["snake", "bird"], "res":["ape"]},
    "snake": {"weak":["bird"], "res":["ape"]},
    "monster": {"weak":["rodent", "monster"], "res":["snake"]},
}

ANIMAL_STAT_MODS = {
    "bird": { "SP": 4, "AT": 2, "DF": 2, "HP": 10 },
    "ape": { "SP": 2, "AT": 3, "DF": 2, "HP": 15 },
    "rodent": { "SP": 3, "AT": 3, "DF": 2, "HP": 10 },
    "snake": { "SP": 3, "AT": 2, "DF": 3, "HP": 10 },
    "monster": { "SP": 2, "AT": 4, "DF": 2, "HP": 10 },
}

MOVES = {
    "fire": {
        "Blast": """attack;front;20""",
        "Cook": """attack;left,right;10""",
        "Enflame": """stat;front;AT+1,SP+1"""
    },
    "water": {
        "Gush": """attack;front;20""",
        "Drown": """attack;front,left,right;8""",
        "Wade": """stat;left,right;HEAL10"""
    },
    "wind": {
        "Gust": """attack;front;20""",
        "Snipe": """attack;left;25""",
        "Breeze": """stat;front,left,right;SP+2"""
    },
    "earth": {
        "Avalanche": """attack;front;20""",
        "Quake": """attack;front,left,right;8""",
        "Compound": """stat;front;DF+2""",
    },
    "plant": {
        "Bloom": """attack;front;20""",
        "Invasive": """attack;front,right;10""",
        "Synthisize": """stat;front,left,right;HEAL5,DF+1""",
    },
    "bird": {
        "Dive Bomb": """attack;front;20""",
        "Pick": """attack;right;20""",
        "Floof": """stat;left,right;HEAL5,SP+1"""
    },
    "ape": {
        "Monke Mash": """attack;front;20""",
        "Angry Ape": """attack;left,right;15""",
        "Big Brain": """stat;front;SP+1,AT+1,DF+1""",
    },
    "rodent": {
        "Gnaw": """attack;front;20""",
        "Double Claw": """attack;left,right;10""",
        "Burrow": """stat;front,left,right;SP+1,DF+1"""
    },
    "snake": {
        "Bite": """attack;front;20""",
        "Constrict": """attack;right;20""",
        "Shed Skin": """stat;front;HEAL5,DF+1""",
    },
    "monster": {
        "Dominate": """attack;front;20""",
        "Ruin": """attack;front,right,left;10""",
        "Terrify": """stat;front,left,right;AT+2"""
    }
}

index_modifier = {
    "front": 0, "left": -1, "right":1
}
        

def calculate_damage(attacker, defender, move_type, base_dmg):
    dmg = (base_dmg * (attacker.stats["AT"] + attacker.stat_mods["AT"])) * (1 / (defender.stats["DF"] + defender.stat_mods["DF"]))
    if move_type in ANIMALS[defender.animal]["weak"] + ELEMENTS[defender.element]["weak"]:
        dmg *= 1.25
    if move_type in ANIMALS[defender.animal]["res"] + ELEMENTS[defender.element]["res"]:
        dmg *= 0.75
    print(dmg, "damage")
    return dmg

def kill_mons(team):
    for i, mon in enumerate(team.mons):
        if mon is not None and mon.HP <= 0: team.mons[i] = None        

def battle_turn(team1, team2):
    mon1 = choice(team1.mons)
    while mon1 is None: mon1 = choice(team1.mons)
    mon1_move = choice(mon1.moves)
    mon2 = choice(team2.mons)
    while mon2 is None: mon2 = choice(team2.mons)
    mon2_move = choice(mon2.moves)

    print("team1 sends", mon1.element, mon1.animal)
    print("team2 sends", mon2.element, mon2.animal)
    
    team1.front = team1.mons.index(mon1)
    team2.front = team2.mons.index(mon2)

    if mon1.stats["SP"] + mon1.stat_mods["SP"] > mon2.stats["SP"] + mon2.stat_mods["SP"] or (mon1.stats["SP"] + mon1.stat_mods["SP"] == mon2.stats["SP"] + mon2.stat_mods["SP"] and randint(0, 1)):
        team1.resolve_move(mon1, mon1_move, team2)
        kill_mons(team2)
        if mon2.HP <= 0: return
        team2.resolve_move(mon2, mon2_move, team1)
        kill_mons(team1)
    else:
        team2.resolve_move(mon2, mon2_move, team1)
        kill_mons(team1)
        if mon1.HP <= 0: return
        team1.resolve_move(mon1, mon1_move, team2)
        kill_mons(team2)
        
class Mon(object):
    def __init__(self, element, animal, level=1):
        self.element = element
        self.animal = animal

        self.level = 1

        self.stats = ANIMAL_STAT_MODS[self.animal].copy()
        while self.level < level:
            self.level_up()

        self.stat_mods = {
            "AT": 0, "DF": 0, "SP": 0,
        }
            
        self.HP = self.stats["HP"] * 10  # current HP vs max HP
        
        self.moves = (
            choice(list(MOVES[self.element].keys())),
            choice(list(MOVES[self.animal].keys())),
        )
            
    def level_up(self):
        for stat in self.stats:
            self.stats[stat] += randint(0, ANIMAL_STAT_MODS[self.animal]+1)
        self.HP = self.stats["HP"] * 10
        self.level += 1


class Team(object):
    def __init__(self, mon1=None, mon2=None, mon3=None):
        self.mons = [mon1, mon2, mon3]
        self.front = 0

    def resolve_move(self, attacker, move, enemy_team):
        """
        Move Interpreter (magic goes here)
        """
        print(attacker.element, attacker.animal, "uses", move)
        for ty in MOVES:
            if move in MOVES[ty]:
                movedata = MOVES[ty][move]
                movetype = ty
                break
            
        move_catagory, targets, data = movedata.split(";")
        
        for target in targets.split(","):
            if move_catagory == "attack":
                mon = enemy_team.mons[(enemy_team.front + index_modifier[target]) % 3]
            elif move_catagory == "stat":
                mon = self.mons[(enemy_team.front + index_modifier[target]) % 3]

            if mon is None: continue
            
            if move_catagory == "attack":
                dmg = calculate_damage(attacker, mon, movetype, int(data))
                mon.HP -= dmg

            if move_catagory == "stat":
                for statmod in data.split(","):
                    if "HEAL" in statmod:
                        mon.HP = min(mon.stats["HP"] * 10, mon.HP + 100 * (int(statmod[4:]) / float(mon.stats["HP"] * 10)))
                        continue
                    
                    stat = statmod[:2]
                    mod = int(statmod[2:])
                    mon.stat_mods[stat] += mod

if __name__ == """__main__""":
    mon1 = Mon(
        choice(list(ELEMENTS.keys())),
        choice(list(ANIMALS.keys())) 
    )
    mon2 = Mon(
        choice(list(ELEMENTS.keys())),
        choice(list(ANIMALS.keys())) 
    )
    mon3 = Mon(
        choice(list(ELEMENTS.keys())),
        choice(list(ANIMALS.keys())) 
    )
    myTeam = Team(mon1, mon2, mon3)

    mon4 = Mon(
        choice(list(ELEMENTS.keys())),
        choice(list(ANIMALS.keys())) 
    )
    mon5 = Mon(
        choice(list(ELEMENTS.keys())),
        choice(list(ANIMALS.keys())) 
    )
    mon6 = Mon(
        choice(list(ELEMENTS.keys())),
        choice(list(ANIMALS.keys())) 
    )
    enemyTeam = Team(mon4, mon5, mon6)

    def print_teams():
        print()
        print("my team", "front:", myTeam.front)
        for i, mon in enumerate(myTeam.mons):
            print("-")
            if mon is None:
                print("DEAD")
                continue
            print(i, ":", mon.element, mon.animal)
            print("HP", mon.HP,"/", mon.stats["HP"] * 10)
            print(mon.stat_mods)

        print("-----")
        print("enemy team", "front:", enemyTeam.front)
        for i, mon in enumerate(enemyTeam.mons):
            print("-")
            if mon is None:
                print("DEAD")
                continue
            print(i, ":", mon.element, mon.animal)
            print("HP", mon.HP,"/", mon.stats["HP"] * 10)
            print(mon.stat_mods)

    from os import system
    system("cls|clear")
    print_teams()
    while any(myTeam.mons) and any(enemyTeam.mons):
        input("\nenter to run next turn...")
        system("cls|clear")
        battle_turn(myTeam, enemyTeam)
        print_teams()
    
