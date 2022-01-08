## Not following the formatting might damage the puzzle bank during run time. Make a copy before doing any manual adjustments to the puzzle bank file.

Sudokus stored in puzzle banks must follow the same format: 

N, number_of_clues, complexity_of_solution, tried_before, done_before
sudoku

Here 
N: int is the side of a small square (N = 3 for standard 9x9 sudokus); 
number_of_clues: int is the number of clues in sudoku;
complexity of soltion: int is the number of times the algorithm had to guess to find the solution (roughly correllates to the difficulty)
tried_before: 0 or 1, constitutes whether the puzzle have been attempted before;
done_before: 0 or 1, constitutes whether the puzzle was successfully solved before.

Then after a line break (but no empty line), sudoku is entered as (N\*\*2)\*\*2 sequence of ints separated by commas. numbers from 1 to N\*\*2 correspond to clues, 0's correspond unknown fields.
