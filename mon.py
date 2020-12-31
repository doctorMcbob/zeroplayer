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
   [] draw bracket
|                          |
  ___      BALANCE      ___
  [x]  add turn limit
|                          |
  ___       GAME        ___
  [x] make tournament
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
TURN_LIMIT = 100 if "-t" not in sys.argv else int(sys.argv[sys.argv.index("-t") + 1])
BRACKET_SIZE = 4 if "-b" not in sys.argv else int(sys.argv[sys.argv.index("-b") + 1])

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

DRAWSTUFF = {
    "SCREEN": None,
    "FIGHTSURF": None,
    "BRACKET": None,
    "EXTRASURF": None,
}
ROOT = None

def draw():
    DRAWSTUFF["SCREEN"].fill((255, 255, 255))
    DRAWSTUFF["SCREEN"].blit(DRAWSTUFF["FIGHTSURF"], (128, 0))
    DRAWSTUFF["SCREEN"].blit(DRAWSTUFF["BRACKET"], (0, 256))
    DRAWSTUFF["SCREEN"].blit(DRAWSTUFF["EXTRASTUFF"], (0, DRAWSTUFF["SCREEN"].get_height()-DRAWSTUFF["EXTRASTUFF"].get_height()))

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
                stat_mods += " {}+{}".format(stat, mon.stat_mods[stat])
        stat_mods = font.render(stat_mods, 0, (0, 0, 0))
        dest.blit(stat_mods, (pos[0]-32, pos[1]-16))
        lvl = font.render("L{}".format(mon.level), 0, (0, 0, 0))
        dest.blit(lvl, (pos[0]-32, pos[1]))
        
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
        lvl = font.render("L{}".format(mon.level), 0, (0, 0, 0))
        dest.blit(lvl, (pos[0]-32, pos[1]))

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
    deadmons = []
    for i, mon in enumerate(team.mons):
        if mon is not None and mon.HP <= 0:
            team.mons[i] = None        
            deadmons.append(mon)
    return deadmons

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
        mon1.XP += sum([mon.level for mon in kill_mons(team2)])
        if mon2.HP <= 0: return
        yield mon2_move, "right", team1
        team2.resolve_move(mon2, mon2_move, team1)
        mon2.XP += sum([mon.level for mon in kill_mons(team1)])
    else:
        yield mon2_move, "right", team1
        team2.resolve_move(mon2, mon2_move, team1)
        mon2.XP += sum([mon.level for mon in kill_mons(team1)])
        if mon1.HP <= 0: return
        yield mon1_move, "left", team2
        team1.resolve_move(mon1, mon1_move, team2)
        mon1.XP += sum([mon.level for mon in kill_mons(team2)])
        
class Mon(object):
    def __init__(self, element, animal, moves=None, level=False, stats=None):
        self.element = element
        self.animal = animal

        self.level = level if level else 1
        self.XP = 0
        
        self.stats = stats or ANIMAL_STAT_MODS[self.animal].copy()

        self.stat_mods = {
            "AT": 0, "DF": 0, "SP": 0,
        }
            
        self.HP = self.stats["HP"] * 10  # current HP vs max HP
        
        self.moves = moves or (
            choice(list(MOVES[self.element].keys())),
            choice(list(MOVES[self.animal].keys())),
        )

    def __str__(self):
        return "{} {};{};{};{}".format(self.element, self.animal, self.moves, self.level, self.stats)

    def reset_mods(self):
        self.stat_mods = {
            "AT": 0, "DF": 0, "SP": 0,
        }
    
    def level_up(self):
        for stat in self.stats:
            self.stats[stat] += randint(0, ANIMAL_STAT_MODS[self.animal][stat])
        self.level += 1


class Team(object):
    def __init__(self, mon1=None, mon2=None, mon3=None):
        self.mons = [mon1, mon2, mon3]
        self.front = 0

    def __str__(self):
        return " | ".join([str(mon) for mon in self.mons])

    def drawn_team(self):
        surf = pygame.Surface((32, 32))
        surf.fill((255, 255, 255))
        col1, col2 = COLORS[self.mons[0].element]
        tk.draw_token(surf, self.mons[0].animal, (8, 0), col1=col1, col2=col2, PW=1)
        col1, col2 = COLORS[self.mons[1].element]
        tk.draw_token(surf, self.mons[1].animal, (0, 16), col1=col1, col2=col2, PW=1)
        col1, col2 = COLORS[self.mons[2].element]
        tk.draw_token(surf, self.mons[2].animal, (16, 16), col1=col1, col2=col2, PW=1)
        return surf
        
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


class BracketNode(object):
    def __init__(self, team1, team2):
        self.team1 = team1
        self.team2 = team2

    def resolve(self, font, clock):
        if type(self.team1) == BracketNode:
            self.team1 = self.team1.resolve(font, clock)
        if type(self.team2) == BracketNode:
            self.team2 = self.team2.resolve(font, clock)

        DRAWSTUFF["BRACKET"] = ROOT.drawn_node()
        return run_battle(DRAWSTUFF["FIGHTSURF"], font, clock, self.team1, self.team2)

    def drawn_node(self):
        left_img = self.team1.drawn_node() if type(self.team1) == BracketNode else self.team1.drawn_team()
        right_img = self.team2.drawn_node() if type(self.team2) == BracketNode else self.team2.drawn_team()
        W = left_img.get_width() + right_img.get_width()
        H = max(left_img.get_height(), right_img.get_height()) + 32
        surf = pygame.Surface((W, H))
        surf.fill((255, 255, 255))
        surf.blit(left_img, (0, 32))
        surf.blit(right_img, (left_img.get_width(), 32))
        pygame.draw.line(surf, (0, 0, 0), (left_img.get_width() // 2, 32), (left_img.get_width() // 2, 16), 3)
        pygame.draw.line(surf, (0, 0, 0), (W - right_img.get_width() // 2, 32), (W - right_img.get_width() // 2, 16), 3)
        pygame.draw.line(surf, (0, 0, 0), (left_img.get_width() // 2, 16), (W - right_img.get_width() // 2, 16), 3)
        pygame.draw.line(surf, (0, 0, 0), (W//2, 16), (W//2, 0), 3)
        return surf

def make_bracket(size=3):
    bottom_nodes = [Team(make_mon(), make_mon(), make_mon()) for _ in range(2 ** size)]
    top_nodes = []
    while len(top_nodes + bottom_nodes) > 1:
        while bottom_nodes:
            top_nodes.append(BracketNode(bottom_nodes.pop(), bottom_nodes.pop()))
        top_nodes, bottom_nodes = bottom_nodes, top_nodes
    return bottom_nodes.pop()


def make_mon():
    return Mon(
        choice(list(ELEMENTS.keys())),
        choice(list(ANIMALS.keys())) 
    )

def load_mon(string):
    name, moves, level, stats = string.split(";")
    element, animal = name.split()
    return Mon(element, animal, moves=eval(moves), level=int(level), stats=eval(stats))

def load_team(string):
    mon_strings = string.split(" | ")
    mons = [load_mon(s) for s in mon_strings]
    return Team(mons[0], mons[1], mons[2])

def update():
    global STEP
    draw()
    pygame.display.update()
    for e in pygame.event.get():
        if e.type == QUIT or e.type == KEYDOWN and e.key == K_ESCAPE:
            quit()
        if e.type == KEYDOWN:
            if e.key == K_LEFT: STEP = min(STEP * 2, 2000)
            if e.key == K_RIGHT: STEP = max(STEP // 2, 1)


def choose_winner(team1, team2):
    if not any(team1.mons): return team2
    if not any(team2.mons): return team1
    if team1.mons.count(None) < team2.mons.count(None): return team1
    if team1.mons.count(None) > team2.mons.count(None): return team2
    team1_damage, team2_damage = 0, 0
    for i in range(3):
        if team1.mons[i] is not None:
            team1_damage += team1.mons[i].stats["HP"]*10 - team1.mons[i].HP
        if team2.mons[i] is not None:
            team2_damage += team2.mons[i].stats["HP"]*10 - team2.mons[i].HP
    if team1_damage < team2_damage: return team1
    if team1_damage > team2_damage: return team2
    return team1 if randint(0, 1) else team2
    
def run_battle(surface, font, clock, team1, team2):
    team1_mons = [mon for mon in team1.mons]
    team2_mons = [mon for mon in team2.mons]
    timer = 0
    turn = 0
    while turn < TURN_LIMIT and any(team1.mons) and any(team2.mons):
        timer += clock.tick()
        turn_num = font.render(str(turn), 0, (0, 0, 0))
        if timer > STEP:
            for move, leftright, defenders in battle_turn(team1, team2):
                timer = 0
                surface.fill((255, 255, 255))
                surface.blit(turn_num, (242, 204))
                draw_battle(surface, font, team1, team2)
                draw_move(surface, font, move, leftright, defenders)
                while timer < STEP:
                    timer += clock.tick()
                    update()
            for mon in team1.mons + team2.mons:
                if mon is None: continue
                if mon.XP > mon.level * 2:
                    mon.XP = 0
                    mon.level_up()
            turn += 1
        surface.fill((255, 255, 255))
        surface.blit(turn_num, (242, 204))
        draw_battle(surface, font, team1, team2)
        update()

    winner = choose_winner(team1, team2) 
    team1.mons = team1_mons
    team2.mons = team2_mons
    for mon in team1.mons + team2.mons:
        mon.HP = mon.stats["HP"] * 10
        mon.reset_mods()
    return winner


def initialize():
    global CLOCK, HEL16
    pygame.init()
    DRAWSTUFF["SCREEN"] = pygame.display.set_mode((896, 640)) if "-f" not in sys.argv else pygame.display.set_mode((896, 640), FULLSCREEN)
    DRAWSTUFF["FIGHTSURF"] = pygame.Surface((600, 256))
    DRAWSTUFF["EXTRASTUFF"] = pygame.Surface((896, 64))
    CLOCK = pygame.time.Clock()
    HEL16 = pygame.font.SysFont("Helvetica", 16)
    
def run_tournament():
    global ROOT
    ROOT = make_bracket(BRACKET_SIZE)
    DRAWSTUFF["BRACKET"] = ROOT.drawn_node()
    return ROOT.resolve(HEL16, CLOCK)


def get_champs():
    with open("mon.save", "r") as f:
        champs = eval(f.read())
    return champs

def save_champ(team):
    champs = get_champs()
    champs[BRACKET_SIZE] = str(team)
    with open("mon.save", "w") as f:
        f.write(repr(champs))
    
if __name__ == """__main__""":
    winners = []
    initialize()
    DRAWSTUFF["EXTRASTUFF"].fill((255, 255, 255))

    while True:
        winner = run_tournament()

        DRAWSTUFF["EXTRASTUFF"].fill((255, 255, 255))
        DRAWSTUFF["EXTRASTUFF"].blit(HEL16.render("WINNER", 0, (0, 0, 0)), (0, 0))
        t = 0
        while t < 2000:
            t += CLOCK.tick()
            update()
        
        champs = get_champs()
        if BRACKET_SIZE in champs:
            champion = load_team(champs[BRACKET_SIZE])
            DRAWSTUFF["EXTRASTUFF"].fill((255, 255, 255))
            DRAWSTUFF["EXTRASTUFF"].blit(HEL16.render("CHALLENGING CHAMPION", 0, (0, 0, 0)), (0, 0))
            DRAWSTUFF["EXTRASTUFF"].blit(champion.drawn_team(), (0, 16))
            t = 0
            while t < 2000:
                t += CLOCK.tick()
                update()
            
            champion = run_battle(DRAWSTUFF["FIGHTSURF"], HEL16, CLOCK, champion, winner)
        else:
            champion = winner
        save_champ(champion)
        
    
