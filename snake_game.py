import pygame
import random
import sys

# scherm:
COLS, ROWS = 25, 25
CELL = 24
WIDTH  = COLS * CELL
HEIGHT = ROWS * CELL
PANEL  = 160
SPEED  = 100 

# kleuren
BG         = (10, 10, 15)
PANEL_BG   = (15, 15, 26)
BORDER     = (26, 26, 46)
GRID       = (255, 255, 255, 10)
SNAKE_HEAD = (0, 255, 136)
SNAKE_BODY = (0, 180, 90)
FOOD_COL   = (255, 60, 110)
TEXT_COL   = (200, 200, 255)
DIM_COL    = (74, 74, 106)
ACCENT     = (0, 255, 136)


def draw_rounded_rect(surf, color, rect, radius=4):
    pygame.draw.rect(surf, color, rect, border_radius=radius)


class Snake:
    def __init__(self):
        self.reset()

    def reset(self):
        self.body = [(12, 12), (11, 12), (10, 12)]
        self.dir = (1, 0)
        self.next_dir = (1, 0)
        self.score = 0
        self.alive = True

    def set_dir(self, d):
        if (d[0] + self.dir[0], d[1] + self.dir[1]) != (0, 0):
            self.next_dir = d

    def step(self, food_pos):
        self.dir = self.next_dir
        head = (self.body[0][0] + self.dir[0], self.body[0][1] + self.dir[1])

        if not (0 <= head[0] < COLS and 0 <= head[1] < ROWS):
            self.alive = False
            return False

        if head in self.body:
            self.alive = False
            return False

        self.body.insert(0, head)

        ate = head == food_pos
        if ate:
            self.score += 1
        else:
            self.body.pop()

        return ate


def place_food(snake_body):
    while True:
        pos = (random.randint(0, COLS - 1), random.randint(0, ROWS - 1))
        if pos not in snake_body:
            return pos


def draw_game(screen, snake, food, food_tick, best, font_big, font_med, font_small):
    screen.fill(BG)

    for x in range(COLS + 1):
        pygame.draw.line(screen, (255, 255, 255, 6), (x * CELL, 0), (x * CELL, HEIGHT))
    for y in range(ROWS + 1):
        pygame.draw.line(screen, (255, 255, 255, 6), (0, y * CELL), (WIDTH, y * CELL))

    pulse = abs((food_tick % 30) - 15) / 15
    glow_r = int(3 + pulse * 5)
    glow_surf = pygame.Surface((CELL * 2, CELL * 2), pygame.SRCALPHA)
    pygame.draw.circle(glow_surf, (*FOOD_COL, 60), (CELL, CELL), CELL // 2 + glow_r)
    screen.blit(glow_surf, (food[0] * CELL - CELL // 2, food[1] * CELL - CELL // 2))
    fp = 3
    draw_rounded_rect(screen, FOOD_COL,
        pygame.Rect(food[0]*CELL+fp, food[1]*CELL+fp, CELL-fp*2, CELL-fp*2), 3)

    n = len(snake.body)
    for i, (sx, sy) in enumerate(snake.body):
        is_head = (i == 0)
        t = 1 - i / n
        if is_head:
            color = SNAKE_HEAD
            p = 1
            r = 5
        else:
            g = int(80 + t * 100)
            color = (0, g, int(40 + t * 50))
            p = 2
            r = 2
        draw_rounded_rect(screen, color,
            pygame.Rect(sx*CELL+p, sy*CELL+p, CELL-p*2, CELL-p*2), r)

        if is_head:
            dx, dy = snake.dir
            cx, cy = sx * CELL + CELL // 2, sy * CELL + CELL // 2
            for s in [1, -1]:
                ex = cx + dx * 5 + (-dy) * 4 * s
                ey = cy + dy * 5 + dx * 4 * s
                pygame.draw.circle(screen, BG, (int(ex), int(ey)), 2)

    panel_x = WIDTH
    pygame.draw.rect(screen, PANEL_BG, pygame.Rect(panel_x, 0, PANEL, HEIGHT))
    pygame.draw.line(screen, BORDER, (panel_x, 0), (panel_x, HEIGHT), 1)

    def label(text, x, y):
        s = font_small.render(text, True, DIM_COL)
        screen.blit(s, (x, y))

    def value(text, x, y, color=ACCENT):
        s = font_big.render(text, True, color)
        screen.blit(s, (x, y))

    px = panel_x + 14
    label("SCORE", px, 20)
    value(str(snake.score), px, 38)

    label("BEST", px, 90)
    value(str(best), px, 108)

    label("BESTURING", px, 200)
    for i, line in enumerate(["↑↓←→ beweeg", "WASD beweeg", "P  pauze", "R  herstart", "Q  stoppen"]):
        s = font_small.render(line, True, DIM_COL)
        screen.blit(s, (px, 220 + i * 20))


def draw_overlay(screen, title, subtitle, font_title, font_med):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((10, 10, 15, 180))
    screen.blit(overlay, (0, 0))

    t = font_title.render(title, True, FOOD_COL)
    screen.blit(t, (WIDTH // 2 - t.get_width() // 2, HEIGHT // 2 - 60))

    s = font_med.render(subtitle, True, DIM_COL)
    screen.blit(s, (WIDTH // 2 - s.get_width() // 2, HEIGHT // 2))

    hint = font_med.render("DRUK ENTER OM TE SPELEN", True, ACCENT)
    screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT // 2 + 40))


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH + PANEL, HEIGHT))
    pygame.display.set_caption("Snake")
    clock = pygame.time.Clock()

    try:
        font_title = pygame.font.SysFont("Courier New", 48, bold=True)
        font_big   = pygame.font.SysFont("Courier New", 32, bold=True)
        font_med   = pygame.font.SysFont("Courier New", 18)
        font_small = pygame.font.SysFont("Courier New", 13)
    except:
        font_title = pygame.font.SysFont(None, 48)
        font_big   = pygame.font.SysFont(None, 32)
        font_med   = pygame.font.SysFont(None, 20)
        font_small = pygame.font.SysFont(None, 14)

    snake = Snake()
    food  = place_food(snake.body)
    best  = 0

    STATE_MENU   = "menu"
    STATE_PLAY   = "play"
    STATE_PAUSE  = "pause"
    STATE_OVER   = "over"
    state = STATE_MENU

    step_timer = 0
    food_tick  = 0

    while True:
        dt = clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_q,):
                    pygame.quit(); sys.exit()

                if state == STATE_MENU:
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        snake.reset()
                        food = place_food(snake.body)
                        step_timer = 0
                        state = STATE_PLAY

                elif state == STATE_PLAY:
                    if event.key == pygame.K_UP    or event.key == pygame.K_w: snake.set_dir((0, -1))
                    if event.key == pygame.K_DOWN  or event.key == pygame.K_s: snake.set_dir((0,  1))
                    if event.key == pygame.K_LEFT  or event.key == pygame.K_a: snake.set_dir((-1, 0))
                    if event.key == pygame.K_RIGHT or event.key == pygame.K_d: snake.set_dir(( 1, 0))
                    if event.key == pygame.K_p: state = STATE_PAUSE
                    if event.key == pygame.K_r:
                        snake.reset(); food = place_food(snake.body)
                        step_timer = 0; state = STATE_PLAY

                elif state == STATE_PAUSE:
                    if event.key == pygame.K_p: state = STATE_PLAY
                    if event.key == pygame.K_r:
                        snake.reset(); food = place_food(snake.body)
                        step_timer = 0; state = STATE_PLAY

                elif state == STATE_OVER:
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_r):
                        snake.reset(); food = place_food(snake.body)
                        step_timer = 0; state = STATE_PLAY
                    if event.key == pygame.K_m:
                        state = STATE_MENU

        if state == STATE_PLAY:
            step_timer += dt
            food_tick += 1

            if step_timer >= SPEED:
                step_timer -= SPEED
                ate = snake.step(food)
                if ate:
                    food = place_food(snake.body)
                    best = max(best, snake.score)
                if not snake.alive:
                    state = STATE_OVER

        draw_game(screen, snake, food, food_tick, best, font_big, font_med, font_small)

        if state == STATE_MENU:
            draw_overlay(screen, "SNAKE", "Retro Edition", font_title, font_med)
        elif state == STATE_PAUSE:
            draw_overlay(screen, "PAUZE", "Druk P om verder te gaan", font_title, font_med)
        elif state == STATE_OVER:
            draw_overlay(screen, "GAME OVER",
                f"Score: {snake.score}   Best: {best}   |   M = menu", font_title, font_med)

        pygame.display.flip()


if __name__ == "__main__":
    main()