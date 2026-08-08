import pygame, sys, random, time, json, os, math
pygame.init()

# Screen
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fishing Tycoon - Casting Bobber")

# Colors
WHITE, BLACK = (255,255,255), (0,0,0)
BLUE, DARK_BLUE = (50,150,255), (30,100,200)
GREEN, YELLOW = (50,205,50), (255,230,100)
RED, BROWN = (255,0,0), (101,67,33)
GRAY = (180,180,180)
LIGHT_BLUE = (100,180,255)

# Fonts
font = pygame.font.SysFont(None, 36)

# Save/load
save_file = "save_data.json"
money = 0
if os.path.exists(save_file):
    with open(save_file, "r") as f:
        money = json.load(f).get("money",0)

# Game vars
money, fishing, fish_ready = money, False, False
fish_timer, reaction_timer = 0, 0
current_fish = None
button_pressed = False

# Rod & bobber
rod_x, rod_y = WIDTH//2, HEIGHT//2 - 150
bobber_x, bobber_y = rod_x, rod_y
rod_state = "up"  # up, casting, floating, sinking, wait, caught
bobber_velocity = 0
bobber_accel = 0.2
bobber_max_sink = 150
bobber_cast_speed = -12

# Water
water_y = HEIGHT//2 + 50
wave_amplitude = 5
wave_speed = 0.05
wave_phase = 0

# Fish types
fish_types = [
    {"name":"Salmon","rarity":1,"base_price":10},
    {"name":"Trout","rarity":2,"base_price":20},
    {"name":"Golden Fish","rarity":5,"base_price":100}
]

# Buttons
fish_button = pygame.Rect(WIDTH//2 - 300, HEIGHT-150, 200,100)
sell_button = pygame.Rect(WIDTH//2 + 100, HEIGHT-150, 200,100)
clock = pygame.time.Clock()

def save_game(): 
    with open(save_file,"w") as f: json.dump({"money":money},f)

def start_fishing():
    global fishing, fish_ready, fish_timer, rod_state, bobber_y, bobber_velocity
    fishing = True
    fish_ready=False
    rod_state="casting"
    bobber_y = rod_y
    bobber_velocity = bobber_cast_speed
    fish_timer = time.time() + random.randint(7,10)

def spawn_fish():
    global current_fish, reaction_timer, rod_state
    fish = random.choice(fish_types)
    size=random.randint(1,10)
    fish["size"]=size
    fish["price"]=fish["base_price"]*size*fish["rarity"]
    current_fish=fish
    reaction_timer=time.time()+random.uniform(2,3)
    rod_state="sinking"

while True:
    screen.fill(LIGHT_BLUE)
    mx,my = pygame.mouse.get_pos()

    # Water waves
    wave_phase += wave_speed
    for x in range(0, WIDTH, 2):
        y = water_y + math.sin(wave_phase + x*0.05) * wave_amplitude
        pygame.draw.line(screen, BLUE, (x, y), (x, HEIGHT))

    # Buttons
    # Fishing button: greyed out if fishing, shows pressed when clicked
    if fishing and rod_state not in ["wait","caught"]:
        pygame.draw.rect(screen, GRAY, fish_button, border_radius=8)
    elif button_pressed:
        pygame.draw.rect(screen, YELLOW, fish_button, border_radius=8)
    else:
        pygame.draw.rect(screen, DARK_BLUE, fish_button, border_radius=8)
    screen.blit(font.render("Fish!",True,BLACK),(fish_button.x+50,fish_button.y+30))

    # Sell button
    pygame.draw.rect(screen, GREEN if current_fish else GRAY, sell_button, border_radius=8)
    screen.blit(font.render("Sell Fish",True,BLACK),(sell_button.x+30,sell_button.y+30))

    # Money
    screen.blit(font.render(f"Money: ${money}",True,BLACK),(20,20))

    # Rod
    pygame.draw.line(screen,BROWN,(rod_x,rod_y),(bobber_x,bobber_y),6)

    # Bobber physics
    if rod_state=="casting":
        bobber_velocity += bobber_accel
        bobber_y += bobber_velocity
        if bobber_y >= water_y - 15:
            bobber_y = water_y - 15
            rod_state = "floating"
            bobber_velocity = 0

    elif rod_state=="floating":
        bobber_y = water_y - 15 + math.sin(time.time()*5)*2

    elif rod_state=="sinking":
        bobber_velocity += bobber_accel
        bobber_y += bobber_velocity
        if bobber_y >= water_y - 15 + bobber_max_sink:
            rod_state="wait"
            bobber_velocity=0

    elif rod_state=="up":
        bobber_y = rod_y
        bobber_velocity = 0

    pygame.draw.circle(screen, RED, (rod_x,int(bobber_y)),15)

    # Display caught fish info
    if current_fish and rod_state in ["wait","caught"]:
        screen.blit(font.render(f"{current_fish['name']} Size:{current_fish['size']}",True,BLACK),(WIDTH//2-150,100))

    # Fishing timer
    if fishing and not fish_ready and time.time()>=fish_timer:
        fish_ready=True; spawn_fish(); fishing=False

    if rod_state=="wait" and time.time()>=reaction_timer:
        # Missed fish
        current_fish=None; rod_state="up"; start_fishing()

    # Events
    button_pressed=False
    for e in pygame.event.get():
        if e.type==pygame.QUIT: save_game(); pygame.quit(); sys.exit()
        if e.type==pygame.MOUSEBUTTONDOWN:
            # Start fishing
            if fish_button.collidepoint((mx,my)) and not fishing and rod_state=="up":
                start_fishing(); button_pressed=True
            # Sell fish
            if sell_button.collidepoint((mx,my)) and current_fish and rod_state=="caught":
                money+=current_fish["price"]; current_fish=None; rod_state="up"; save_game()
            # Catch fish
            if current_fish and rod_state=="wait":
                rod_state="caught"

    pygame.display.update()
    clock.tick(60)