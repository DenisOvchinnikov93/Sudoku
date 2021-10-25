import numpy as np
import copy
import random
import sys


class Sudoku(np.ndarray):
    def __new__(cls, array, N, computed=None, possibilities=None):
        """
        Class to operate with sudokus.
        Inherits from np.ndarray and supports all relevant operations.
        :param array: (N**2,N**2) dimension array.
            Elements between 1 and N**2 are for cells that are given.
            0 for elements that are not determined.
        :param N: is the side of the small square.
            #TODO: implement rectangular sudokus.
        :param computed:
            #TODO: implement for GUI display.
        :param possibilities: None or (N**2, N**2, N**2+1) np.ndarray, dtype: bool
            if an array, [x, y, value] = True
                if value is one of the possibilities for the cell with coordinates [x, y]
            if None, all possibilities are allowed
            [x, y, 0] = False for all x, y.
        """
        obj = np.asarray(array).copy().view(cls)
        if possibilities is not None:
            obj.possibilities = possibilities.copy()
        else:
            obj.possibilities = np.ones((N * N, N * N, N * N + 1), dtype=bool)
            obj.possibilities[:, :, 0] = 0
        obj.N = N
        obj.extendable = True
        # Finally, we must return the newly created object:
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
                    print('i, j =' + str(i) + ',' + str(j))
                    print(occurs)
                    print('column ' + str(i))
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

    def solve(self, find_all_solutions:bool = False) -> "[Sudoku]":
        """
        Finds a solution or all solutions of a given sudoku;

        :param find_all_solutions: bool.
        :return: List of Sudokus that are solutions of the original Sudoku.
            If find_all_solutions, returns a list of all solutions.
            If not find_all_solutions, returns a list with just one element that is one of the solutions.
            If no solutions exist, returns a list with one sudoku filled with -1.
        At the moment the implementation is deterministic, but in the future the returned solution
        (or the order of solutions if find_all_solutions) might be different.
        """
        answers = []
        sudokus = []
        sudoku = copy.copy(self)
        N = self.N
        simplified = sudoku.simplify(initial_simplification=True)
        while (not sudoku.solved()) or len(sudokus) > 0:
            sudoku.full_simplify()
            if sudoku.solved():
                answers.append(sudoku)
                # Debugging print("found a solution")
                if not find_all_solutions:
                    break
                if len(sudokus) > 0:
                    # Debugging print("backtracking to find other solutions")
                    sudoku = sudokus[-1]
                    sudokus.pop()
            else:
                possibilities_number = sudoku.number_of_possibilities()

                if (possibilities_number == 0).any():
                    ## coded on the desktop
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
                    value = values[0] #np.random.choice(values)
                    new_sudoku = copy.copy(sudoku)
                    sudoku.possibilities[min_index[0], min_index[1], value] = 0
                    sudokus.append(sudoku)
                    sudoku = new_sudoku
                    sudoku.set_point(min_index, value)
                    # Debugging print("setting value " + str(value) + " at point " + str(min_index) + "\n")
        if len(answers) > 0:
            return answers
        else:
            sudoku.fill(-1)
            return [sudoku]

if __name__ == "__main__":
    # Testing the solve method: remove random drop numbers from a specific full N^2 x N^2 sudoku, record all answers
    # (with some debugging information) in the out.txt
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
        answers = sudoku.solve(find_all_solutions=True)
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
