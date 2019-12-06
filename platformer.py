import pygame
from pygame.locals import *
import random

pygame.init()

W, H = 64 * 100, 64 * 3
SCREEN = pygame.display.set_mode((min(W, 640), min(H, 480)))
CLOCK = pygame.time.Clock()

HEL16 = pygame.font.SysFont("helvetica", 16)

pygame.display.set_caption("zero player platformer")
sprites = {
    "wizrun0":pygame.Surface((64, 64)),
    "wizrun1":pygame.Surface((64, 64)),
    "wizjmp0":pygame.Surface((64, 64)),
    "wizjmp1":pygame.Surface((64, 64)),
    "wizair0":pygame.Surface((64, 64)),
    "wizair1":pygame.Surface((64, 64)),

    "baddie0":pygame.Surface((64, 32)),
    "baddie1":pygame.Surface((64, 32)),

    "platform":pygame.image.load("img/floor.png").convert(),
    "poof":pygame.image.load("img/poof.png").convert(),
}

wiz = pygame.image.load("img/running_wizard.png").convert()
sprites['wizrun0'].blit(wiz, (0, 0))
sprites['wizrun1'].blit(wiz, (-192, 0))
sprites['wizjmp0'].blit(wiz, (-64, 0))
sprites['wizjmp1'].blit(wiz, (-64-192, 0))
sprites['wizair0'].blit(wiz, (-128, 0))
sprites['wizair1'].blit(wiz, (-128-192, 0))
baddie = pygame.image.load("img/baddie.png").convert()
sprites['baddie0'].blit(baddie, (0, 0))
sprites['baddie1'].blit(baddie, (-64, 0))

for key in sprites: sprites[key].set_colorkey((1, 255, 1))

frame=0
enemies = []
platforms = []

for x in range(W // 64):
    platforms.append(pygame.rect.Rect((x*64, H-32), (64, 32)))
    if x > 8 and x % 4 == 0:
        roll = random.randint(0, 60)
        if roll <= 15:
            enemies.append(pygame.rect.Rect(((x+1)*64, 16), (64, 32)))
            platforms.append(pygame.rect.Rect((x*64, H-64), (64, 32)))
        elif roll <= 30:
            enemies.append(pygame.rect.Rect((x*64, H-64),(64, 32)))
        elif roll <= 45:
            enemies.append(pygame.rect.Rect((x*64, 64),(64, 32)))
        else:
            enemies.append(pygame.rect.Rect((x*64, H-64), (64, 32)))
            platforms.append(pygame.rect.Rect(((x+1)*64, H-64), (64, 32)))
            platforms.append(pygame.rect.Rect(((x+1)*64, H-96), (64, 32)))

player = pygame.rect.Rect((0, H-96), (64, 64))
state = "run"

def drawn():
    surf = pygame.Surface((W, H))
    surf.fill((100, 200, 250))
    for enemy in enemies: surf.blit(sprites["baddie" + str(frame%2)], (enemy.x, enemy.y))
    for plat in platforms: surf.blit(sprites["platform"], (plat.x, plat.y))

    for x in range(0, W // 64):
        if jumps and x <= jumps[-1]:
            col = (0, 255, 0) if x in jumps else (100, 100, 100)
            pygame.draw.circle(surf, col, ((x*64)+32, 16), 5)
    return surf

jumps = []
def jump(frame):
    if not jumps or frame > jumps[-1]:
        if random.randint(0, 1): jumps.append(frame)
    return frame in jumps

def death():
    global frame
    jumps.pop()
    SCREEN.blit(sprites['poof'], (64, player.y))
    player.x = 0
    player.y = H - 96
    frame = 0

if __name__ == "__main__":
    complete = False
    sidx = 0
    slist = [120, 60, 30, 15, 6, 3]
    while frame < W // 64:
        if complete:
            CLOCK.tick(3)
        else:
            CLOCK.tick(slist[sidx])
        if state == 'jmp':
            player.y -= 96

        if player.move(64, 0).collidelist(platforms) == -1:
            player.x += 64
            frame += 1

        if player.move(0, 32).collidelist(platforms) == -1:
            state = "air"
            player.y += 32
        else:
            state = 'run'

        if state != "air" and jump(frame):
            state = 'jmp'
        
        SCREEN.fill((100, 100, 100))
        SCREEN.blit(drawn(), (64 - player.x, 0))
        SCREEN.blit(sprites["wiz"+state+str(frame%2)], (64, player.y))
        SCREEN.blit(HEL16.render(str(frame), 0, (0, 0, 0)), (0, 32))
        pygame.display.update()
        if player.collidelist(enemies) != -1:
            death()
        if not complete and frame == W // 64:
            complete = True
            player.x = 0
            player.y = H - 96
            frame = 0
        pygame.display.update()
        for e in pygame.event.get():
            if e.type == QUIT: quit()
            if e.type == KEYDOWN:
                if e.key == K_ESCAPE: quit()
                if e.key == K_LEFT: sidx = min(sidx + 1, 5)
                if e.key == K_RIGHT: sidx = max(sidx - 1, 0)
