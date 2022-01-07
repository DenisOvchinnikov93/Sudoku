# Sourse code for back-end computations of sudokus. Allows creating and working with square sudokus of any size.
# Size is controlled by N (the side of a small square). Normal sudoku corresponds to N=3.
#
# Functionalities include: storing sudokus; simplifying sudokus using simple algorithms; fully solving sudokus using a
# combination of such simple simplifications and backtracking.
# Sudoku.solve() method allows to specify the maximal number of solutions, in particular it allows to distinguish
# whether a given puzzle has no solutions, has unique solution, or has multiple solutions.
# Checking if a given puzzle has unique solution is time consuming even for standard 9x9 sudokus and might take quite
# some time for 16x16 puzzles. Finding just one solution is usually significantly faster.
#
# Do not change the output formats since the UI relies heavily on this module.
#
# Does not (and should not) depend on any other project files.
#
# TODO: (important) Rewrite this module in C++, as this module is the one that takes the most processing time/resources
#  for sudoku generation and validation.
#



import numpy as np
import copy
import random
import sys
import itertools


class Sudoku(np.ndarray):
    def __new__(cls, array, N, computed=None, possibilities=None):
        """
        Class to operate with sudokus.
        Inherits from np.ndarray and supports all relevant operations.
        :param array: (N**2,N**2) dimension array.
            Elements between 1 and N**2 are for cells that are given.
            0 for elements that are not determined.
            #TODO: (long term) Implement sudokus that have multiple possibilities for a clue
        :param N: is the side of the small square.
            #TODO: (long term) implement rectangular sudokus.
        :param computed:
        :param possibilities: None or (N**2, N**2, N**2+1) np.ndarray, dtype: bool
            if an array, [x, y, value] = True
                if value is one of the possibilities for the cell with coordinates [x, y]
            if None, all possibilities are allowed
            [x, y, 0] = False for all x, y.
        """
        obj = np.asarray(array).copy().view(cls).astype('int16')
        if possibilities is not None:
            obj.possibilities = possibilities.copy()
        else:
            obj.possibilities = np.ones((N * N, N * N, N * N + 1), dtype=bool)
            obj.possibilities[:, :, 0] = 0
        obj.N = N
        obj.extendable = True
        # Finally, we return the newly created object:
        return obj

    def __copy__(self):
        """
        Copy method on Sudoku objects. Call it with copy.copy(sudoku).
        :return: Sudoku
        Copies possibilities for the object as well.
        """
        # cls = self.__class__
        result = Sudoku(array=self, N=self.N, possibilities=self.possibilities)
        return result

    def set_point(self, coordinates: [int,int], value: int) -> None:
        """
        Sets position coordinates to be equal to value. Adjusts self.possibilities to account for the new value set.
        :param coordinates: [int, int]. 0 <= coordinates[0], coordinates[1] <= self.N
        :param value: int. 1 <= value <= self.N
        :return: None
        """
        N = self.N
        i, j = coordinates
        if self[i, j] != 0 and self[i, j] != value and not self.possibilities[i, j, value]:
            raise Exception(
                "Trying to set the value of %s to the coordinate %s in the table \n %s" % (value, coordinates, self))

        self[i, j] = value
        self.possibilities[i, j] = 0
        for ind in range(N * N):
            self.possibilities[ind, j, value] = 0
            self.possibilities[i, ind, value] = 0
        for di in range(N):
            for dj in range(N):
                self.possibilities[(i // N) * N + di, (j // N) * N + dj, value] = 0
        self.possibilities[i, j, value] = 1


    def check(self) -> bool:
        """
        Checks if a Sudoku satisfies all the rules of sudoku. Doesn't check if it is solved, only checks for contradictions.
        :return: bool
        Takes (N**2)**2 basic operations.
        """
        N = self.N
        occurs = np.zeros(N * N + 1, dtype=bool)
        for i in range(N * N):
            occurs.fill(0)
            correct = True
            for j in range(N * N):
                if self[i, j] != 0 and occurs[self[i, j]] == 0:
                    occurs[self[i, j]] = 1
                elif self[i, j] != 0:
                    correct = False
                    #   Debugging print
                    #   print('i, j =' + str(i) + ',' + str(j))
                    #   print(occurs)
                    #   print('column ' + str(i))
                    return False

        for i in range(N * N):
            occurs.fill(0)
            correct = True
            for j in range(N * N):
                if occurs[self[j, i]] == 0:
                    occurs[self[j, i]] = 1
                elif self[j, i]:
                    correct = False
                    print('row ' + str(i))
                    return False

        for i in range(N):
            for j in range(N):
                occurs.fill(0)
                for di in range(N):
                    for dj in range(N):
                        if occurs[self[N * i + di, N * j + dj]] == 0:
                            occurs[self[N * i + di, N * j + dj]] = 1
                        elif self[N * i + di, N * j + dj]:
                            correct = False
                            print('square (' + str(i) + ',' + str(j) + ')')
                            return False
        return correct

    def solved(self) -> bool:
        """
        Computes whether a sudoku is fully solved (doesn't check if it satisfies the rules of sudoku).
        :return: bool
        """
        if np.any(self == 0):
            return False
        else:
            return True

    def number_of_clues(self) -> int:
        """
        Returns the number of non-zero elements in a sudoku
        :return: int
        """
        return int((self != 0).sum())

    def has_unique_solution(self):
        solutions = self.solve(maximal_number_of_solutions=2)
        if len(solutions) == 1:
            return True
        elif len(solutions)>1:
            return False
        else:
            return None

    def can_remove_positions(self, positions):
        """
        Check if removing clues at all positions in positions results in a puzzle with unique solution.
            Does not modify the original Sudoku.
        :param positions: [(int, int)] list of positions to be removed
        :return: bool. True if after removing positions the sudoku has unique solution, else False.
        """

        N = self.N
        new_table = np.copy(self)
        for position in positions:
            i, j = position
            new_table[i][j] = 0

        new_sudoku = Sudoku(new_table, N=self.N)
        solutions = new_sudoku.solve(maximal_number_of_solutions=2)
        if len(solutions) > 1:
            return False
        if len(solutions) == 1:
            return True
        else:
            raise Exception("Given table has no solutions")


    def simplify(self, initial_simplification: bool = False) -> bool:
        """
        Sets the values to all positions in Sudoku that have only one possibility
        :param initial_simplification: bool
            If not initial_simplification, the function assumes possibilities already account for values that are set
                and only adjusts possibilities for cells that are set during the function execution.
            If initial_simplification, the function also adjusts possibilities for cells that were set before.
        :return: bool
            True if a simplification occurs
            False if no simplification occurs
        Initial simplification only needs to be done once. Possibilities persist through copy.copy(sudoku)
        Initial simplification potentially increases the number of operations from (N**2)**2 to (N**2)**3
        """
        simplified = False
        N = self.N
        for i in range(N * N):
            for j in range(N * N):
                if self.possibilities[i, j, 1:].sum() == 1 and not self[i, j]:
                    simplified = True
                    value = np.nonzero(self.possibilities[i, j, 1:])[0] + 1
                    self.set_point([i, j], value)
                if initial_simplification:
                    if self[i, j] != 0:
                        simplified = True
                        self.set_point([i, j], self[i, j])

        return simplified

    def full_simplify(self, initial_simplification: bool = False) -> bool:
        """
        Applies self.simplify() until no more simplifications occur
        :param initial_simplification: bool
        :return: bool
            True if a simplification occurred
            False if no simplification occurred
        """
        simplified_step = self.simplify(initial_simplification=initial_simplification)
        simplified = simplified_step
        while simplified_step:
            simplified_step = self.simplify()
        return simplified

    def number_of_possibilities(self) -> np.ndarray:
        """
        :return: For a given Sudoku, computes (N**2, N**2) ndarray that shows the number of possibilities in each coordinate.
        """
        return self.possibilities.sum(axis=2)


    def solve(self, maximal_number_of_solutions=1, random_state=None, number_of_guesses_tracker=None) -> "[Sudoku]":
        """
        Finds a solution solutions of a given sudoku;
        :param maximal_number_of_solutions: int >= 1 or 'all'. The number of solutions fetched. Use 1 to get a
            single solution, and 2 to check if solution is unique.
        :param random_state: None or int for deterministic behaviour. If None, and the solution is not unique,
                returned solution (or the order of solutions if maximal_number_of_solutions != 1) might be different.
        :param number_of_guesses_tracker: None or []. if array=[] is provided, array will be modified to to have
            the same length as output and display the number of guesses used to compute each solution.
            This will be 'best case' number of guesses.
        :return List of Sudokus that are solutions of the original Sudoku.
            Stops if it finds at least maximal_number_of_solutions of different solutions.
            If no solutions exist, return empty list.
        """

        random.seed(random_state)
        answers = []
        sudokus = []
        sudoku = copy.copy(self)
        N = self.N
        sudoku.simplify(initial_simplification=True)
        if sudoku.solved():
            answers.append(sudoku)
            if number_of_guesses_tracker is not None:
                number_of_guesses_tracker.append(0)

        while (not sudoku.solved()) or len(sudokus) > 0:
            sudoku.full_simplify()
            if sudoku.solved():
                answers.append(sudoku)
                if number_of_guesses_tracker is not None:
                    number_of_guesses_tracker.append(len(sudokus))

                # Debugging print("found a solution")

                if maximal_number_of_solutions != 'all' and len(answers) >= maximal_number_of_solutions:
                    break
                if len(sudokus) > 0:
                    # Debugging print("backtracking to find other solutions")
                    sudoku = sudokus[-1]
                    sudokus.pop()
            else:
                possibilities_number = sudoku.number_of_possibilities()

                if (possibilities_number == 0).any():
                    """print("backtracking since there is no way to put a number on position(s)" + str(
                        np.unravel_index(np.argmin(possibilities_number, axis=None), (N*N, N*N))) + "\n")"""
                    if len(sudokus) == 0:
                        # Debugging print("sudoku not solvable")
                        break
                    else:
                        sudoku = sudokus[-1]
                        sudokus.pop()
                else:

                    possibilities_number = np.where(possibilities_number <= 1, N*N+1, possibilities_number)
                    min_index = np.unravel_index(np.argmin(possibilities_number, axis=None), (N*N, N*N))
                    values = np.nonzero(sudoku.possibilities[min_index] == True)[0]
                    # value = values[0] # use this for deterministic behaviour
                    value = np.random.choice(values)
                    new_sudoku = copy.copy(sudoku)
                    sudoku.possibilities[min_index[0], min_index[1], value] = 0
                    sudokus.append(sudoku)
                    sudoku = new_sudoku
                    sudoku.set_point(min_index, value)

                    # Debugging print("setting value " + str(value) + " at point " + str(min_index) + "\n")

        return answers


def main():
    # Testing the solve method: remove random drop numbers from a specific full N^2 x N^2 sudoku, record all answers
    # (with some debugging information) in the out.txt
    # See old results from this and several other tests in the 'debugging/' folder.
    # Some of the testing is now implemented in
    N = 4
    drop = 150
    number_of_samples = 1

    f_out = open("out.txt", "w")
    sys.stdout = f_out

    table = np.fromfunction(lambda i, j: (N * i + j + (i // N)) % (N * N) + 1, (N * N, N * N), dtype=int)

    random.seed(2)
    for test_case in range(number_of_samples):
        sudoku = Sudoku(table, N)
        for drop_number in range(drop):
            i = random.randint(0, N * N - 1)
            j = random.randint(0, N * N - 1)
            sudoku[i, j] = 0
        #sudoku[1:, :] = 0
        print("Case #" + str(test_case) +"\n", sudoku, sudoku.check())
        answers = sudoku.solve(maximal_number_of_solutions='all')
        print("Case number " + str(test_case)+" has "+str(len(answers))+" solutions. They are:\n")
        for sudoku in answers:
            print(sudoku)

        #print("possibilities number : \n", sudoku.number_of_possibilities())
        if not sudoku.solved():
            print("###########################################")

    f_out.close()

    # Below code used for testing in the past below
    """sudoku = Sudoku(table, N)
    sudoku[-3:, :] = 0
    answers = sudoku.solve(find_all_solutions=True)
    f_answers = open("answers.txt", "w")
    sys.stdout = f_answers
    print("Number of solutions is "+str(len(answers)))
    for sudoku in answers:
        print(sudoku)
    f_answers.close()"""

    """sudoku.set_point([1, 0], 4)
    sudoku.simplify()
    print(sudoku.number_of_possibilities(), "\n")
    print(sudoku1.number_of_possibilities(), "\n")"""


    """sudoku = Sudoku([[0, 2, 3, 4, 5, 6, 7, 8, 9],
     [4, 5, 6, 7, 8, 9, 0, 2, 3],
     [7, 8, 9, 1, 0, 3, 0, 5, 6],
     [2, 3, 0, 5, 6, 0, 8, 9, 1],
     [5, 6, 0, 8, 9, 1, 2, 3, 4],
     [8, 9, 1, 2, 0, 4, 5, 6, 0],
     [3, 4, 5, 6, 7, 8, 9, 1, 2],
     [6, 7, 8, 9, 1, 2, 0, 4, 5],
     [9, 1, 2, 3, 4, 5, 6, 7, 8]], 3)"""

    """[[0 2 3 0 5 6 0 8 9]
     [0 5 6 0 8 9 0 2 3]
     [7 8 9 1 2 3 4 5 6]
     [2 3 4 5 6 7 8 9 1]
     [5 6 7 8 9 1 2 3 4]
     [8 9 1 2 3 4 5 6 7]
     [3 4 5 6 7 8 9 1 2]
     [6 7 8 9 1 2 3 4 5]
     [9 1 2 3 4 5 6 7 8]]"""

    """[[0 0 0 0 0 0 7 8 0]
     [4 5 6 0 0 9 0 0 3]
     [7 8 9 0 2 3 4 5 6]
     [2 0 0 5 0 0 8 9 1]
     [5 6 7 0 0 1 2 0 4]
     [8 9 1 0 0 4 5 6 0]
     [3 0 0 6 7 0 9 0 2]
     [6 0 0 9 0 0 3 0 5]
     [0 0 0 3 4 0 6 7 8]]"""

    """
    25-hint sudoku 
    [[2, 1, 0, 0, 0, 3, 0, 0, 4],
        [0, 0, 0, 0, 0, 2, 0, 6, 0],
        [0, 6, 3, 0, 0, 0, 0, 0, 1],
        [0, 5, 0, 8, 0, 1, 0, 0, 0],
        [0, 0, 0, 2, 0, 9, 0, 0, 3],
        [0, 0, 0, 4, 0, 7, 8, 9, 0],
        [0, 8, 0, 5, 0, 0, 0, 1, 6],
        [0, 7, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 7]]"""

    """print(sudoku.N)
    #sudoku1=sudoku.copy()
    sudoku1 = copy.copy(sudoku)
    print(sudoku1)
    sudoku1.possibilities[1,1]=2
    print(sudoku.possibilities[1,1])
    print(sudoku.computed)
    table = sudoku
    i, j = 1,1
    #check(table, N)"""

if __name__ == "__main__":
    main()

