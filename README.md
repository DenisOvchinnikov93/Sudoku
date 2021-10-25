# Sudoku
Python project to solve sudokus, mostly just for fun.

At the moment it is just barebones Sudoku class, for sudokus of size (N^2, N^2) (standard sudukus are N=3), and supporting methods.

Methods include functionality to find a single solution and/or find all solutions. I didn't want to bruteforce too much, so I added some simple heuristics to simplify sudokus before trying to bruteforce search. Further experiments are needed, but it seems that on most sudokus, heuristics improve performance dramatically. Of course, genearlly solving sudokus is an NP-complete problem (in N), so worst-case complexity is still not polynomial.

Interactive GUI will be added in the future, including ability to enter and check your sudokus.
