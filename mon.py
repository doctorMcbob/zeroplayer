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
    "bird": { "SP": 4, "AT": 2, "DF": 2, "HP": 2 },
    "ape": { "SP": 2, "AT": 3, "DF": 2, "HP": 3 },
    "rodent": { "SP": 3, "AT": 3, "DF": 2, "HP": 2 },
    "snake": { "SP": 3, "AT": 2, "DF": 3, "HP": 2 },
    "monster" { "SP": 2, "AT": 4, "DF": 2, "HP": 2 },
}

ATTACKS = {
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

def calculate_damage(attacker, defender, move_type, base_dmg):
    dmg = (base_dmg * attacker["stats"]["AT"]) * (1 / defender["stats"]["DF"])
    if move_type in ANIMALS[defender.animal]["weak"] + ELEMENTS[defender.element]["weak"]:
        dmg *= 1.25
    if move_type in ANIMALS[defender.animal]["res"] + ELEMENTS[defender.element]["res"]:
        dmg *= 0.75
    return dmg
        
class Mon(object):
    def __init__(self, element, animal, level=1):
        self.element = element
        self.animal = animal

        self.level = 1

        self.stats = ANIMAL_STAT_MODS[self.animal].copy()
        while self.level < level:
            self.level_up()

        self.HP = self.stats["HP"]  # current HP vs max HP
        
        self.moves = (
            choice(ATTACKS[self.element]),
            choice(ATTACKS[self.animal]),
        )
            
    def level_up(self):
        for stat in self.stats:
            self.stats[stat] += randint(0, ANIMAL_STAT_MODS[self.animal]+1)
        self.HP = self.stats["HP"]
        self.level += 1


class Team(object):
    def __init__(self, mon1=None, mon2=None, mon3=None):
        self.mons = [mon1, mon2, mon3]
        self.front = 0

    def resolve_attack(self, enemy_team):
        """
        Move Interpreter (magic goes here)
        """
        pass
