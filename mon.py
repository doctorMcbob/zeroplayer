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

the game will be a tournament, 16, 32, or 64? maybe decide size from command line

 _ .. ~~ TO DO LIST ~~ .. _
|                          |
  ___      DRAWING      ___
  [x]  draw mon names
  [x]  draw move names
  [x]  draw attack arrows 
  [x]  draw stat modifiers
|                          |
  ___      BALANCE      ___
   []  add turn limit
|                          |
  ___       GAME        ___
   [] make tournament
   [] save/load champion
|__________________________|

-Wxly
"""
import pygame
from pygame import Rect
from pygame.locals import *
from random import randint, choice
import sys

from tokens import tokens as tk

STEP = 2000 if "-s" not in sys.argv else int(sys.argv[sys.argv.index("-s") + 1])


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
        "Compound": """stat;front;AT+1,DF+1""",
    },
    "plant": {
        "Bloom": """attack;front;20""",
        "Invasive": """attack;front,right;10""",
        "Synthisize": """stat;left,right;HEAL5,DF+1""",
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
        "Shed Skin": """stat;front;HEAL5,SP+1""",
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

COLORS = {
    "fire": ((77, 0, 0), (255, 0, 0)),
    "water": ((0, 0, 77), (0, 0, 255)),
    "wind": ((0, 77, 77), (153, 255, 201)),
    "earth": ((51, 26, 0), (153, 77, 0)),
    "plant": ((0, 77, 0), (0, 255, 0)),
}

BATTLE_DRAW_POSITIONS = {
    "team1": {
        "left": (32, 32),
        "right": (32, 128),
        "front": (128, 64)
    },
    "team2":{
        "left": (448, 32),
        "right": (448, 128),
        "front": (320, 64)
    }
}

def draw_arrow(dest, col, pos, leftright):
    pygame.draw.line(dest, col, pos, (pos[0]+64, pos[1]), 3)
    if leftright == "right":
        pygame.draw.line(dest, col, pos, (pos[0]+16, pos[1]+16), 3)
        pygame.draw.line(dest, col, pos, (pos[0]+16, pos[1]-16), 3)
    if leftright == "left":
        pygame.draw.line(dest, col, (pos[0]+64, pos[1]), (pos[0]+48, pos[1]+16), 3)
        pygame.draw.line(dest, col, (pos[0]+64, pos[1]), (pos[0]+48, pos[1]-16), 3)

def draw_move(dest, font, move, leftright, defendingteam):
    for key in MOVES:
        if move in MOVES[key]:
            move_type = key
            move_catagory, targets, data = MOVES[key][move].split(";")
            break
    text = font.render(move, 0, (0, 0, 0))
    dest.blit(text, (128 + ((leftright == "right") * 160), 144))

    if move_catagory == "stat":
        leftright = "left" if leftright == "right" else "right"
    
    for target in targets.split(","):

        if move_catagory == "attack":
            defender = defendingteam.mons[(defendingteam.front + index_modifier[target]) % 3]

            if defender is None:
                col = (0, 0, 0)
            elif move_type in ELEMENTS[defender.element]["weak"] + ANIMALS[defender.animal]["weak"]:
                col = (255, 0, 0)
            elif move_type in ELEMENTS[defender.element]["res"] + ANIMALS[defender.animal]["res"]:
                col = (0, 0, 255)
        
            else:
                col = (0, 0, 0)
        else:
            col = (0, 255, 0)


        draw_arrow(dest, col, (208, [96, 160, 32][index_modifier[target]]), leftright)

def draw_battle(dest, font, team1, team2):
    for i, mon in enumerate(team1.mons):
        if mon is None: continue
        if i == team1.front:
            PW = 3
            pos = BATTLE_DRAW_POSITIONS["team1"]["front"]
        elif i == (team1.front + 1) % 3:
            PW = 2
            pos = BATTLE_DRAW_POSITIONS["team1"]["right"]
        elif i == (team1.front - 1) % 3:
            PW = 2
            pos = BATTLE_DRAW_POSITIONS["team1"]["left"]

        col1, col2 = COLORS[mon.element]
        tk.draw_token(dest, mon.animal, pos, col1=col1, col2=col2, PW=PW)
        
        pygame.draw.rect(dest, (0, 0, 0), Rect((pos[0] - 8*PW, pos[1] + 18*PW), (32*PW, 5*PW)))
        pygame.draw.rect(dest, (0, 255, 0), Rect(((pos[0] - 8*PW) + 2, (pos[1] + 18*PW)+2),((mon.HP / (mon.stats["HP"]*10)) * (32*PW)-4, (5*PW)-4)))
        stat_mods = ""
        for stat in ["AT", "DF", "SP"]:
            if mon.stat_mods[stat]:
                stat_mods += " {} +{}".format(stat, mon.stat_mods[stat])
        stat_mods = font.render(stat_mods, 0, (0, 0, 0))
        dest.blit(stat_mods, (pos[0]-32, pos[1]-16))
        
    for i, mon in enumerate(team2.mons):
        if mon is None: continue
        if i == team2.front:
            PW = 3
            pos = BATTLE_DRAW_POSITIONS["team2"]["front"]
        elif i == (team2.front + 1) % 3:
            PW = 2
            pos = BATTLE_DRAW_POSITIONS["team2"]["right"]
        elif i == (team2.front - 1) % 3:
            PW = 2
            pos = BATTLE_DRAW_POSITIONS["team2"]["left"]

        col1, col2 = COLORS[mon.element]
        tk.draw_token(dest, mon.animal, pos, col1=col1, col2=col2, PW=PW)

        pygame.draw.rect(dest, (0, 0, 0), Rect((pos[0] - 8*PW, pos[1] + 18*PW), (32*PW, 5*PW)))
        pygame.draw.rect(dest, (0, 255, 0), Rect(((pos[0] - 8*PW) + 2, (pos[1] + 18*PW)+2),((mon.HP / (mon.stats["HP"]*10)) * (32*PW)-4, (5*PW)-4)))
        stat_mods = ""
        for stat in ["AT", "DF", "SP"]:
            if mon.stat_mods[stat]:
                stat_mods += " {} +{}".format(stat, mon.stat_mods[stat])
        stat_mods = font.render(stat_mods, 0, (0, 0, 0))
        dest.blit(stat_mods, (pos[0]-32, pos[1]-16))

    if team1.mons[team1.front] is not None:
        name = font.render(team1.mons[team1.front].element + " " + team1.mons[team1.front].animal, 0, (0, 0, 0))
        dest.blit(name, (114, 32))
    if team2.mons[team2.front] is not None:
        name2 = font.render(team2.mons[team2.front].element + " " + team2.mons[team2.front].animal, 0, (0, 0, 0))
        dest.blit(name2, (320, 32))
        
        
def calculate_damage(attacker, defender, move_type, base_dmg):
    dmg = (base_dmg * (attacker.stats["AT"] + attacker.stat_mods["AT"])) * (1 / (defender.stats["DF"] + defender.stat_mods["DF"]))
    if move_type in ANIMALS[defender.animal]["weak"] + ELEMENTS[defender.element]["weak"]:
        dmg *= 1.25
    if move_type in ANIMALS[defender.animal]["res"] + ELEMENTS[defender.element]["res"]:
        dmg *= 0.75
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

    team1.front = team1.mons.index(mon1)
    team2.front = team2.mons.index(mon2)

    if mon1.stats["SP"] + mon1.stat_mods["SP"] > mon2.stats["SP"] + mon2.stat_mods["SP"] or (mon1.stats["SP"] + mon1.stat_mods["SP"] == mon2.stats["SP"] + mon2.stat_mods["SP"] and randint(0, 1)):
        yield mon1_move, "left", team2
        team1.resolve_move(mon1, mon1_move, team2)
        kill_mons(team2)
        if mon2.HP <= 0: return
        yield mon2_move, "right", team1
        team2.resolve_move(mon2, mon2_move, team1)
        kill_mons(team1)
    else:
        yield mon2_move, "right", team1
        team2.resolve_move(mon2, mon2_move, team1)
        kill_mons(team1)
        if mon1.HP <= 0: return
        yield mon1_move, "left", team2
        team1.resolve_move(mon1, mon1_move, team2)
        kill_mons(team2)
        
class Mon(object):
    def __init__(self, element, animal, moves=False, level=1):
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
        
        self.moves = moves or (
            choice(list(MOVES[self.element].keys())),
            choice(list(MOVES[self.animal].keys())),
        )

    def __str__(self):
        return "{} {};{};{}".format(self.element, self.animal, self.moves, self.level)

    def level_up(self):
        for stat in self.stats:
            self.stats[stat] += randint(0, ANIMAL_STAT_MODS[self.animal]+1)
        self.HP = self.stats["HP"] * 10
        self.level += 1


class Team(object):
    def __init__(self, mon1=None, mon2=None, mon3=None):
        self.mons = [mon1, mon2, mon3]
        self.front = 0


    def __str__(self):
        return " | ".join([str(mon) for mon in self.mons])
        
    def resolve_move(self, attacker, move, enemy_team):
        """
        Move Interpreter (magic goes here)
        """
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
                mon = self.mons[(self.front + index_modifier[target]) % 3]

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

def make_mon():
    return Mon(
        choice(list(ELEMENTS.keys())),
        choice(list(ANIMALS.keys())) 
    )


def update():
    global STEP
    pygame.display.update()
    for e in pygame.event.get():
        if e.type == QUIT or e.type == KEYDOWN and e.key == K_ESCAPE:
            quit()
        if e.type == KEYDOWN:
            if e.key == K_LEFT: STEP = min(STEP * 2, 2000)
            if e.key == K_RIGHT: STEP = max(STEP // 2, 1)


if __name__ == """__main__""":
    # TEMPORARY DEMO
    
    myTeam = Team(make_mon(), make_mon(), make_mon())
    enemyTeam = Team(make_mon(), make_mon(), make_mon())

    pygame.init()
    SCREEN = pygame.display.set_mode((528, 256)) if "-f" not in sys.argv else pygame.display.set_mode((528, 256), FULLSCREEN)
    CLOCK = pygame.time.Clock()
    HEL16 = pygame.font.SysFont("Helvetica", 16)
    t = 0
    while True:
        t += CLOCK.tick()

        if t > STEP and any(myTeam.mons) and any(enemyTeam.mons):
            for move, leftright, defenders in battle_turn(myTeam, enemyTeam):
                t = 0
                SCREEN.fill((255, 255, 255))
                draw_battle(SCREEN, HEL16, myTeam, enemyTeam)
                draw_move(SCREEN, HEL16, move, leftright, defenders)
                while t < STEP:
                    t += CLOCK.tick()
                    update()

                   
        SCREEN.fill((255, 255, 255))
        draw_battle(SCREEN, HEL16, myTeam, enemyTeam)
        update()

    
