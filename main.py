import pygame
import sys
import random

# Khởi tạo pygame
pygame.init()

# Kích thước ô và số hàng/cột
TILE_SIZE = 40
ROWS = 15
COLS = 15
WIDTH = TILE_SIZE * COLS
HEIGHT = TILE_SIZE * ROWS

# Màu sắc
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
GREEN = (0, 255, 0)
ORANGE = (255, 165, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)

# Font
font = pygame.font.SysFont(None, 36)

# Tạo cửa sổ
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Boom 2D")

# Clock
clock = pygame.time.Clock()

# Thời gian
start_time = pygame.time.get_ticks()
win_time_used = None

# Thông số game
TIMER_LIMIT = 60  # giây
WIN_CONDITION = random.randint(10, 20)  # số hộp phải phá để thắng

# Trạng thái
menu = True
running = False
win = False
lose = False

# Vị trí người chơi
player_x = 1
player_y = 1

# Danh sách boom
bombs = []
bomb_timer = 3000  # ms
bomb_range = 1
explosions = []

# Số hộp đã phá
destroyed_boxes = 0

# Tạo bản đồ
def generate_map():
    map_data = []
    total_cells = ROWS * COLS
    total_boxes = random.randint(total_cells // 2, (total_cells * 3) // 4)
    box_count = 0
    for row in range(ROWS):
        line = []
        for col in range(COLS):
            if (row, col) in [(1, 1), (1, 2), (2, 1)]:
                line.append(0)
            else:
                rand = random.randint(1, 100)
                if rand <= 10:
                    line.append(1)  # tường cứng
                elif rand <= 80 and box_count < total_boxes:
                    line.append(2)  # hộp phá được
                    box_count += 1
                else:
                    line.append(0)
        map_data.append(line)
    return map_data

map_data = generate_map()
map_data[player_y][player_x] = 0

def draw_map():
    for y in range(ROWS):
        for x in range(COLS):
            rect = pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE)
            if map_data[y][x] == 1:
                pygame.draw.rect(screen, GRAY, rect)
            elif map_data[y][x] == 2:
                pygame.draw.rect(screen, ORANGE, rect)
            else:
                pygame.draw.rect(screen, (50, 50, 50), rect)
            pygame.draw.rect(screen, BLACK, rect, 1)

def draw_player():
    rect = pygame.Rect(player_x*TILE_SIZE, player_y*TILE_SIZE, TILE_SIZE, TILE_SIZE)
    pygame.draw.rect(screen, GREEN, rect)

def draw_bombs():
    current_time = pygame.time.get_ticks()
    for bomb in bombs[:]:
        rect = pygame.Rect(bomb['x']*TILE_SIZE, bomb['y']*TILE_SIZE, TILE_SIZE, TILE_SIZE)
        pygame.draw.circle(screen, RED, rect.center, TILE_SIZE//3)
        if current_time - bomb['time'] > bomb_timer:
            explode_bomb(bomb)
            bombs.remove(bomb)

def explode_bomb(bomb):
    global destroyed_boxes, lose
    explosion_cells = []
    for dx, dy in [(0,0), (1,0), (-1,0), (0,1), (0,-1)]:
        bx = bomb['x'] + dx
        by = bomb['y'] + dy
        if 0 <= bx < COLS and 0 <= by < ROWS:
            explosion_cells.append((bx, by))
            explosions.append({'x': bx, 'y': by, 'time': pygame.time.get_ticks()})
            if map_data[by][bx] == 2:
                map_data[by][bx] = 0
                destroyed_boxes += 1

    # Kiểm tra thua NGAY LẬP TỨC nếu người chơi đứng trong vùng nổ
    for (bx, by) in explosion_cells:
        if player_x == bx and player_y == by:
            lose = True

def draw_explosions():
    current_time = pygame.time.get_ticks()
    for exp in explosions[:]:
        if current_time - exp['time'] <= 500:
            rect = pygame.Rect(exp['x']*TILE_SIZE, exp['y']*TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, YELLOW, rect)
        else:
            explosions.remove(exp)

def show_menu():
    screen.fill(BLACK)
    text = font.render("Press ENTER to Start", True, WHITE)
    screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2))
    pygame.display.flip()

def show_game_over():
    text = font.render("You LOSE! Click to play again", True, RED)
    screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2))
    pygame.display.flip()

def show_game_win():
    text = font.render("You WIN! Click to play again", True, GREEN)
    time_text = font.render(f"Time used: {win_time_used} seconds", True, RED)
    screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 30))
    screen.blit(time_text, (WIDTH//2 - time_text.get_width()//2, HEIGHT//2 + 10))
    pygame.display.flip()

# Main loop
while True:
    if menu:
        show_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                WIN_CONDITION = random.randint(10, 20)
                map_data = generate_map()
                menu = False
                running = True
                start_time = pygame.time.get_ticks()
                destroyed_boxes = 0
                player_x, player_y = 1, 1
                bombs.clear()
                explosions.clear()
                win = False
                lose = False
                win_time_used = None
    elif running:
        screen.fill(BLACK)
        draw_map()
        draw_player()
        draw_bombs()
        draw_explosions()

        elapsed = (pygame.time.get_ticks() - start_time) // 1000
        remaining = max(0, TIMER_LIMIT - elapsed)
        timer_text = font.render(f"Time: {remaining}", True, WHITE)
        screen.blit(timer_text, (10, 10))

        box_text = font.render(f"Destroyed: {destroyed_boxes}/{WIN_CONDITION}", True, ORANGE)
        screen.blit(box_text, (10, 50))

        if remaining == 0:
            lose = True
            running = False

        if destroyed_boxes >= WIN_CONDITION and not win:
            win = True
            win_time_used = elapsed
            running = False

        if lose:
            running = False

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    if player_x > 0 and map_data[player_y][player_x-1] != 1 and map_data[player_y][player_x-1] != 2:
                        player_x -= 1
                elif event.key == pygame.K_RIGHT:
                    if player_x < COLS-1 and map_data[player_y][player_x+1] != 1 and map_data[player_y][player_x+1] != 2:
                        player_x += 1
                elif event.key == pygame.K_UP:
                    if player_y > 0 and map_data[player_y-1][player_x] != 1 and map_data[player_y-1][player_x] != 2:
                        player_y -= 1
                elif event.key == pygame.K_DOWN:
                    if player_y < ROWS-1 and map_data[player_y+1][player_x] != 1 and map_data[player_y+1][player_x] != 2:
                        player_y += 1
                elif event.key == pygame.K_SPACE:
                    bombs.append({'x': player_x, 'y': player_y, 'time': pygame.time.get_ticks()})

        clock.tick(60)

    elif win:
        screen.fill(BLACK)
        draw_map()
        draw_player()
        show_game_win()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                menu = True
                win = False

    elif lose:
        screen.fill(BLACK)
        draw_map()
        draw_player()
        draw_explosions()
        show_game_over()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                menu = True
                lose = False
