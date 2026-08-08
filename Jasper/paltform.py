import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Platformer with Tiny Grid Snow")
clock = pygame.time.Clock()
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

# Tile settings
TILE_SIZE = 40
GRID_WIDTH = WIDTH // TILE_SIZE
GRID_HEIGHT = HEIGHT // TILE_SIZE
SNOW_SIZE = TILE_SIZE / 100  # 1/100th of a tile

# Player settings
player_speed = 5
jump_power = 15
gravity = 0.8

# Grid: 0 = empty, 1 = platform, 2 = snow
grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

# Groups
falling_snow = pygame.sprite.Group()
blue_dots = pygame.sprite.Group()
platforms = pygame.sprite.Group()
player_group = pygame.sprite.GroupSingle()

# Snow particle class
class SnowParticle(pygame.sprite.Sprite):
    def __init__(self, x_cell, y_pixel):
        super().__init__()
        self.image = pygame.Surface((SNOW_SIZE, SNOW_SIZE))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect(center=(x_cell*TILE_SIZE + TILE_SIZE/2, y_pixel))
        self.speed = random.uniform(1,3)
        self.x_cell = min(max(0, x_cell), GRID_WIDTH-1)

    def update(self):
        self.rect.y += self.speed
        y_cell_below = int(self.rect.bottom // TILE_SIZE)
        if y_cell_below >= GRID_HEIGHT:
            y_cell_below = GRID_HEIGHT - 1

        if grid[y_cell_below][self.x_cell] != 0:
            # Snap to top of cell
            self.rect.bottom = y_cell_below * TILE_SIZE
            # Prevent negative index
            settle_y = max(0, y_cell_below - 1)
            grid[settle_y][self.x_cell] = 2
            self.kill()

# Platform class
class Platform(pygame.sprite.Sprite):
    def __init__(self, x_cell, y_cell):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect(topleft=(x_cell*TILE_SIZE, y_cell*TILE_SIZE))
        grid[y_cell][x_cell] = 1

# Blue dot explosion
class BlueDot(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5,5))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect(center=(x,y))
        self.vel_x = random.randint(-5,5)
        self.vel_y = random.randint(-5,0)

    def update(self):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        self.vel_y += 0.5
        if self.rect.top > HEIGHT:
            self.kill()

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(RED)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.counter = 100
        self.alive = True

    def update(self, platforms):
        if not self.alive:
            return

        keys = pygame.key.get_pressed()
        self.vel_x = 0
        if keys[pygame.K_LEFT]:
            self.vel_x = -player_speed
        if keys[pygame.K_RIGHT]:
            self.vel_x = player_speed
        if keys[pygame.K_UP] and self.on_ground:
            self.vel_y = -jump_power

        self.vel_y += gravity

        # Horizontal collision
        self.rect.x += self.vel_x
        for p in platforms:
            if self.rect.colliderect(p.rect):
                if self.vel_x > 0:
                    self.rect.right = p.rect.left
                elif self.vel_x < 0:
                    self.rect.left = p.rect.right

        # Vertical collision
        self.rect.y += self.vel_y
        self.on_ground = False
        for p in platforms:
            if self.rect.colliderect(p.rect):
                if self.vel_y > 0:
                    self.rect.bottom = p.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:
                    self.rect.top = p.rect.bottom
                    self.vel_y = 0

        # Permanent death by counter
        if self.counter <= 0:
            self.explode(permanent=True)

        # Respawn if falling off bottom
        if self.rect.top > HEIGHT:
            self.respawn()

    def explode(self, permanent=False):
        for _ in range(50):
            blue_dots.add(BlueDot(self.rect.centerx, self.rect.centery))
        if permanent:
            self.alive = False

    def respawn(self):
        spawn_x, spawn_y = find_spawn(current_level)
        self.rect.topleft = (spawn_x, spawn_y)
        self.vel_x = 0
        self.vel_y = 0

# Levels (# = platform, space = air)
levels = [
    [
        "                                ",
        "                                ",
        "                                ",
        "                                ",
        "                                ",
        "                                ",
        "                                ",
        "                                ",
        "                                ",
        "############       ############ ",
        "############       ############ ",
        "############       ############ ",
    ]
]

current_level = 0

# Load level
def load_level(level_index):
    platforms.empty()
    y = 0
    for row in levels[level_index]:
        x = 0
        for char in row:
            if char == "#":
                platforms.add(Platform(x, y))
            x += 1
        y += 1

# Safe spawn
def find_spawn(level_index):
    level = levels[level_index]
    for y, row in enumerate(level):
        for x, char in enumerate(row):
            if char == " ":
                return x*TILE_SIZE, y*TILE_SIZE
    return WIDTH//2, TILE_SIZE

# Load first level and spawn player
load_level(current_level)
spawn_x, spawn_y = find_spawn(current_level)
player = Player(spawn_x, spawn_y)
player_group.add(player)

# Camera
camera_y = 0

# Counter event (1 second)
counter_event = pygame.USEREVENT + 1
pygame.time.set_timer(counter_event, 1000)

# Main loop
running = True
while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == counter_event:
            if player.alive:
                player.counter -= 1

    # Determine highest occupied cell for snow spawning
    occupied_y = [y for y in range(GRID_HEIGHT) for x in range(GRID_WIDTH) if grid[y][x] != 0]
    highest_y = min(occupied_y) if occupied_y else GRID_HEIGHT
    spawn_y_pixel = highest_y*TILE_SIZE - TILE_SIZE*10

    # Spawn a few falling snow per frame
    for _ in range(2):
        x_cell = random.randint(0, GRID_WIDTH-1)
        falling_snow.add(SnowParticle(x_cell, spawn_y_pixel))

    # Update
    player_group.update(platforms)
    falling_snow.update()
    blue_dots.update()

    # Camera follows player
    camera_y = -player.rect.centery + HEIGHT//2

    # Draw
    screen.fill(BLACK)
    # Draw settled snow
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if grid[y][x] == 2:
                rect = pygame.Rect(x*TILE_SIZE, y*TILE_SIZE + camera_y, SNOW_SIZE, SNOW_SIZE)
                screen.fill(WHITE, rect)
    # Draw platforms
    for plat in platforms:
        screen.blit(plat.image, (plat.rect.x, plat.rect.y + camera_y))
    # Draw falling snow
    for snow in falling_snow:
        screen.blit(snow.image, (snow.rect.x, snow.rect.y + camera_y))
    # Draw blue dots
    for dot in blue_dots:
        screen.blit(dot.image, (dot.rect.x, dot.rect.y + camera_y))
    # Draw player
    if player.alive:
        screen.blit(player.image, (player.rect.x, player.rect.y + camera_y))

    # HUD
    font = pygame.font.SysFont(None, 36)
    counter_surf = font.render(f"Counter: {player.counter}", True, WHITE)
    screen.blit(counter_surf, (10,10))
    level_surf = font.render(f"Level: {current_level+1}", True, WHITE)
    screen.blit(level_surf, (10,40))

    pygame.display.flip()
