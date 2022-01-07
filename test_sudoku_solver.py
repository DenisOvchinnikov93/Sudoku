# Unitest module for the project. Mainly tests Sudoku class interface and solutions
#
# TODO: add more relevant tests so that changing implementations in the future is easy.


import unittest
from sudoku import Sudoku
import puzzle_generator


class SudokuClassTest(unittest.TestCase):

    def setUp(self):
        """
        If adding additional test sudokus, append to the end of the list.
        :return: None
        """
        self.test_boards =[]
        self.test_Ns = []
        self.test_sudokus = []
        self.test_solutions_unique = []
        self.test_solution =[]

        self.test_boards.append(0)
        self.test_Ns.append(0)
        self.test_solutions_unique.append(0)
        self.test_solution.append(0)
        self.test_boards[0] = [[0, 2, 3, 4, 5, 6, 7, 8, 9],
                        [4, 5, 6, 7, 8, 9, 0, 2, 3],
                        [7, 8, 9, 1, 0, 3, 0, 5, 6],
                        [2, 3, 0, 5, 6, 0, 8, 9, 1],
                        [5, 6, 0, 8, 9, 1, 2, 3, 4],
                        [8, 9, 1, 2, 0, 4, 5, 6, 0],
                        [3, 4, 5, 6, 7, 8, 9, 1, 2],
                        [6, 7, 8, 9, 1, 2, 0, 4, 5],
                        [9, 1, 2, 3, 4, 5, 6, 7, 8]]
        self.test_Ns[0] = 3
        self.test_solutions_unique[0] = True

        self.test_boards.append([[ 1,0,0,0,0,0,0,8,9,0,11,0,0,0,0,16],
             [ 5,0,0,8,9,0,11,0,0,14,15,16,0,0,3,0],
             [ 9,0,11,0,13,14,15,0,0,2,0,0,5,6,7,8],
             [ 0,0,0,0,0,2,0,4,0,0,7,8,9,10,11,12],
             [ 2,0,4,5,6,0,8,9,0,0,0,0,0,15,16,0],
             [ 6,7,8,0,0,0,12,0,0,0,16,1,0,3,0,0],
             [10,11,0,0,14,15,16,1,2,3,4,5,6,0,8,9],
             [14,15,0,0,2,3,0,0,6,7,0,9,0,11,0,0],
             [ 3,0,5,6,0,0,0,10,0,12,13,14,0,0,1,0],
             [ 7,8,0,10,11,12,0,14,15,16,1,2,3,0,5,6],
             [11,12,13,0,15,0,1,0,3,4,5,6,7,8,0,0],
             [15,16,1,2,0,4,5,6,0,0,9,0,0,12,0,14],
             [ 4,5,6,7,8,9,0,0,12,13,14,15,16,0,0,3],
             [ 0,9,0,0,12,0,14,15,0,1,2,0,0,5,6,7],
             [12,0,14,15,0,0,2,0,4,0,0,0,8,9,0,0],
             [16,0,2,3,4,5,6,7,8,0,0,0,12,0,0,15]]) # this sudoku has 4 different solutions
        self.test_Ns.append(4)
        self.test_solutions_unique.append(False)


        self.test_boards.append([[0,0,3,4],
                                 [0,0,1,2],
                                 [2,1,4,3],
                                 [4,3,2,1]]
                                )
        self.test_Ns.append(2)
        self.test_solutions_unique = True #simple N=2 sudoku, has only one solution.


        for i in range(len(self.test_boards)):
            self.test_sudokus.append(Sudoku(array=self.test_boards[i], N=self.test_Ns[i]))


    def test_sudoku_setup(self):

        for i in range(len(self.test_boards)):
            self.assertTrue( (self.test_sudokus[i] == self.test_boards[i]).all() )

    def test_sudoku_solver_unique_solution(self):
        self.assertTrue(self.test_sudokus[0].has_unique_solution())

        self.assertFalse(self.test_sudokus[1].has_unique_solution())

    def test_removing_items(self):
        sudoku = self.test_sudokus[0]
        self.assertTrue(sudoku.can_remove_positions([]))
        self.assertTrue(sudoku.can_remove_positions([(1, 1), (2, 5)]))

        sudoku = self.test_sudokus[2]
        self.assertTrue(sudoku.can_remove_positions([(3, 0)]))
        self.assertFalse(sudoku.can_remove_positions([(3, 0), (3, 1)]))

        self.assertTrue(sudoku.can_remove_positions([(3, 0), (3, 2), (2, 1), (2, 3)]))

    def test_number_of_solutions(self):
        pass

    def test_number_of_hints(self):
        self.assertTrue(81 - 10 == self.test_sudokus[0].number_of_clues())
        self.assertTrue(16 - 4 == self.test_sudokus[2].number_of_clues())


    def test_generate_solved_sudoku(self):
        a, n, p = 5, 14315, 237932
        number_of_tests = 3 # Tested with 100 once, takes about .2 seconds per iteration.
        for i in range(number_of_tests):
            random_state = (a+n*i) % p
            N = 2 + (i % 3)
            sudoku = puzzle_generator.generate_solved_sudoku(N=N, random_state=random_state)
            self.assertFalse((sudoku == 0).any()) # checks if the tables are fully filled
            self.assertTrue(sudoku.check()) # checks that there are no contradictions

    def test_generate_sudoku_from_a_full_puzzle(self):
        a, n, p = 3, 14311, 237932
        number_of_tests = 3 # Each loop takes about 10 seconds.
        for i in range(number_of_tests):
            random_state = (a + n * i) % p
            N = 2 + (i%3)
            solved_sudoku = puzzle_generator.generate_solved_sudoku(N=N, random_state=random_state)
            if N<=3:
                target_proportion = 2/3
            if N == 4:
                target_proportion = 1/2
            if N>4:
                target_proportion =1/4

            success, sudoku = puzzle_generator.generate_sudoku_from_a_full_puzzle(
                solved_sudoku, N=N, proportion_of_missing_cells=target_proportion, random_state=random_state)
            solutions = sudoku.solve(maximal_number_of_solutions=2)

            self.assertTrue(len(solutions) == 1)
            self.assertTrue((solutions[0] == solved_sudoku).all())
            if target_proportion <=2/3:
                self.assertTrue(success)
            if success:
                self.assertTrue(sudoku.number_of_clues() <= (1 - target_proportion)*(N**4) + 1 )


if __name__ == '__main__':
    unittest.main()
