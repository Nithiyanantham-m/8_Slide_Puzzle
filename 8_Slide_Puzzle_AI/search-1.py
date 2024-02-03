from treeds import Tree
import time


class Search(Tree):

    def __init__(self, goal_test, next_states, state=None):

        if state is not None:
            super().__init__(root_nodes=[state], auto_correct=True)
            self.state = state
        self.algorithms = {
            'bfs': self.bfs,
            'dfs': self.dfs,
            'dls': self.dls,
            'dfids': self.dfids
        }
        self.goal_test = goal_test
        self.next_states = next_states
        self.quit = False

    def set_state(self, state):

        self.state = state
        super().__init__(root_nodes=[state], auto_correct=True)

    def non_visited_states(self, state) -> list:

        self.add_children(state, self.next_states(state))
        return self.get_children(state)

    def search(self, algorithm: str, verbose=True) -> list:

        if type(algorithm) != str:
            raise Exception("type(algorithm) must be string.")
        try:
            start_time = time.time()
            solution = self.algorithms[algorithm](verbose=verbose)
            time_taken = str(time.time() - start_time).split('.')
            fmt_time = time_taken[0] + '.' + time_taken[1][:2]
            if verbose:
                print("Time taken:", fmt_time)
            return solution
        except KeyError:
            raise Exception(f"No algorithm named {algorithm} found.")

    # Search Methods
    def bfs(self, verbose: bool = True) -> list:

        if verbose:
            print("**************Solving(BFS)*****************")
        depth_count = 0
        states = 1
        queue = [self.state]
        while len(queue) != 0:
            if verbose:
                print(f"\rDepth: {depth_count} | States: {states}", end='')
            new_open = []
            for state in queue:
                if self.quit:
                    quit()
                if self.goal_test(state):
                    if verbose:
                        print()
                    return self.get_path(state)
                new_open += self.non_visited_states(state)
            queue = new_open
            depth_count += 1
            states += len(queue)
        print(self.tree)
        raise Exception("Can't find Solution.")

    def dfs(self, verbose: bool = True) -> list:

        if verbose:
            print("**************Solving(DFS)*****************")
        depth_count = 0
        states = 1
        stack = [self.state]
        while len(stack) != 0:
            if verbose:
                print(f"\rDepth: {depth_count} | States: {states}", end='')
            if self.quit:
                quit()
            state = stack.pop()
            if self.goal_test(state):
                if verbose:
                    print()
                return self.get_path(state)
            nvs = self.non_visited_states(state)
            if len(nvs) == 0:
                self.delete(state)
                depth_count -= 1
            stack += nvs
            self.add_children(state, nvs)
            depth_count += 1
            states += len(nvs)
        raise Exception("Can't find Solution.")

    def dls(self, depth: int = 0, verbose: bool = True, get_sates: bool = False) -> [list, int]:

        if verbose:
            print("**************Solving(DLS)*****************")
        stack = [self.state]
        states = 1
        while len(stack) != 0:
            if self.quit:
                quit()
            state = stack.pop()
            state_depth = self.get_depth(state)
            if self.goal_test(state):
                print()
                return self.get_path(state)
            if state_depth <= depth:
                if verbose:
                    print(f"\rDepth: {state_depth} | States: {states}", end='')
                nvs = self.non_visited_states(state)
                if len(nvs) == 0:
                    self.delete(state)
                    pass
                self.add_children(state, nvs)
                stack += nvs
                states += len(nvs)
        if get_sates:
            return states
        raise Exception(
            "Can't find Solution in the specified depth try increasing depth.")

    def dfids(self, verbose: bool = True) -> list:

        if verbose:
            print("**************Solving(DFIDS)*****************")
        depth_count = 0
        states = 1
        while True:
            if verbose:
                print(f"\rIteration: {depth_count} | States: {states}", end='')
            if self.quit:
                quit()
            solution = self.dls(depth=depth_count,
                                verbose=False, get_sates=True)
            if type(solution) == list:
                return solution
            else:
                states += solution
            depth_count += 1
