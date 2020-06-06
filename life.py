import pygame
from pygame.locals import *
from pygame.rect import Rect
from random import randint

W, H = (40, 40)
PW = 16
cells = set()

def nbrs(x, y):
    yield x + 1, y + 1; yield x + 1, y; yield x + 1, y - 1
    yield x, y + 1;                     yield x, y - 1,
    yield x - 1, y + 1; yield x - 1, y; yield x - 1, y - 1

def life(cells):
    new = set()
    for x in range(W):
        for y in range(H):
            n = sum([(x_%W, y_%H) in cells for x_, y_ in nbrs(x, y)])
            if n == 3 or ( (x, y) in cells and n == 2 ):
                new.add((x%W, y%H))
    return new

def drawn_board(cells, col=(255, 255, 255)):
    surf = pygame.Surface((W*PW, H*PW))
    for x in range(W):
        for y in range(H):
            if (x, y) in cells:
                pygame.draw.rect(surf, col, Rect((x*PW, y*PW), (PW, PW)))
    return surf

if __name__ == "__main__":
    SCREEN = pygame.display.set_mode((W*PW, H*PW))
    pygame.display.set_caption("game of life")
    CLOCK = pygame.time.Clock()

    for n in range(W*H//3):
        cells.add((randint(0, W-1), randint(0, H-1)))
    col = (randint(0, 255), randint(0, 255), randint(0, 255))
    while True:
        for e in pygame.event.get():
            if e.type == QUIT: quit()
            if e.type == KEYDOWN and e.key == K_ESCAPE: quit()

        SCREEN.blit(drawn_board(cells, col), (0, 0))
        pygame.display.update()
        cells = life(cells)
        CLOCK.tick(15)
