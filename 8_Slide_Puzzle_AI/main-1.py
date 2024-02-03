import sys

import pygame
import time
import threading
from random import randint
from copy import deepcopy
from search import Search

pygame.init()


class MysticSquare:

    def __init__(self, shape: int, shuffle: bool = True, sleep_time: float = 0.3, algorithm: str = None):

        self.search = Search(
            state=None, goal_test=self.is_solved, next_states=self.next_states)
        if shape > 7 or shape < 2:
            raise Exception('The shape between 2 & 7 is recommended.')
        # Puzzle Variables
        self.puzzle_shape = shape
        self.puzzle_size = self.puzzle_shape ** 2
        self.puzzle = [
            [num + 1 for num in range(i * shape, i * shape + shape)] for i in range(0, shape)]
        self.puzzle[-1][-1] = 0
        self.goal_puzzle = deepcopy(self.puzzle)

        # Game Variables
        self.algorithm = algorithm
        self.on_process = False
        self.sleep_time = sleep_time
        self.running = True
        self.blocks = []
        self.labels = []
        self.font = pygame.font.SysFont("freesansbold.ttf", 50)
        self.icon = pygame.image.load(
            r'C:\Users\vidya\Desktop\slide_ai\icon.png')

        # Colors
        self.bg_color = pygame.Color('#97E5EF')
        self.fg_color = pygame.Color('#F0134D')
        self.text_color = pygame.Color('#E4FBFF')

        # Window
        self.block_size = 100
        self.gap = 2
        self.size = ((self.puzzle_shape + 1) * self.gap) + \
            (self.puzzle_shape * self.block_size)
        self.screen = pygame.display.set_mode((self.size, self.size))
        pygame.display.set_caption(
            f'8 Slide Puzzle  - {str(self.puzzle_shape ** 2 - 1)}')
        pygame.display.set_icon(self.icon)

        if shuffle:
            self.shuffle()
        self.update_blocks()

    # Game Functions
    def update_blocks(self):
       
        self.blocks.clear()
        self.labels.clear()

        x = self.gap
        y = self.gap
        for row in self.puzzle:
            for num in row:
                text_fraction = 3 if len(str(num)) == 1 else 4
                block = pygame.Rect((x, y), (self.block_size, self.block_size))
                num_text = (self.font.render(str(num), True, self.text_color),
                            (int(x + self.block_size / text_fraction), int(y + self.block_size / 4)))
                if num == 0:
                    self.blocks.append(0)
                    self.labels.append(0)
                else:
                    self.blocks.append(block)
                    self.labels.append(num_text)
                x += self.gap + self.block_size

            x = self.gap
            y += self.gap + self.block_size

    def draw_blocks(self):

        for block, text in zip(self.blocks, self.labels):
            if block != 0:
                pygame.draw.rect(self.screen, self.fg_color,
                                 block, border_radius=20)
                self.screen.blit(text[0], text[1])

    def possible_moves(self, root: bool = False, state=None) -> list:

        if state is None:
            state = self.puzzle
        possibilities = []
        for row in range(len(state)):
            for col in range(len(state[0])):
                if state[row][col] == 0:
                    loc = [row, col]
                    shape = self.puzzle_shape
                    # if in Corners
                    if loc == [0, 0]:
                        possibilities.extend([(0, 1), (1, 0)])
                    elif loc == [0, shape - 1]:
                        possibilities.extend([(0, shape - 2), (1, shape - 1)])
                    elif loc == [shape - 1, 0]:
                        possibilities.extend([(shape - 2, 0), (shape - 1, 1)])
                    elif loc == [shape - 1, shape - 1]:
                        possibilities.extend(
                            [(shape - 2, shape - 1), (shape - 1, shape - 2)])
                    # if in Sides
                    elif loc[0] == 0:
                        possibilities.extend(
                            [(0, col + 1), (0, col - 1), (1, col)])
                    elif loc[0] == shape - 1:
                        possibilities.extend(
                            [(shape - 1, col + 1), (shape - 1, col - 1), (shape - 2, col)])
                    elif loc[1] == 0:
                        possibilities.extend(
                            [(row - 1, 0), (row + 1, 0), (row, 1)])
                    elif loc[1] == shape - 1:
                        possibilities.extend(
                            [(row - 1, shape - 1), (row + 1, shape - 1), (row, shape - 2)])
                    # if in Middle
                    else:
                        possibilities.extend(
                            [(row, col + 1), (row, col - 1), (row + 1, col), (row - 1, col)])
                    if root:
                        return [possibilities, (row, col)]
                    return possibilities

    def changed_state(self, move: tuple, state=None) -> list:

        empty_block = None
        state = deepcopy(state)
        if state is None:
            state = deepcopy(self.puzzle)
        for row in range(len(state)):
            for col in range(len(state[0])):
                if state[row][col] == 0:
                    empty_block = (row, col)
                    break
        possible_blocks = self.possible_moves(state=state)
        i, j = move[0], move[1]

        if move in possible_blocks:
            temp = state[i][j]
            state[i][j] = 0
            state[empty_block[0]][empty_block[1]] = temp
        return state

    def handle_click(self, pos: tuple, mouse_event, key_event):

        self.on_process = True
        if key_event.key == pygame.K_LEFT:
            r, c = 0, 0
            for block in self.blocks:
                if block != 0 and block.collidepoint(pos[0], pos[1]):
                    self.puzzle = self.changed_state((r, c))
                    self.update_blocks()
                    break
                c += 1
                if c > self.puzzle_shape - 1:
                    c = 0
                    r += 1
            self.on_process = False

        elif key_event.key == pygame.K_RIGHT:
            self.shuffle()
            self.on_process = False

        elif key_event.key == pygame.K_DOWN:
            self.search.set_state(self.puzzle)
            thread = threading.Thread(target=self.solve)
            thread.start()

    def shuffle(self, moves: int = None):

        print("Shuffled the Puzzle randomly.")
        root_copy = None
        if moves is None:
            if self.puzzle_shape < 4:
                moves = self.puzzle_shape ** 3
            else:
                moves = self.puzzle_shape * 25
        for i in range(moves):
            possible_blocks, root = self.possible_moves(root=True)
            if root_copy is not None:
                possible_blocks.remove(root_copy)
            random_move = possible_blocks[randint(0, len(possible_blocks) - 1)]
            self.puzzle = self.changed_state(random_move)
            root_copy = root
        self.update_blocks()

    
    def is_solved(self, state=None) -> bool:

        if state is None:
            state = self.puzzle
        return state == self.goal_puzzle

    def next_states(self, state) -> list:

        states = []
        next_moves = self.possible_moves(state=state)
        for move in next_moves:
            temp_state = deepcopy(state)
            states.append(self.changed_state(move, temp_state))
        return states

    def solve(self):

        steps = self.search.search(algorithm=self.algorithm)
        n_steps = len(steps)
        c_step = 1
        for step in steps:
            time.sleep(self.sleep_time)
            print(f"\rStep: {c_step}/{n_steps}", end='')
            self.puzzle = step
            try:
                self.update_blocks()
            except pygame.error:
                quit("Program Stopped")
            c_step += 1
        print("\nSolved\n")
        self.on_process = False

    
    def main(self):
        while self.running:
            self.screen.fill(self.bg_color)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.search.quit = True
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if not self.on_process:
                        self.handle_click(pygame.mouse.get_pos(), event, event)
            self.draw_blocks()
            pygame.display.update()


if __name__ == '__main__':

    choice = input("ENTER A CHOICE : ")
    if choice == "bfs":
        try:
            puzzle = MysticSquare(shape=3, shuffle=False,
                                  sleep_time=0.5, algorithm="bfs")
            puzzle.main()
        except AttributeError as error:
            print(error)
            quit("Program Stopped")
        except Exception as error:
            quit(error)

    elif choice == "dfids":
        try:
            puzzle = MysticSquare(shape=3, shuffle=False,
                                  sleep_time=0.5, algorithm="dfids")
            puzzle.main()
        except AttributeError as error:
            print(error)
            quit("Program Stopped")
        except Exception as error:
            quit(error)

    elif choice == "dls":
        try:
            puzzle = MysticSquare(shape=3, shuffle=False,
                                  sleep_time=0.5, algorithm="dfids")
            puzzle.main()
        except AttributeError as error:
            print(error)
            quit("Program Stopped")
        except Exception as error:
            quit(error)

    elif choice == "dfs":
        try:
            puzzle = MysticSquare(shape=3, shuffle=False,
                                  sleep_time=0.5, algorithm="dfids")
            puzzle.main()
        except AttributeError as error:
            print(error)
            quit("Program Stopped")
        except Exception as error:
            quit(error)
