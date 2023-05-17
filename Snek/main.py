import os
import random
import sys
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
from pygame.locals import *

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

gameIcon = get_image('snek.png')
pygame.display.set_icon(gameIcon)

colors = {'white': (255, 255, 255), 'yellow': (255, 255, 102), 'black': (0, 0, 0),
          'body': (233, 161, 78), 'food': (4, 136, 143), 'gray': (128, 128, 128)}

GRID_SIZE = 40
screen_info = pygame.display.Info()
max_width = screen_info.current_w // GRID_SIZE * GRID_SIZE
max_height = screen_info.current_h // GRID_SIZE * GRID_SIZE

SCREEN_WIDTH = max_width
SCREEN_HEIGHT = max_height

GRID_DIM = (SCREEN_WIDTH // GRID_SIZE, SCREEN_HEIGHT // GRID_SIZE)

WINDOW = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption('Snek')

font_style = pygame.font.SysFont("Aerial", 30)


def draw_message(msg, color):
    message = get_text(msg, "Aerial", 30, color)
    message_rect = message.get_rect()
    message_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    WINDOW.blit(message, message_rect)


def draw_grid(surface):
    for x in range(0, SCREEN_WIDTH, GRID_SIZE):
        pygame.draw.line(surface, colors['gray'], (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
        pygame.draw.line(surface, colors['gray'], (0, y), (SCREEN_WIDTH, y))


def reset_snake():
    positions = [(200, 200), (210, 200), (220, 200)]
    direction = (GRID_SIZE, 0)
    return positions, direction, len(positions)


def check_snake_collision(snake_positions):
    head = snake_positions[0]
    return head in snake_positions[1:]


def check_wall_collision(head_position):
    x, y = head_position
    return x < 0 or x >= SCREEN_WIDTH or y < 0 or y >= SCREEN_HEIGHT


def move_snake(positions, direction):
    head_x, head_y = positions[0]
    dx, dy = direction
    new_head = (head_x + dx, head_y + dy)
    positions = [new_head] + positions[:-1]

    return positions, direction, len(positions)


def grow_snake(positions, direction):
    tail_x, tail_y = positions[-1]
    dx, dy = direction
    new_tail = ((tail_x - dx) % SCREEN_WIDTH, (tail_y - dy) % SCREEN_HEIGHT)
    positions.append(new_tail)
    return positions, len(positions)


def respawn_food(snake_positions):
    while True:
        food_position = random.randint(0, GRID_DIM[0] - 1) * GRID_SIZE, random.randint(0, GRID_DIM[1] - 1) * GRID_SIZE
        if food_position not in snake_positions:
            return food_position


def draw_food(food_position):
    food_rect = pygame.Rect(food_position[0], food_position[1], GRID_SIZE, GRID_SIZE)
    pygame.draw.rect(WINDOW, colors['food'], food_rect)


def draw_snake(snake_positions):
    for i, position in enumerate(snake_positions):
        color = colors['yellow'] if i == 0 else colors['body']
        snake_rect = pygame.Rect(position[0], position[1], GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(WINDOW, color, snake_rect)

        if i == 0:
            eye_size = GRID_SIZE // 4
            eye_offset_x = GRID_SIZE // 4
            eye_offset_y = GRID_SIZE // 4

            left_eye = pygame.Rect(position[0] + eye_offset_x, position[1] + eye_offset_y, eye_size, eye_size)
            right_eye = pygame.Rect(position[0] + eye_offset_x * 3, position[1] + eye_offset_y, eye_size, eye_size)
            pygame.draw.rect(WINDOW, colors['black'], left_eye)
            pygame.draw.rect(WINDOW, colors['black'], right_eye)


def print_previous_score(score):
    score_msg = font_style.render(f"Previous Score: {score}", True, colors['white'])
    score_rect = score_msg.get_rect()
    score_rect.center = (SCREEN_WIDTH // 2, (SCREEN_HEIGHT // 2) + 50)
    WINDOW.blit(score_msg, score_rect)


def handle_key_presses(direction, move_sound, sound_played):
    pressed_keys = pygame.key.get_pressed()
    if pressed_keys[K_UP] or pressed_keys[K_w]:
        if direction != (0, GRID_SIZE):
            if not sound_played:
                pygame.mixer.Sound.play(move_sound)
                sound_played = True
            direction = (0, -GRID_SIZE)
    elif pressed_keys[K_DOWN] or pressed_keys[K_s]:
        if direction != (0, -GRID_SIZE):
            if not sound_played:
                pygame.mixer.Sound.play(move_sound)
                sound_played = True
            direction = (0, GRID_SIZE)
    elif pressed_keys[K_LEFT] or pressed_keys[K_a]:
        if direction != (GRID_SIZE, 0):
            if not sound_played:
                pygame.mixer.Sound.play(move_sound)
                sound_played = True
            direction = (-GRID_SIZE, 0)
    elif pressed_keys[K_RIGHT] or pressed_keys[K_d]:
        if direction != (-GRID_SIZE, 0):
            if not sound_played:
                pygame.mixer.Sound.play(move_sound)
                sound_played = True
            direction = (GRID_SIZE, 0)
    else:
        sound_played = False
    return direction, sound_played


def game_loop():
    s = 'sounds'
    snake_positions, direction, length = reset_snake()
    food_position = respawn_food(snake_positions)

    clock = pygame.time.Clock()
    snake_speed = 7
    update_snake_event = pygame.USEREVENT + 1
    pygame.time.set_timer(update_snake_event, int(1000 // snake_speed))

    pygame.mixer.music.load(os.path.join(s, 'theme.wav'))
    pygame.mixer.music.play(-1)
    crash_sound = get_sound(os.path.join(s, 'hit.wav'))
    move_sound = get_sound(os.path.join(s, 'move.wav'))
    eat_sound = get_sound(os.path.join(s, 'score.wav'))

    game_started = False
    sound_played = False
    score = 0

    grid_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    grid_surface.fill(colors['black'])
    draw_grid(grid_surface)

    paused = False

    while True:
        if not game_started:
            WINDOW.fill(colors['black'])
            snake_positions, direction, length = reset_snake()
            food_position = respawn_food(snake_positions)

            clock = pygame.time.Clock()
            snake_speed = 7
            pygame.time.set_timer(update_snake_event, int(1000 // snake_speed))

            draw_message("Press SPACE to start. Press Q to quit", colors['white'])
            print_previous_score(score)
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == KEYDOWN and event.key == K_SPACE:
                    pygame.mixer.music.stop()
                    game_started = True
                elif event.type == KEYDOWN and event.key == K_q:
                    pygame.quit()
                    sys.exit()
        else:
            for event in pygame.event.get():
                if event.type == QUIT:
                    return
                elif event.type == KEYDOWN and event.key == K_p:
                    paused = not paused
                    if paused:
                        pygame.mixer.music.pause()
                    else:
                        pygame.mixer.music.unpause()
                elif not paused and event.type == update_snake_event:
                    snake_positions, direction, length = move_snake(snake_positions, direction)

                    if check_snake_collision(snake_positions) or check_wall_collision(snake_positions[0]):
                        pygame.mixer.Sound.play(crash_sound)
                        game_started = False
                        pygame.mixer.music.play(-1)
                        continue

                    if snake_positions[0] == food_position:
                        pygame.mixer.Sound.play(eat_sound)
                        snake_positions, length = grow_snake(snake_positions, direction)
                        food_position = respawn_food(snake_positions)
                        snake_speed += 0.1
                        pygame.time.set_timer(update_snake_event, int(1000 // snake_speed))

            if not paused:
                direction, sound_played = handle_key_presses(direction, move_sound, sound_played)
                WINDOW.blit(grid_surface, (0, 0))
                draw_snake(snake_positions)
                draw_food(food_position)
                score = length - 3
                pygame.display.flip()

            else:
                draw_message("Game Paused. Press P to continue.", colors['white'])
                pygame.display.flip()

        clock.tick(MAX_FPS)


if __name__ == "__main__":
    game_loop()
