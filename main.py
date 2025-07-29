import pygame
import sys
import time

# Khởi tạo
pygame.init()

# Kích thước
TILE_SIZE = 40
ROWS, COLS = 13, 15
WIDTH, HEIGHT = COLS * TILE_SIZE, ROWS * TILE_SIZE + 60
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Boom 2D")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

# Màu
WHITE = (255, 255, 255)
GRAY = (150, 150, 150)
DARKGRAY = (80, 80, 80)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

# Map (0: trống, 1: tường cứng, 2: gạch mềm)
map_data = [
    [1 if x % 2 == 1 and y % 2 == 1 else 2 for x in range(COLS)] for y in range(ROWS)
]
for y in range(ROWS):
    for x in range(COLS):
        if x == 0 or y == 0 or x == COLS - 1 or y == ROWS - 1:
            map_data[y][x] = 1

map_data[1][1] = map_data[1][2] = map_data[2][1] = 0

player_pos = [1, 1]
bombs = []
explosions = []
start_time = 0
game_started = False
game_over = False

# ---------------- Vẽ ----------------
def draw_map():
    for y in range(ROWS):
        for x in range(COLS):
            rect = pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE)
            if map_data[y][x] == 1:
                pygame.draw.rect(screen, DARKGRAY, rect)
            elif map_data[y][x] == 2:
                pygame.draw.rect(screen, GRAY, rect)
            else:
                pygame.draw.rect(screen, WHITE, rect)
            pygame.draw.rect(screen, BLACK, rect, 1)

def draw_player():
    x, y = player_pos
    rect = pygame.Rect(x*TILE_SIZE+5, y*TILE_SIZE+5, TILE_SIZE-10, TILE_SIZE-10)
    pygame.draw.rect(screen, GREEN, rect)

def place_bomb():
    x, y = player_pos
    bombs.append({"pos": (x, y), "time": pygame.time.get_ticks()})

def update_bombs():
    current_time = pygame.time.get_ticks()
    for bomb in bombs[:]:
        x, y = bomb["pos"]
        pygame.draw.ellipse(screen, RED, pygame.Rect(x*TILE_SIZE+10, y*TILE_SIZE+10, TILE_SIZE-20, TILE_SIZE-20))
        if current_time - bomb["time"] >= 2000:
            explode_bomb(x, y)
            bombs.remove(bomb)

def explode_bomb(x, y):
    directions = [(0,0), (1,0), (-1,0), (0,1), (0,-1)]
    for dx, dy in directions:
        nx, ny = x+dx, y+dy
        if 0 <= nx < COLS and 0 <= ny < ROWS:
            if map_data[ny][nx] == 2:
                map_data[ny][nx] = 0
            explosions.append({"pos": (nx, ny), "time": pygame.time.get_ticks()})

def update_explosions():
    current_time = pygame.time.get_ticks()
    for exp in explosions[:]:
        x, y = exp["pos"]
        rect = pygame.Rect(x*TILE_SIZE+5, y*TILE_SIZE+5, TILE_SIZE-10, TILE_SIZE-10)
        pygame.draw.rect(screen, ORANGE, rect)
        if current_time - exp["time"] >= 500:
            explosions.remove(exp)

def draw_ui():
    if game_started and not game_over:
        time_left = max(0, 60 - int((pygame.time.get_ticks() - start_time)/1000))
        timer_text = font.render(f"Time: {time_left}s", True, BLACK)
        screen.blit(timer_text, (10, HEIGHT - 50))

def show_start_screen():
    screen.fill(WHITE)
    title = font.render("BOOM 2D", True, BLACK)
    start_button = font.render("Click to START", True, RED)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 60))
    screen.blit(start_button, (WIDTH//2 - start_button.get_width()//2, HEIGHT//2))
    pygame.display.flip()

def show_game_over():
    over_text = font.render("You lose! click to play again", True, RED)
    screen.blit(over_text, (WIDTH//2 - over_text.get_width()//2, HEIGHT//2))
    pygame.display.flip()

# ---------------- MAIN LOOP ------------------
while True:
    clock.tick(180)

    if not game_started:
        show_start_screen()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                game_started = True
                start_time = pygame.time.get_ticks()
    elif game_over:
        show_game_over()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                player_pos = [1, 1]
                bombs.clear()
                explosions.clear()
                map_data = [[1 if x % 2 == 1 and y % 2 == 1 else 2 for x in range(COLS)] for y in range(ROWS)]
                for y in range(ROWS):
                    for x in range(COLS):
                        if x == 0 or y == 0 or x == COLS - 1 or y == ROWS - 1:
                            map_data[y][x] = 1
                map_data[1][1] = map_data[1][2] = map_data[2][1] = 0
                game_over = False
                start_time = pygame.time.get_ticks()
    else:
        screen.fill(WHITE)
        draw_map()
        draw_player()
        update_bombs()
        update_explosions()
        draw_ui()

        # Kiểm tra trùng với bom nổ
        for exp in explosions:
            if tuple(player_pos) == exp["pos"]:
                game_over = True

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        x, y = player_pos
        if keys[pygame.K_LEFT] and map_data[y][x-1] == 0:
            player_pos[0] -= 1
            time.sleep(0.1)
        if keys[pygame.K_RIGHT] and map_data[y][x+1] == 0:
            player_pos[0] += 1
            time.sleep(0.1)
        if keys[pygame.K_UP] and map_data[y-1][x] == 0:
            player_pos[1] -= 1
            time.sleep(0.1)
        if keys[pygame.K_DOWN] and map_data[y+1][x] == 0:
            player_pos[1] += 1
            time.sleep(0.1)
        if keys[pygame.K_SPACE]:
            if all(b["pos"] != tuple(player_pos) for b in bombs):
                place_bomb()
            time.sleep(0.2)
