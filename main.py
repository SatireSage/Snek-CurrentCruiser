import os

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import sys
import random

cache = {
    'images': {},
    'texts': {},
    'sounds': {}
}
MAX_FPS = 1000


def get_image(path):
    if path not in cache['images']:
        cache['images'][path] = pygame.image.load(path)
    return cache['images'][path]


def get_text(text, font, size, color):
    key = (text, font, size, color)
    if key not in cache['texts']:
        font_style_value = pygame.font.SysFont(font, size)
        cache['texts'][key] = font_style_value.render(text, True, color)
    return cache['texts'][key]


def get_sound(path):
    if path not in cache['sounds']:
        cache['sounds'][path] = pygame.mixer.Sound(path)
    return cache['sounds'][path]


pygame.init()
pygame.font.init()
pygame.mixer.init()
pygame.mouse.set_visible(False)

gameIcon = get_image('current_cruiser.png')
pygame.display.set_icon(gameIcon)

screen_info = pygame.display.Info()
SCREEN_WIDTH = screen_info.current_w
SCREEN_HEIGHT = screen_info.current_h
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption('Current Cruiser')
colors = {'white': (255, 255, 255), 'score': (255, 255, 102), 'black': (0, 0, 0),
          'bird': (233, 161, 78), 'pipe': (4, 136, 143), 'gray': (128, 128, 128)}
GRID_SIZE = 40
font = pygame.font.Font(pygame.font.get_default_font(), 24)


class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((SCREEN_WIDTH // 32, SCREEN_HEIGHT // 32))
        self.image.fill(colors['bird'])
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.gravity = 0.25
        self.velocity = 0

    def update(self):
        self.velocity += self.gravity
        self.rect.y += int(self.velocity)


class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(colors['pipe'])
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.crossed = False


def spawn_pipes():
    pipe_width = SCREEN_WIDTH // 10
    pipe_gap = SCREEN_HEIGHT // 4
    min_pipe_height = SCREEN_HEIGHT // 8
    max_pipe_height = SCREEN_HEIGHT // 2
    x = SCREEN_WIDTH
    height = random.randint(min_pipe_height, max_pipe_height)
    bottom_pipe = Pipe(x, height + pipe_gap, pipe_width, SCREEN_HEIGHT - height - pipe_gap)
    top_pipe = Pipe(x, 0, pipe_width, height)
    return bottom_pipe, top_pipe


def move_pipes(pipe_set, speed=2):
    for pipe in pipe_set:
        pipe.rect.x -= speed


def draw_grid(surface):
    for x in range(0, SCREEN_WIDTH, GRID_SIZE):
        pygame.draw.line(surface, colors['gray'], (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
        pygame.draw.line(surface, colors['gray'], (0, y), (SCREEN_WIDTH, y))


def draw_score(surface, score_value):
    score_text = font.render(f"Score: {score_value}", True, (255, 255, 255))
    surface.blit(score_text, (10, 10))


def draw_message(message, color):
    text = font.render(message, True, color)
    text_rect = text.get_rect()
    text_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    screen.blit(text, text_rect)


def print_previous_score(score):
    score_msg = font.render(f"Previous Score: {score}", True, colors['white'])
    score_rect = score_msg.get_rect()
    score_rect.center = (SCREEN_WIDTH // 2, (SCREEN_HEIGHT // 2) + 50)
    screen.blit(score_msg, score_rect)


def pause_game():
    paused = True
    draw_message("Game Paused. Press P to continue.", colors['white'])
    pygame.display.update()

    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = False


def main_menu(score):
    s = 'sounds'
    game_started = False
    pygame.mixer.music.load(os.path.join(s, 'theme.wav'))
    pygame.mixer.music.play(-1)
    while not game_started:
        screen.fill(colors['black'])

        draw_message("Press SPACE to start. Press Q to quit", colors['white'])
        print_previous_score(score)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                pygame.mixer.music.stop()
                game_started = True
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                pygame.quit()
                sys.exit()


def game_loop():
    bird = Bird(SCREEN_WIDTH // 2 - (SCREEN_WIDTH // 18) // 2, SCREEN_HEIGHT // 2 - (SCREEN_HEIGHT // 32) // 2)
    bird_group = pygame.sprite.Group()
    bird_group.add(bird)

    pipe_speed = 2
    pipes = spawn_pipes()
    pipe_group = pygame.sprite.Group()
    pipe_group.add(pipes)

    s = 'sounds'
    score = 0
    clock = pygame.time.Clock()
    pipe_spawn_timer = pygame.USEREVENT
    pygame.time.set_timer(pipe_spawn_timer, 1500)

    crash_sound = get_sound(os.path.join(s, 'hit.wav'))
    move_sound = get_sound(os.path.join(s, 'move.wav'))

    while True:
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    pygame.mixer.Sound.play(move_sound)
                    bird.velocity = -7
                if event.key == pygame.K_p:  # Pause the game when 'P' is pressed
                    pause_game()
            if event.type == pipe_spawn_timer:
                pipes = spawn_pipes()
                pipe_group.add(pipes)

        bird_group.update()
        move_pipes(pipe_group, pipe_speed)

        for pipe in pipe_group.sprites():
            if pipe.rect.bottom < SCREEN_HEIGHT and pipe.rect.right < bird.rect.left:
                if not pipe.crossed:
                    score += 1
                    pipe.crossed = True

        if pygame.sprite.spritecollide(bird, pipe_group,
                                       False) or bird.rect.top < 0 or bird.rect.bottom > SCREEN_HEIGHT:
            pygame.mixer.Sound.play(crash_sound)
            return score

        draw_grid(screen)
        bird_group.draw(screen)
        pipe_group.draw(screen)
        draw_score(screen, score)
        pygame.display.flip()
        clock.tick(120)

        fps = int(clock.get_fps())
        pygame.display.set_caption(f"Flappy Bird - FPS: {fps}")


if __name__ == "__main__":
    score = 0
    while True:
        main_menu(score)
        score = game_loop()
