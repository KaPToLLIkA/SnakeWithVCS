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

    git_key_pressed = False

    @staticmethod
    def to_str():
        body = []
        for b in State.snake_body:
            body.append(b[0])
            body.append(b[1])

        l = [
            State.snake_pos[0], State.snake_pos[1],
            State.food_pos[0], State.food_pos[1],
            State.directions.index(State.direction),
            State.score,
            int(State.food_spawn),
            int(True),
            *body,
        ]
        return ','.join(list(map(lambda x: str(x), l)))

    @staticmethod
    def from_list(l):
        State.snake_pos = [l[0], l[1]]
        State.food_pos = [l[2], l[3]]
        State.direction = State.directions[l[4]]
        State.change_to = State.directions[l[4]]
        State.score = l[5]
        State.food_spawn = bool(l[6])
        State.paused = bool(l[7])

        body = l[8:]
        State.snake_body.clear()
        for i in range(0, len(body), 2):
            State.snake_body.append([body[i], body[i + 1]])
