import pygame

from state import State


def safe_read_int(msg):
    while True:
        try:
            return int(input(msg))
        except ValueError:
            print('[ERR-] Provide integer.')


class Commit:
    def __init__(self, push=[-1, -1], pop=[-1, -1], score_d=0, direction=0, food_pos=[-1, -1], parent_id=-1, id=0):
        self.pop = pop
        self.push = push
        self.score_d = score_d
        self.parent_id = parent_id
        self.child_ids = []
        self.id = id
        self.direction = direction
        self.food_pos = food_pos

    def write(self, out_stream):
        l = [
            self.pop[0], self.pop[1],
            self.push[0], self.push[1],
            self.score_d,
            self.parent_id,
            self.id,
            self.direction,
            self.food_pos[0], self.food_pos[1],
            *self.child_ids
        ]
        out_stream.write(','.join(list(map(lambda x: str(x), l))))

    @staticmethod
    def parse(c_str: str):
        c = Commit()
        data = list(map(lambda x: int(x), c_str.split(',')))
        c.pop = [data[0], data[1]]
        c.push = [data[2], data[3]]
        c.score_d = data[4]
        c.parent_id = data[5]
        c.id = data[6]
        c.direction = data[7]
        c.food_pos = [data[8], data[9]]
        c.child_ids = data[10:]
        return c


class Git:
    def __init__(self):
        self.commits = [Commit()]
        self.head_id = 0
        self.git = 'git.dt'
        self.git_ls = 'git_ls.dt'
        self.branch_ids = [0]
        self.__read()
        self.log(["--all"])

        if len(self.commits) > 1:
            self.restore_state_with_id(self.head_id)

    def proc_engine_input(self, event):
        if State.git_key_pressed:
            if event.key == pygame.K_u:
                State.paused = True
                self.undo()
            elif event.key == pygame.K_r:
                State.paused = True
                self.redo()
            elif event.key == pygame.K_f:
                State.paused = True
                self.log(["--all"])
            elif event.key == pygame.K_c:
                State.paused = True
                self.log(["--cur"])

    def log(self, cmds: list):
        if len(cmds) == 0:
            print('[ERR-] Where args? --all or --cur')
            return
        if cmds[0] == '--all':
            print(f'[INFO] {"ID":10}{"PUSH":15}{"POP":15}{"SCR":4}{"DIR":4}{"FOOD":15}{"CHILD"}')
            for c in self.commits:
                print(f'[INFO] {c.id:10}{c.push.__str__():15}{c.pop.__str__():15}{c.score_d.__str__():4}'
                      f'{c.direction.__str__():4}{c.food_pos.__str__():15}{c.child_ids.__str__()}')
            print(f'[INFO] Head {self.head_id}')
            print(f'[INFO] Branches {self.branch_ids}')
        elif cmds[0] == '--cur':
            c = self.commits[self.head_id]
            print(f'[INFO] {"ID":10}{"PUSH":15}{"POP":15}{"SCR":4}{"DIR":4}{"FOOD":15}{"CHILD"}')
            print(f'[INFO] {c.id:10}{c.push.__str__():15}{c.pop.__str__():15}{c.score_d.__str__():4}'
                  f'{c.direction.__str__():4}{c.food_pos.__str__():15}{c.child_ids.__str__()}')
        else:
            print('[ERR-] Where args? --all or --cur')

    def undo(self):
        if self.commits[self.head_id].parent_id == -1:
            print('[INFO] The root of the tree has been reached')
        else:
            commit = self.commits[self.head_id]
            self.head_id = commit.parent_id

            State.score = State.score - commit.score_d
            State.snake_body.remove(State.snake_body[0])
            State.snake_pos = list(State.snake_body[0])
            cur_index = State.directions.index(State.direction)
            cur_index = cur_index - commit.direction
            State.direction = State.directions[cur_index]
            State.change_to = State.directions[cur_index]
            State.food_pos = [State.food_pos[0] - commit.food_pos[0], State.food_pos[1] - commit.food_pos[1]]
            if commit.score_d == 0:
                State.snake_body.append(list(commit.pop))

            cc = self.commits[self.head_id]
            print(f'[INFO] Now we here (id, push, pop, delta_score, direction, food_pos, child) ==>> '
                  f'{cc.id}, {cc.push}, {cc.pop}, {cc.score_d}, {cc.direction}, {cc.food_pos}, {cc.child_ids}')

    def redo(self):
        if len(self.commits[self.head_id].child_ids) == 0:
            print('[INFO] The end of the branch has been reached')
        else:
            commit = self.commits[self.head_id]
            cid = 0
            if len(commit.child_ids) > 1:
                cid = safe_read_int(f'[INFO] Select branch index from 0 to ({len(commit.child_ids) - 1}): ')
            self.head_id = commit.child_ids[cid]
            cc = self.commits[self.head_id]

            State.score = State.score + commit.score_d
            State.snake_body.insert(0, list(cc.push))
            State.snake_pos = list(cc.push)
            cur_index = State.directions.index(State.direction)
            cur_index = cur_index + cc.direction
            State.direction = State.directions[cur_index]
            State.change_to = State.directions[cur_index]
            State.food_pos = [State.food_pos[0] + cc.food_pos[0], State.food_pos[1] + cc.food_pos[1]]
            if cc.score_d == 0:
                State.snake_body.pop()

            print(f'[INFO] Now we here (id, push, pop, delta_score, direction, food_pos, child) ==>> '
                  f'{cc.id}, {cc.push}, {cc.pop}, {cc.score_d}, {cc.direction}, {cc.food_pos}, {cc.child_ids}')

    def commit(self, push, pop, score_d, direction, food_pos):
        self.save_current_state()
        new_commit = Commit(push=push,
                            pop=pop,
                            score_d=score_d,
                            direction=direction,
                            food_pos=food_pos,
                            parent_id=self.head_id,
                            id=len(self.commits))
        if len(self.commits[self.head_id].child_ids) > 0:
            self.branch_ids.append(new_commit.id)
        else:
            self.branch_ids.remove(self.head_id)
            self.branch_ids.append(new_commit.id)
        self.commits[self.head_id].child_ids.append(new_commit.id)
        self.head_id = new_commit.id
        self.commits.append(new_commit)

    def save_current_state(self):
        with open(self.git_ls, 'a') as f:
            f.write(f'{self.head_id},{State.to_str()}\n')

    def restore_state_with_id(self, s_id):
        try:
            print(f'[INFO] Try to restore {s_id}.')
            with open(self.git_ls, 'r') as f:
                for line in f:
                    data = list(map(lambda x: int(x), line.split(',')))
                    if data[0] == s_id - 1:
                        print('[INFO] restoring...')
                        State.from_list(data[1:])
                        return
        except FileNotFoundError:
            pass

    def __read_header(self, input_stream):
        self.head_id = int(input_stream.readline())
        self.branch_ids = list(map(lambda x: int(x), input_stream.readline().split(',')))

    def __write_header(self, out_stream):
        out_stream.write(str(self.head_id) + '\n')
        out_stream.write(','.join(map(lambda x: str(x), self.branch_ids)) + '\n')

    def __read(self):
        try:
            with open(self.git, 'r') as f:
                self.__read_header(f)
                self.commits.clear()
                for line in f:
                    self.commits.append(Commit.parse(line))
        except FileNotFoundError:
            pass

    def write(self):
        with open(self.git, 'w') as f:
            self.__write_header(f)
            for c in self.commits:
                c.write(f)
                f.write('\n')
