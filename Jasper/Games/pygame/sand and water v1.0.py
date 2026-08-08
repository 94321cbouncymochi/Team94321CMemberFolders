import pygame
import sys
import random

# ---------- CONFIG ----------
CELL = 5
W, H = 160, 120
SCREEN = (W * CELL, H * CELL)

EMPTY = 0
SAND = 1
WATER = 2
STONE = 3
OIL = 4
STEAM = 5
ACID = 6
WOOD = 7
LAVA = 8

COLORS = {
    EMPTY: (0, 0, 0),
    SAND: (194, 178, 128),
    WATER: (64, 164, 223),
    STONE: (100, 100, 100),
    OIL: (60, 60, 40),
    STEAM: (200, 200, 200),
    ACID: (0, 255, 0),
    WOOD: (139, 69, 19),
    LAVA: (255, 80, 0),
}

pygame.init()
screen = pygame.display.set_mode(SCREEN)
pygame.display.set_caption("Falling Sand Sim")
clock = pygame.time.Clock()

grid = [[EMPTY for _ in range(H)] for _ in range(W)]
current = SAND

def in_bounds(x, y):
    return 0 <= x < W and 0 <= y < H

def swap(x1, y1, x2, y2):
    grid[x1][y1], grid[x2][y2] = grid[x2][y2], grid[x1][y1]

# ---------- SIM ----------
def update():
    for y in range(H - 2, -1, -1):
        for x in range(W):
            cell = grid[x][y]

            # ----- SAND -----
            if cell == SAND:
                for dx in [0, -1, 1]:
                    nx, ny = x + dx, y + 1
                    if in_bounds(nx, ny) and grid[nx][ny] in (EMPTY, WATER, OIL):
                        swap(x, y, nx, ny)
                        break

            # ----- WATER -----
            elif cell == WATER:
                dirs = [(0,1), (-1,1), (1,1)]
                side = [(-1,0), (1,0)]
                random.shuffle(side)
                dirs += side

                for dx, dy in dirs:
                    nx, ny = x + dx, y + dy
                    if in_bounds(nx, ny) and grid[nx][ny] in (EMPTY, OIL):
                        swap(x, y, nx, ny)
                        break

            # ----- OIL -----
            elif cell == OIL:
                # actively rise above water
                if in_bounds(x, y - 1) and grid[x][y - 1] == WATER:
                    swap(x, y, x, y - 1)
                else:
                    side = [(-1,0), (1,0)]
                    random.shuffle(side)
                    for dx, dy in [(0,1)] + side:
                        nx, ny = x + dx, y + dy
                        if in_bounds(nx, ny) and grid[nx][ny] == EMPTY:
                            swap(x, y, nx, ny)
                            break

            # ----- WOOD (floats) -----
            elif cell == WOOD:
                for dx in [0, -1, 1]:
                    nx, ny = x + dx, y + 1
                    if in_bounds(nx, ny) and grid[nx][ny] in (EMPTY, OIL):
                        swap(x, y, nx, ny)
                        break

            # ----- STEAM -----
            elif cell == STEAM:
                if random.random() < 0.2:
                    for dx, dy in [(0,-1), (-1,-1), (1,-1)]:
                        nx, ny = x + dx, y + dy
                        if in_bounds(nx, ny) and grid[nx][ny] == EMPTY:
                            swap(x, y, nx, ny)
                            break
                if random.random() < 0.01:
                    grid[x][y] = EMPTY

            # ----- ACID -----
            elif cell == ACID:
                dirs = [(0,1), (-1,0), (1,0)]
                random.shuffle(dirs)
                for dx, dy in dirs:
                    nx, ny = x + dx, y + dy
                    if in_bounds(nx, ny):
                        if grid[nx][ny] == SAND and random.random() < 0.05:
                            grid[nx][ny] = EMPTY
                        elif grid[nx][ny] == EMPTY:
                            swap(x, y, nx, ny)
                            break

            # ----- LAVA -----
            elif cell == LAVA:
                for dx, dy in [(0,1), (-1,1), (1,1)]:
                    nx, ny = x + dx, y + dy
                    if in_bounds(nx, ny):
                        if grid[nx][ny] == WOOD:
                            grid[nx][ny] = STEAM
                        elif grid[nx][ny] in (EMPTY, WATER):
                            swap(x, y, nx, ny)
                            break

# ---------- DRAW ----------
def draw():
    for x in range(W):
        for y in range(H):
            pygame.draw.rect(
                screen,
                COLORS[grid[x][y]],
                (x * CELL, y * CELL, CELL, CELL),
            )

# ---------- LOOP ----------
running = True
while running:
    clock.tick(60)
    screen.fill((0, 0, 0))

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
        if e.type == pygame.KEYDOWN:
            if pygame.K_1 <= e.key <= pygame.K_8:
                current = e.key - pygame.K_0

    if pygame.mouse.get_pressed()[0]:
        mx, my = pygame.mouse.get_pos()
        gx, gy = mx // CELL, my // CELL
        if in_bounds(gx, gy):
            grid[gx][gy] = current

    update()
    draw()
    pygame.display.flip()

pygame.quit()
sys.exit()
