# Implements SudokuGame object that allows to keep track of the initial puzzle and user's guesses.
#
# Allows saving and loading games to/from a file.
#
# Currently computes a solution on SudokuGame instance creation, making it slow (especially for 16x16 sudokus).
# Think whether this can be changed.
#
# should only depend on sudoku.py
#


import itertools
import numpy as np
import pickle

from sudoku import Sudoku


def to_list(element):
    """
    If element is a list, returns entry, else converts it to a list [element]
    :param element: Any
    :return:
    """
    if type(element) is list:
        return element.copy()
    else:
        return [element]


class SudokuGame():
    """
    Class responsible for a single sudoku game, including remembering user input.
    """

    def __init__(self, initial_board, N=3, allow_multiple_solutions=False):
        """
        :param initial_board: Initial sudoku set up, integer array of shape (N**2, N**2).
            0's for missing values, numbers 1 to N**2 for fixed values
            TODO: implement multiple possibilities given values
        :param N: Size of the small squares in sudoku, default is N=3 for the standard sudoku
        :param allow_multiple_solutions:
            TODO: implement dealing with boards that have multiple solutions, for now some functionality might not work
             as expected if initial set up has multiple solutions
        """
        self.initial_board = initial_board.copy()
        self.N = N
        self.solutions = Sudoku(initial_board, self.N).solve(
            maximal_number_of_solutions=('all' if allow_multiple_solutions else 1)
        )
        self.allow_multiple_solutions = allow_multiple_solutions

        self.guesses = [[0]*(N*N) for j in range(N*N)]
        for i, j in itertools.product(range(N * N), range(N * N)):
            self.guesses[i][j] = to_list(self.initial_board[i][j])

        self._computer_help_enabled = False

        self._create_sudoku_mode = False

        self._version = 0.1

    def enable_create_sudoku_mode(self):
        self._create_sudoku_mode = True

    def create_sudoku_mode_is_enabled(self):
        return self._create_sudoku_mode

    def enable_computer_help(self):
        self._computer_help_enabled = True

    def computer_help_is_enabled(self):
        return self._computer_help_enabled

    def check_position(self, position):
        N = self.N
        try:
            if len(position) != 2:
                raise Exception("Invalid format position argument.")
        except:
            raise Exception("Invalid format position argument")

        x = position[0]
        y = position[1]
        if x >= N * N or x < 0 or y >= N * N or y < 0:
            raise Exception("position specified is outside of the bounds of sudoku")

    '''def change_guess(self, new_guesses, position):
        """
        Adjusts the guess to new_guess at position.
        :param new_guesses: a list of ints from 0 to N**2, 0 for no guess, single element list for a certain number guess. Single int
        :param position: (int,int): the position to adjust. If position at the start was fixed in the initial board, do not do anything
        :return: None, modifies the original object
        """

        self.check_position(position)

        new_guesses = to_list(new_guesses)
        for guess in new_guesses:
            if guess >= N ** N or guess < 0:
                raise Exception("guess is outside of the possible range")

        i, j = position

        if self.initial_board[i][j] != 0:
            return None
            # TODO: implement dealing with initial boards that have options

        else:
            self.guesses[i][j] = new_guesses

    def add_guess(self, extra_guess, position):

        self.check_position(position)

        i, j = position

        if extra_guess in self.guesses[i][j]:
            pass
        else:
            self.guesses[i][j].append(extra_guess)

    def pop_guess(self, position, guess=None):

        self.check_position(position)

        i, j = position

        if (len(self.guesses[i][j]) > 0) and (self.initial_board[i][j] == 0):
            # TODO: Implement pop for initial boards that allow multiple options
            if guess is None:
                self.guesses[i][j].pop()

            elif (guess == 'All') or (guess == 'all'):
                self.guesses[i][j] = to_list(self.initial_board[i][j])

            else:
                pass
                # TODO: implement removing a certain guess'''

    def check_current_guesses(self):
        N = self.N
        solution = self.solutions[0]  # TODO: Implement multiple solutions

        correctness_check = True
        for i, j in itertools.product(range(N * N)):
            if 0 not in self.guesses[i][j] and solution[i][j] not in self.guesses[i][j]:
                correctness_check = False
                break

        if not correctness_check:
            return False
        else:
            return True

    def check_if_solution_is_full_and_correct(self):
        N = self.N
        answers = np.zeros((N*N, N*N))
        correct = True
        for i, j in itertools.product(range(N*N), range(N*N)):
            if len(self.guesses[i][j]) != 1 or self.guesses[i][j][0] == 0:
                correct = False
                break
            else:
                answers[i][j] = self.guesses[i][j][0]

        if not correct:
            return 'Not all cells filled'
        else:
            answers_sudoku = Sudoku(answers, N)
            correct = answers_sudoku.check()
        return correct

    def save_game(self, file_path):
        """
        Saves the current game to file_path
        :param file_path:
        :return: None
        """
        try:
            with open(file_path, 'wb') as output_file:
                pickle.dump(self, output_file, pickle.HIGHEST_PROTOCOL)
        except:
            pass


def load_game(file_path):
    try:
        with open(file_path, 'rb') as input_file:
            return pickle.load(input_file)
    except:
        pass