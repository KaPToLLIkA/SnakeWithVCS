import pygame
import random
import sys

from git import Git
from state import State, frame_size_y, frame_size_x

difficulty = 10

check_errors = pygame.init()
if check_errors[1] > 0:
    print(f'[!] Had {check_errors[1]} errors when initialising game, exiting...')
    sys.exit(-1)
else:
    print('[+] Game successfully initialised')


git = Git()
git.start()


class Colors:
    black = pygame.Color(0, 0, 0)
    white = pygame.Color(255, 255, 255)
    red = pygame.Color(255, 0, 0)
    green = pygame.Color(0, 255, 0)
    blue = pygame.Color(0, 0, 255)


class Game:
    pygame.display.set_caption('Snake Eater')
    game_window = pygame.display.set_mode((frame_size_x, frame_size_y))
    fps_controller = pygame.time.Clock()

    @staticmethod
    def proc_input():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                State.exit = True
                pygame.display.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == ord('w'):
                    if State.direction != 'D':
                        State.change_to = 'U'
                if event.key == pygame.K_DOWN or event.key == ord('s'):
                    if State.direction != 'U':
                        State.change_to = 'D'
                if event.key == pygame.K_LEFT or event.key == ord('a'):
                    if State.direction != 'R':
                        State.change_to = 'L'
                if event.key == pygame.K_RIGHT or event.key == ord('d'):
                    if State.direction != 'L':
                        State.change_to = 'R'
                if event.key == pygame.K_ESCAPE:
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
                if event.key == pygame.K_p and not Game.check_game_over():
                    State.paused = not State.paused

    @staticmethod
    def game_tick():
        old_index = State.directions.index(State.direction)
        cur_index = State.directions.index(State.change_to)
        d_index = cur_index - old_index

        if State.change_to == 'U' and State.direction != 'D':
            State.direction = 'U'
        if State.change_to == 'D' and State.direction != 'U':
            State.direction = 'D'
        if State.change_to == 'L' and State.direction != 'R':
            State.direction = 'L'
        if State.change_to == 'R' and State.direction != 'L':
            State.direction = 'R'

        if State.direction == 'U':
            State.snake_pos[1] -= 10
        if State.direction == 'D':
            State.snake_pos[1] += 10
        if State.direction == 'L':
            State.snake_pos[0] -= 10
        if State.direction == 'R':
            State.snake_pos[0] += 10

        State.snake_body.insert(0, list(State.snake_pos))
        if State.snake_pos[0] == State.food_pos[0] and State.snake_pos[1] == State.food_pos[1]:
            State.score += 1
            next_food_pos = [
                random.randrange(1, (frame_size_x // 10)) * 10,
                random.randrange(1, (frame_size_y // 10)) * 10
            ]
            delta_food_pos = [next_food_pos[0] - State.food_pos[0], next_food_pos[1] - State.food_pos[1]]
            State.food_pos = next_food_pos
            git.commit(push=list(State.snake_pos), pop=None, food_pos=delta_food_pos, direction=d_index, score_d=1)
        else:
            popped = State.snake_body.pop()
            git.commit(push=list(State.snake_pos), pop=popped, food_pos=[0, 0], direction=d_index, score_d=0)

    @staticmethod
    def draw():
        Game.game_window.fill(Colors.black)
        for pos in State.snake_body:
            pygame.draw.rect(Game.game_window, Colors.green, pygame.Rect(pos[0], pos[1], 10, 10))

        pygame.draw.rect(
            Game.game_window, Colors.white,
            pygame.Rect(State.food_pos[0], State.food_pos[1], 10, 10)
        )

    @staticmethod
    def check_game_over():
        if State.snake_pos[0] < 0 or State.snake_pos[0] > frame_size_x - 10:
            return True
        if State.snake_pos[1] < 0 or State.snake_pos[1] > frame_size_y - 10:
            return True
        for block in State.snake_body[1:]:
            if State.snake_pos[0] == block[0] and State.snake_pos[1] == block[1]:
                return True

    @staticmethod
    def draw_score():
        score_font = pygame.font.SysFont('cansalas', 20)
        score_surface = score_font.render('Score : ' + str(State.score), True, Colors.white)
        score_rect = score_surface.get_rect()
        score_rect.midtop = (frame_size_x / 10, 15)
        Game.game_window.blit(score_surface, score_rect)

    @staticmethod
    def draw_pause():
        pause_font = pygame.font.SysFont('cansalas', 40)
        pause_surface = pause_font.render('Paused', True, Colors.white)
        pause_rect = pause_surface.get_rect()
        pause_rect.midtop = (frame_size_x / 2, frame_size_y / 2)
        Game.game_window.blit(pause_surface, pause_rect)


while not State.exit:
    Game.proc_input()

    if not State.paused:
        Game.game_tick()

    Game.draw()
    Game.draw_score()
    if Game.check_game_over():
        State.paused = True
    if State.paused:
        Game.draw_pause()

    pygame.display.update()
    Game.fps_controller.tick(difficulty)


