# IGNORE
# Junk file for quickly checking some functionality.
#
#


import tkinter as tk
import tkinter.ttk

import numpy as np
import puzzle_generator
from sudoku import Sudoku
import pick_game_ui
from game_settings import UI_settings

import time
import sys

table = np.array([[0, 2, 3, 4, 5, 6, 7, 8, 9],
                        [4, 5, 6, 7, 8, 9, 0, 2, 3],
                        [7, 8, 9, 1, 0, 3, 0, 5, 6],
                        [2, 3, 0, 5, 6, 0, 8, 9, 1],
                        [5, 6, 0, 8, 9, 1, 2, 3, 4],
                        [8, 9, 1, 2, 0, 4, 5, 6, 0],
                        [3, 4, 5, 6, 7, 8, 9, 1, 2],
                        [6, 7, 8, 9, 1, 2, 0, 4, 5],
                        [9, 1, 2, 3, 4, 5, 6, 7, 8]])

#print(np.argwhere(table==0))

#success, sudoku = puzzle_generator.generate_sudoku_from_a_full_puzzle(proportion_of_missing_cells=float(50/81), maximal_time=60)

#print(puzzle_generator.generate_sudoku_from_a_full_puzzle(proportion_of_missing_cells=float(50/81), maximal_time=60))



"""
    #  have ~ 100-120 hints for N=4 

    initial_board = [[0, 4, 3, 6, 1, 0, 5, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 2, 0, 0, 4, 0, 0, 0, 0],
        [0, 1, 0, 5, 0, 0, 0, 0, 6],
        [4, 0, 7, 3, 0, 0, 0, 0, 1],
        [0, 0, 8, 0, 0, 2, 4, 5, 0],
        [5, 0, 0, 0, 8, 0, 0, 4, 0],
        [7, 6, 0, 9, 2, 0, 0, 3, 5],
        [0, 0, 1, 4, 3, 0, 9, 0, 0]]
        
    initial_board = [[0, 0, 8, 0, 0, 7, 0, 0, 0],
        [0, 0, 2, 8, 0, 0, 0, 9, 5],
        [0, 0, 0, 2, 6, 0, 0, 0, 0],
        [6, 0, 0, 0, 0, 5, 0, 0, 0],
        [7, 0, 0, 0, 1, 0, 0, 0, 0],
        [2, 0, 0, 0, 0, 0, 7, 4, 0],
        [1, 0, 0, 0, 0, 2, 0, 0, 3],
        [0, 0, 0, 6, 0, 0, 0, 5, 0],
        [4, 0, 0, 0, 7, 0, 0, 0, 6]] # 23 guesses board!  
        
    initial_board = [[1, 0, 3, 0, 0, 0, 7, 0, 5],
        [0, 0, 0, 0, 7, 6, 0, 0, 0],
        [0, 0, 6, 0, 5, 0, 0, 0, 0],
        [0, 7, 5, 0, 9, 0, 0, 0, 3],
        [0, 3, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 8, 0, 0, 9, 0, 0],
        [0, 2, 0, 1, 0, 0, 0, 8, 0],
        [8, 0, 7, 0, 0, 0, 4, 5, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0]] # 22 guesses board!  
        """


number_of_guesses = []
sudoku = Sudoku([[0, 4, 3, 6, 1, 0, 5, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 2, 0, 0, 4, 0, 0, 0, 0],
        [0, 1, 0, 5, 0, 0, 0, 0, 6],
        [4, 0, 7, 3, 0, 0, 0, 0, 1],
        [0, 0, 8, 0, 0, 2, 4, 5, 0],
        [5, 0, 0, 0, 8, 0, 0, 4, 0],
        [7, 6, 0, 9, 2, 0, 0, 3, 5],
        [0, 0, 1, 4, 3, 0, 9, 0, 0]], N=3)

#print(puzzle_generator.to_string(sudoku=sudoku))
# 043610500000000000020040000010500006407300001008002450500080040760920035001430900,31,0,False,False
# 3,0,4,3,6,1,0,5,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,4,0,0,0,0,0,1,0,5,0,0,0,0,6,4,0,7,3,0,0,0,0,1,0,0,8,0,0,2,4,5,0,5,0,0,0,
# 8,0,0,4,0,7,6,0,9,2,0,0,3,5,0,0,1,4,3,0,9,0,0,3,31,0,False,False

#string = puzzle_generator.to_string(sudoku=sudoku)
#unpacked = puzzle_generator.full_information_from_string(string)
#sudoku = puzzle_generator.sudoku_from_string(string=unpacked[5], N=unpacked[0])

#print(sudoku)

#start_time = time.time()

#puzzle_generator.generate_to_file("puzzle_banks/try.txt", number_of_sudokus=300, time_for_each_sudoku=3)

#print(str(time.time()-start_time))

structured_data = np.array([(1, 0, '15')], dtype=[('N', 'uint8'), ('bool', '?'), ('string', 'U10')])

new_structured_data = np.array([tuple([3,1,'12883'])], dtype=[('N', 'uint8'), ('bool', '?'), ('string', 'U10')])

structured_data = np.append(structured_data, new_structured_data)


file_names = ['puzzle_banks/try(6).txt']


sudokus_info = puzzle_generator.read_from_files(file_names)

root = tk.Tk()
root.title('Sudoku')

mainframe = tk.ttk.Frame(root)
mainframe.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))

ui_settings = UI_settings(N=3)

picking_puzzle_ui = pick_game_ui.PickGameUI(parent=mainframe, sudokus_info=sudokus_info, ui_settings=ui_settings)

root.mainloop()