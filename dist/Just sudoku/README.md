# Sudoku
## Python project for enjoying sudoku on your local machine. 
###  Customizable settings, over 1000 puzzles and the ability to generate more! 
### Your games are autosaved and can be loaded later, so don't worry about losing your progress!

Interactive GUI was added, including ability to enter and check your sudokus, save and load your games and a puzzle pank with about 1000 sudokus of various difficulty. At the moment standard 9x9 sudokus work without interruptions or using much computational power. 16x16 sudokus are supported (and a few are present in the puzzle bank), but might take up to a minute to load (since the program computes puzzle solution on game launch). 

The user unterface also contains adjustable settings which will be persistent throughout different sessions. More customizable settings will be added in the future.

On the backend side, the app is built around Sudoku class (sudoku.py), for sudokus of size (N^2, N^2) (standard sudukus are N=3), and supporting methods.
Methods include functionality to find a single solution and/or find all solutions. Sudoku class inherits from numpy arrays, allowing to use full numpy functionality to work with them. 

I didn't want to bruteforce solutions algorithm too much, so I added some simple heuristics to simplify sudokus before trying to bruteforce search. Further experiments are needed, but it seems that on most sudokus, heuristics improve performance dramatically. Of course, genearlly solving sudokus is an NP-complete problem (in N), so worst-case complexity is still not polynomial. I plan to reimplement solving sudokus in C++ in the future for better performance. Even though the class inherits from numpy arrays, most expensive operations do not (and can not realistically) use the numpy-specific functionality. 

The project also supports generating new sudokus with desired parameters. Run puzzle_generation.py for a simple gui for that. Again, generating 16x16 sudokus works but is extremely slow. Similarly, generating sudokus with few hints (22 and less) is extremely inconsistent. File puzzle_banks/puzzle_bank.txt contains around 1000 puzzles, all of which (with the exception of two 17-hint sudokus) were generated by puzzle_generator.py. 

Debugging folder contains outputs from several of the older debugging tests.
