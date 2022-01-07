# User Interface for picking a sudoku out of a puzzle bank.
#
# Allows user to view a puzzle bank, sort available sudokus by difficulty or number of clues.
#
# Parent must be a MainProgram object.
# You can use any Frame as well, if you disable menu and start selected game buttons (can be used to preview games).
#
# Note that the difficulty level estimation is likely not very accurate. Generally:
# sudokus with low difficulty (0-20) are easy,
# sudokus with difficulty 20-40/50 are normal/hard,
# sudokus with difficulty >40/50 are hard/evil
#
# TODO: Improve difficulty estimation (function is provided in pop_up_messages)
# TODO: It might be a better design to allow solving puzzles from this menu. Think about it.

import tkinter as tk
import tkinter.messagebox, tkinter.font
from tkinter import Canvas, Frame

import random
import itertools
import numpy as np
import os

from sudoku import Sudoku
from sudoku_game import SudokuGame
import sudoku_game
import sudoku_game_gui
from game_settings import UI_settings
from sudoku_game_gui import SudokuUI
import puzzle_generator
import pop_up_messages


class PickGameUI(Frame):
    def __init__(self, parent, sudokus_info, ui_settings):
        Frame.__init__(self, parent)
        self.parent = parent
        ui_settings.set_N(3)
        self.ui_settings = ui_settings
        self.sudoku_list_ui = GameListFrame(parent=self, sudokus_info=sudokus_info, ui_settings=ui_settings)
        self.game_ui = SudokuUI(parent=self, game=SudokuGame(np.zeros((9, 9)), N=3), ui_settings=ui_settings)
        self.game_ui.disable()
        self._init_ui()

        pop_up_messages.Hint(self.ui_settings.hints.sorting_games_hint_info).show(self, relx=0.32, rely=0.25)

    def _init_ui(self):
        self.menu = tk.Menu(self)
        self.menu.add_command(label='Main menu', command=self.parent.go_to_the_main_menu)
        self.menu.add_command(label='Start solving the selected puzzle',
                              command=self.sudoku_list_ui.start_selected_game)

        self.parent.parent.configure(menu=self.menu)

        self.game_ui.pack(side=tk.RIGHT)
        self.sudoku_list_ui.pack(side=tk.LEFT)
        self.pack()

    def set_sudoku(self, sudoku_game):
        # self.game_ui.destroy()
        self.ui_settings.set_N(sudoku_game.N)
        self.game_ui.set_game(game=sudoku_game)
        self.game_ui.pack(side=tk.RIGHT)


class GameListFrame(Frame):
    def __init__(self, parent: PickGameUI, sudokus_info, ui_settings):
        Frame.__init__(self, parent)
        self.parent = parent
        self.ui_settings = ui_settings
        self.sudokus_info = sudokus_info
        self._sorted_by = None # options are: 'number_of_clues', 'difficulty', 'tried_before', 'done_before'
        self._sorted_increasing = False

        self.picked_sudoku_game = None
        self._picked_sudoku_entry = None

        self._init_ui()


    def _init_ui(self):
        height = self.ui_settings.height
        side = self.ui_settings.selection_side

        canvas = Canvas(self, width = self.ui_settings.selection_width, height=self.ui_settings.selection_height-60)
        self.canvas = canvas

        self.number_of_cells = int(self.canvas['height']) // self.ui_settings.selection_side - 1 # number of cells displayed on each page
        self.number_of_pages = (len(self.sudokus_info)-1)//self.number_of_cells + 1 # ceiling division
        self.current_page = 1

        self.canvas.bind("<Button-1>", self._cell_clicked)

        self._draw_grid()
        self._draw_field_names()
        self._draw_info()
        self.canvas.pack(side=tk.TOP, padx=10, pady=(10, 0))

        self._page_label = tk.Label(self, text="Page "+str(self.current_page)+' out of '+str(self.number_of_pages))
        self._page_label.pack(side=tk.TOP)

        buttons_frame = tk.Frame(self)
        self._prev_button = tk.Button(buttons_frame, text='Previous', command=self.previous_page, state=tk.DISABLED)
        self._prev_button.pack(side=tk.LEFT)
        self._next_button = tk.Button(buttons_frame, text='Next', command=self.next_page, width=7)
        self._next_button.pack(side=tk.LEFT)
        buttons_frame.pack(side=tk.TOP)

    def start_selected_game(self):
        entry = self._picked_sudoku_entry
        if entry is None:
            pass
        else:
            self._picked_sudoku_entry['tried_before'] = True
            self.parent.parent.go_to_sudoku_solver(self.picked_sudoku_game, entry=entry)
            """if entry['tried_before']:
                initial_board = puzzle_generator.sudoku_from_string(entry[-1], N=entry[0])
                autosave_name = puzzle_generator.file_name(initial_board, N=entry[0])
                try:
                    self.parent.parent.load_game("save_files/"+autosave_name, entry=entry)
                    restart = False
                except:
                    restart = tk.messagebox.askyesno(title=None, message=
                    "Could not load the autosave, would you like to restart this sudoku?")
            else:
                restart = True
                self._picked_sudoku_entry['tried_before'] = True
            if restart:
                sudoku = puzzle_generator.sudoku_from_string(entry[-1], N=entry[0])
                game = sudoku_game.SudokuGame(initial_board=sudoku, N=sudoku.N)
                self.parent.parent.go_to_sudoku_solver(game, entry=entry)"""

    def previous_page(self):
        if self.current_page > 1:
            self.current_page -= 1
        if self.current_page <= 1:
            self._prev_button.configure(state=tk.DISABLED)
        if self.current_page < self.number_of_pages:
            self._next_button.configure(state=tk.NORMAL)
        self._page_label.configure(text="Page "+str(self.current_page)+' out of '+str(self.number_of_pages))
        self._draw_info()

    def next_page(self):
        if self.current_page < self.number_of_pages:
            self.current_page += 1
        if self.current_page >= 1:
            self._prev_button.configure(state=tk.NORMAL)
        if self.current_page >= self.number_of_pages:
            self._next_button.configure(state=tk.DISABLED)
        self._page_label.configure(text="Page "+str(self.current_page)+' out of '+str(self.number_of_pages))
        self._draw_info()

    def _draw_grid(self):
        height = self.ui_settings.selection_height - 100
        side = self.ui_settings.selection_side
        x0, x1 = 0, self.ui_settings.selection_width
        color = self.ui_settings.line_color
        for i in range(self.number_of_cells+2):
            if i == 0:
                y0 = y1 = i*side+2
            else:
                y0 = y1 = i*side
            self.canvas.create_line(x0, y0, x1, y1, fill=color, tags='selection_grid')

        y0, y1 = 0, (self.number_of_cells+1)*side
        self.canvas.create_line(2, 0, 2, y1, fill=color, tags='selection_grid')
        self.canvas.create_line(x1-1, 0, x1-1, y1, fill=color, tags='selection_grid')

        x = 0
        for i in range(len(self.ui_settings.selection_widths)-1):
            x += self.ui_settings.selection_widths[i]
            self.canvas.create_line(x, 0, x, y1, fill=color, tags='selection_grid')

    def _draw_info(self):
        self.canvas.delete("sudoku_info")
        height = self.ui_settings.height
        side = self.ui_settings.selection_side
        sudokus_to_display = self.sudokus_info[
                             self.number_of_cells*(self.current_page-1):
                             min(self.number_of_cells*self.current_page, len(self.sudokus_info))]

        font = tk.font.Font(**self.ui_settings.selection_font_info)
        for i in range(len(sudokus_to_display)):
            y = int((i+3/2)*side)
            x = self.ui_settings.selection_widths[0]//2
            text = str(sudokus_to_display[i]['number_of_clues'])
            self.canvas.create_text(
                x, y,
                text=text,
                tags="sudoku_info",
                fill='black',
                font=font
                #anchor = tk.W
            )

            x = self.ui_settings.selection_widths[1]//2 + self.ui_settings.selection_widths[0]
            text = str(puzzle_generator.complexity_from_numpy_entry(sudokus_to_display[i]))
            self.canvas.create_text(
                x, y,
                text=text,
                tags="sudoku_info",
                fill='black',
                font=font
                #anchor = tk.W
            )

            x += (self.ui_settings.selection_widths[2]+self.ui_settings.selection_widths[1])//2
            text = '' if not sudokus_to_display[i]['tried_before'] else "Y"
            self.canvas.create_text(
                x, y,
                text=text,
                tags="sudoku_info",
                fill='black',
                font=font
                #anchor = tk.W
            )

            x += (self.ui_settings.selection_widths[3]+self.ui_settings.selection_widths[2])//2
            text = '' if not sudokus_to_display[i]['done_before'] else 'Y'
            self.canvas.create_text(
                x, y,
                text=text,
                tags="sudoku_info",
                fill='black',
                font=font
                #anchor = tk.W
            )

    def _draw_field_names(self):
        self.canvas.delete("sudoku_info_names")
        height = self.ui_settings.height
        side = self.ui_settings.selection_side

        y = side//2
        x = self.ui_settings.selection_widths[0]//2
        text = 'Clues'
        font = tk.font.Font(**self.ui_settings.selection_font_info)
        self.canvas.create_text(
                x, y,
                text=text,
                tags="sudoku_info_names",
                fill='black',
                font=font
                #anchor=tk.W
            )

        x = self.ui_settings.selection_widths[1]//2 + self.ui_settings.selection_widths[0]
        text = 'Difficulty'
        self.canvas.create_text(
                x, y,
                text=text,
                tags="sudoku_info_names",
                fill='black',
                font=font
                #anchor=tk.W
            )

        x += (self.ui_settings.selection_widths[1] + self.ui_settings.selection_widths[2])//2
        text = 'Tried'
        self.canvas.create_text(
                x, y,
                text=text,
                tags="sudoku_info_names",
                fill='black',
                font=font
                #anchor=tk.W
            )

        x += (self.ui_settings.selection_widths[2] + self.ui_settings.selection_widths[3])//2
        text = "Solved"
        self.canvas.create_text(
                x, y,
                text=text,
                tags="sudoku_info_names",
                fill='black',
                font=font
                #anchor=tk.W
            )

    def _sort_sudokus_by(self, field):
        """
        :param field: valid field entries: 'number_of_clues', 'difficulty', 'tried_before', 'done_before'
        :return:
        """
        if field == self._sorted_by:
            self.sudokus_info[:]=np.flip(self.sudokus_info)
            self._sorted_increasing = not self._sorted_increasing
        else:
            if field == 'difficulty':
                difficulties = np.fromfunction(lambda i:
                                               puzzle_generator.complexity_from_numpy_entry(self.sudokus_info[i]),
                                               shape=(len(self.sudokus_info),),
                                               dtype=int
                                               ).astype(float)
                self.sudokus_info[:] = self.sudokus_info[np.argsort(difficulties)]
            elif field in ['number_of_clues', 'tried_before', 'done_before']:
                self.sudokus_info[:] = np.sort(self.sudokus_info, order=field)

        self._sorted_by = field
        self._draw_info()

    def set_sudoku(self, entry):
        if entry is None:
            sudoku = SudokuGame(np.zeros((9, 9)), N=3)
            new_game = SudokuGame(sudoku, sudoku.N)
        else:
            if not entry['tried_before']:
                sudoku = puzzle_generator.sudoku_from_string(entry[-1], N=entry[0])
                new_game = SudokuGame(sudoku, sudoku.N)
            else:
                try:
                    file_name = puzzle_generator.file_name(puzzle_generator.sudoku_from_string(entry[-1], N=entry[0]),
                                                           N=entry[0])
                    new_game = sudoku_game.load_game("save_files/"+file_name)
                    if new_game is None:
                        raise ValueError("incorrect file name or corrupted file")
                except:
                    sudoku = puzzle_generator.sudoku_from_string(entry[-1], N=entry[0])
                    new_game = SudokuGame(sudoku, sudoku.N)
                    tk.messagebox.showwarning(title='', message='Could not load the game')
                    entry['tried_before'] = False
        self.parent.set_sudoku(new_game)
        self.picked_sudoku_game = new_game
        self._picked_sudoku_entry = entry

    def _cell_clicked(self, event):
        x, y = event.x, event.y
        side = self.ui_settings.selection_side
        sudokus_to_display = self.sudokus_info[
                             self.number_of_cells*(self.current_page-1):
                             min(self.number_of_cells*self.current_page, len(self.sudokus_info))]


        if 0 <= x <= self.ui_settings.selection_width and side <= y <= side*(self.number_of_cells+1):
            i = y//side - 1
            if i < len(sudokus_to_display):
                self.set_sudoku(sudokus_to_display[i])

        if 0 <= y <= side-2: # corresponds to sorting
            # options are: 'number_of_clues', 'difficulty', 'tried_before', 'done_before'
            x0 = 0
            if 0 <= x <= self.ui_settings.selection_widths[0]:
                self._sort_sudokus_by('number_of_clues')
            elif sum(self.ui_settings.selection_widths[:1]) <= x <= sum(self.ui_settings.selection_widths[:2]):
                self._sort_sudokus_by('difficulty')
            elif sum(self.ui_settings.selection_widths[:2]) <= x <= sum(self.ui_settings.selection_widths[:3]):
                self._sort_sudokus_by('tried_before')
            elif sum(self.ui_settings.selection_widths[:3]) <= x <= sum(self.ui_settings.selection_widths[:4]):
                self._sort_sudokus_by('done_before')



