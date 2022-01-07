# Simple gui for solving standard 9x9 sudokus.
#
# Does not check for uniqueness just finds a single solution.
# Depending on implementation of Sudoku.solve() a solution returned will not be the same between runs
# if the solution is not unique.
#
# Only depends on sudoku.py in the project. Nothing in the project should depend on this.
#
# Run the script to display the solver.
#


import tkinter as tk
from tkinter import ttk
import tkinter.messagebox

import itertools

from sudoku import Sudoku


def main():

    def solve():
        table = []
        for i in range(N * N):
            table.append([0] * (N * N))
            for j in range(N * N):
                entry = sudoku_numbers[i][j].get()
                if entry != '':
                    table[i][j] = int(entry)

        sudoku = Sudoku(table, N)
        sudoku_solved = sudoku.solve()[0]

        for i, j in itertools.product(range(N * N), range(N * N)):

            if sudoku_solved[i][j] == -1:
                tkinter.messagebox.showinfo('', 'There are no solutions, check your input')
                break

            elif sudoku[i][j] != 0 and sudoku[i][j] != sudoku_solved[i][j]:
                raise Exception("Solver changed a given value, algorithm is incorrect")
            else:
                if sudoku[i][j] == 0:
                    entries[i][j].configure(foreground='blue')
                sudoku_numbers[i][j].set(sudoku_solved[i][j])

    def reset():
        for i, j in itertools.product(range(N * N), range(N * N)):
            sudoku_numbers[i][j].set('')
            entries[i][j].configure(foreground='black')


    root = tk.Tk()
    root.title('Solve any sudoku!')

    mainframe = ttk.Frame(root)
    mainframe.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))


    N=3
    sudoku_numbers = []
    entries = []
    for i in range(N*N):
        sudoku_numbers.append([0]*(N*N))
        entries.append([0]*(N*N))
        for j in range(N*N):
            sudoku_numbers[i][j] = tk.StringVar()
            entries[i][j] = ttk.Entry(mainframe, width=3, textvariable=sudoku_numbers[i][j], foreground='black')
            entries[i][j].grid(column=i+1, row=j+1, sticky=(tk.W,tk.E))

    ttk.Button(mainframe, text="Solve!", command=solve).\
        grid(column=1, row=N*N+2, columnspan=3)

    ttk.Button(mainframe, text="Reset", command=reset).\
        grid(column=7, row=N*N+2, columnspan=3)

    root.mainloop()


if __name__ == '__main__':
    main()