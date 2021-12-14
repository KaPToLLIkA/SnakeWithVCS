import threading

from state import State


def safe_read_int(msg):
    while True:
        try:
            return int(input(msg))
        except ValueError:
            print('[ERR-] Provide integer.')


class Commit:
    def __init__(self, push, pop, score_d, direction, food_pos, parent_id, id):
        self.pop = pop
        self.push = push
        self.score_d = score_d
        self.parent_id = parent_id
        self.child_ids = []
        self.id = id
        self.direction = direction
        self.food_pos = food_pos


class Git (threading.Thread):
    def __init__(self):
        super().__init__()
        self.commits = [Commit(push=None, pop=None, score_d=0, direction=None, food_pos=None, parent_id=None, id=0)]
        self.head_id = 0
        self.git = 'git.dt'
        self.git_ls = 'git_ls.dt'
        self.branch_ids = [0]

    def run(self):
        while not State.exit:
            cmd = input('Command: ')
            State.paused = True
            self.proc_cmd(cmd)

    def proc_cmd(self, cmd):
        cmds = cmd.split(' ')

        if cmds.__len__() == 0:
            print('[ERR-] Supported commands only: log, undo, redo.')

        if cmds[0] == 'log':
            self.log(cmds[1:])
        elif cmds[0] == 'undo':
            self.undo()
        elif cmds[0] == 'redo':
            self.redo()
        else:
            print('[ERR-] Supported commands only: log, undo, redo.')

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
        if self.commits[self.head_id].parent_id is None:
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

    def __read(self):
        pass

    def __write(self):
        pass

    def __del__(self):
        self.__write()
