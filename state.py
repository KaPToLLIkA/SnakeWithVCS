import random


frame_size_x = 720
frame_size_y = 480


class State:
    directions = ['U', 'D', 'R', 'L']

    snake_pos = [100, 50]
    snake_body = [[100, 50], [100 - 10, 50], [100 - (2 * 10), 50]]

    food_pos = [random.randrange(1, (frame_size_x // 10)) * 10, random.randrange(1, (frame_size_y // 10)) * 10]
    food_spawn = True

    direction = 'R'
    change_to = direction

    score = 0

    paused = False

    exit = False

    @staticmethod
    def reset():
        State.snake_pos = [100, 50]
        State.snake_body = [[100, 50], [100 - 10, 50], [100 - (2 * 10), 50]]

        State.food_pos = [random.randrange(1, (frame_size_x // 10)) * 10, random.randrange(1, (frame_size_y // 10)) * 10]
        State.food_spawn = True

        State.direction = 'RIGHT'
        State.change_to = State.direction

        State.score = 0

        State.paused = False

