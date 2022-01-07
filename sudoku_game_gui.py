# This implements the main frame for solving sudokus, GameFrame. The sudoku itself is displayed in SudokuUI Frame; the
# GameFrame is responsible for menus, buttons and interacting with the MainProgram
#
# Parent of GameFrame must be a MainProgram object. It can be replaced by arbitrary Frame
# if menu and loading a game options are disabled.
#
# GameFrame is used in in sudoku creation window.
# SudokuUI is also used in the settings window to preview settings, and in sudoku selection window to preview sudoku.
#
# TODO: refactor rename file (original name is not discriptive any more)


import tkinter as tk
import tkinter.messagebox, tkinter.font, tkinter.filedialog, tkinter.simpledialog
from tkinter import Tk, Canvas, Frame, Button
from collections import OrderedDict

import random
import itertools
import numpy as np
import os

from sudoku import Sudoku
from sudoku_game import SudokuGame
import sudoku_game
from game_settings import UI_settings
import puzzle_generator
import pop_up_messages


class GameFrame(Frame):
    def __init__(self, parent, game, ui_settings, entry=None):
        """
        :param parent: Must be FrameManager Frame.
        :param game: SudokuGame.
        :param ui_settings: UISettings
        :param entry: numpy array entry for tracking solving sudoku
        """
        self.parent = parent
        self.game = game
        self.ui_settings = ui_settings
        self.entry = entry
        self.allow_computer_help = self.ui_settings.always_allow_computer_help

        Frame.__init__(self, parent)

        self.sudoku_ui = SudokuUI(parent=self, game=game, ui_settings=ui_settings)
        self.game_buttons_ui = GameButtonsUI(parent=self)
        self.other_buttons_ui = OtherButtonsUI(parent=self)
        self.create_sudoku_ui = CreateSudokuButtonsUI(parent=self)

        self.sudoku_ui.pack(side='top', fill='x', pady=0)

        if not game.create_sudoku_mode_is_enabled():
            self.game_buttons_ui.pack(after=self.sudoku_ui, fill='x', padx=self.ui_settings.margin, pady=(0, 10))
        else:
            self.create_sudoku_ui.pack(after=self.sudoku_ui, fill='x', padx=self.ui_settings.margin, pady=(0, 10))
        self.pack()

    def clear_all_guesses(self):
        title = ''
        text = "Are you sure you want to clear all your guesses?"
        options = ['Yes', 'No']
        confirmation = tkinter.messagebox.askyesno(title=title, message=text)
        if confirmation:
            self.sudoku_ui.clear_all_guesses()

        """title = ''
        text = "Are you sure you want to clear all your guesses?"
        options = OrderedDict([(True,  'Yes'), (False, 'No')])
        confirmation = my_yes_no_messagebox(self, title=title, message=text, options=options)
        if confirmation:
            self.sudoku_ui.clear_all_guesses()"""

    def submit_answers(self):
        correct = self.game.check_if_solution_is_full_and_correct()
        if correct == 'Not all cells filled':
            text = 'Not all cells are completed, check your puzzle!'
            tkinter.messagebox.showwarning(title='', message=text)

        elif not correct:
            text = 'Your solution is not correct'
            tkinter.messagebox.showwarning(title='', message=text)

        elif correct:
            text = 'Your solution is correct, good job!'
            if self.entry is not None:
                self.entry['done_before'] = True
                self.parent.save_puzzle_list()

            tkinter.messagebox.showinfo(message=text)

    def reveal_correct_guess_in_selected_cell(self):
        i, j = self.sudoku_ui.row, self.sudoku_ui.col
        if i == -1 or j == -1:
            pass
        else:
            value = self.game.solutions[0][i][j]
            self.game.guesses[i][j] = [value]
            self.sudoku_ui.draw_sudoku()

    def check_all_current_guesses(self):
        N = self.game.N
        correct = True
        for i, j in itertools.product(range(N*N), range(N*N)):
            guesses = self.game.guesses[i][j]
            if len(guesses) == 1 and guesses[0] != 0:
                if guesses[0] != self.game.solutions[0][i][j]:
                    correct = False
                    break
        if correct:
            pop_up_messages.PopUpWindow(text="All guesses are correct so far!").show(self)
        else:
            pop_up_messages.PopUpWindow(text="Some guesses are not correct.\n Check your logic!").show(self)

    def start_a_game_with_current_setup(self):
        N = self.ui_settings.N
        table = np.zeros((N*N, N*N), dtype='int16')
        all_ok = True  # Keeps track that everything is ok or we are willing to ignore exceptions.
        #  Checks that all entries have only one option and that solution is unique (user can force to ignore that).

        # check that the formatting is correct and enter guesses into NxN array table.
        for i, j in itertools.product(range(N*N), range(N*N)):
            if len(self.game.guesses[i][j]) > 1:
                text = 'Some of the guesses have multiple options, would you like to remove them?'
                all_ok = tk.messagebox.askyesno(message=text)
                # Does not happen with the current implementation since we do not allow multiple guesses
                # if game.create_sudoku_mode_is_enabled()
                if all_ok:
                    for row, col in itertools.product(range(N*N), range(N*N)):
                        # Not really a quadruple loop complexity since this can only happen once for a given table.
                        if len(self.game.guesses[row][col]) > 1:
                            self.game.guesses[row][col] = [0]
                else:
                    break
            elif len(self.game.guesses[i][j]) == 0:
                table[i][j] = 0
            else:
                table[i][j] = self.game.guesses[i][j][0]
        if not all_ok:
            return None

        sudoku = Sudoku(table, N)
        complexity_tracker = []
        solutions = sudoku.solve(maximal_number_of_solutions=2, number_of_guesses_tracker=complexity_tracker)
        if len(solutions) == 0:
            tk.messagebox.showwarning(message='The puzzle has no solutions, check it!')
            return None
        elif len(solutions) > 1:
            all_ok = tk.messagebox.askyesno(message="The puzzle has multiple solutions, do you want to proceed?")

        if all_ok:
            if len(solutions) == 1 and self.create_sudoku_ui.include_new_game_in_the_puzzle_bank.get():
                string = puzzle_generator.to_string(sudoku, tried_before=True, solution_unique=True,
                                           solution_complexity_precomputed=complexity_tracker[0])
                new_entry = puzzle_generator.string_to_new_numpy_entry(string)
                self.parent.puzzle_list = np.append(self.parent.puzzle_list, new_entry[0])

            new_game = SudokuGame(table, N=self.ui_settings.N)
            self.parent.go_to_sudoku_solver(new_game)

    def return_to_main_menu(self):
        if not self.game.create_sudoku_mode_is_enabled():
            self.autosave_current_game()
        self.parent.go_to_the_main_menu()

    def autosave_current_game(self):
        name = puzzle_generator.file_name(self.game.initial_board, N=self.game.N)
        self.game.save_game("save_files/"+name)
        self.game.save_game("save_files/autosave.pkl")

    def save_current_game(self):
        file_name = tk.simpledialog.askstring(title='Save game', prompt='Enter save name')
        if file_name is None:
            return None

        if os.path.exists("save_files/autosave_"+file_name+".pkl"):
            replace = tk.messagebox.askyesno(
                title='', message="A save file with chosen name already exists, would you like to replace it?")
            if replace:
                self.game.save_game("save_files/"+file_name+".pkl")
            else:
                pass
        else:
            self.game.save_game("save_files/" + file_name + ".pkl")

    def autosave(self):
        self.autosave_current_game()
        self.after(30000, self.autosave)


class CreateSudokuButtonsUI(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent

        self._init_ui()

    def _init_ui(self):
        clear_board_button = Button(self, text='Reset the board', command=self.parent.clear_all_guesses, width=0)
        clear_board_button.pack(side='left')

        start_new_game_button = Button(self, text='Start a game with this setup',
                                       command=self.parent.start_a_game_with_current_setup, width=0)
        start_new_game_button.pack(side='left', padx=10)

        self.include_new_game_in_the_puzzle_bank = tk.BooleanVar(value=False)
        include_new_game_in_the_puzzle_bank_button = tk.Checkbutton(self, text='Upload the puzzle to the puzzle bank\n'
                                                                    '(only if there is unique solution)',
                                                                    variable=self.include_new_game_in_the_puzzle_bank,
                                                                    onvalue=True, offvalue=False
                                                                    )
        include_new_game_in_the_puzzle_bank_button.pack(side='right')


class GameButtonsUI(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent

        self._init_ui()

    def _init_ui(self):
        clear_answers_button = Button(self, text='Clear all guesses', command=self.parent.clear_all_guesses, width=0)
        clear_answers_button.pack(side='left')

        check_answers_button = Button(self, text='Check if the solution is correct',
                                      command=self.parent.submit_answers, width=0)
        check_answers_button.pack(side='left', padx=10)


class OtherButtonsUI(tk.Menu):
    def __init__(self, parent):
        tk.Menu.__init__(self, parent)

        self.parent = parent

        self.add_command(label='Main menu', command=self.parent.return_to_main_menu)

        if not self.parent.game.create_sudoku_mode_is_enabled():
            self.add_command(label='Auto save', command=self.parent.autosave_current_game)
            self.add_command(label='Save', command=self.parent.save_current_game)
            self.add_command(label='Load', command=self.parent.parent.load_game)

            computer_help_menu = tk.Menu(self)
            computer_help_menu.add_command(label='Check if all entered guesses are correct',
                                            command=self.parent.check_all_current_guesses)
            computer_help_menu.add_command(label='Reveal answer for the selected cell',
                                            command=self.parent.reveal_correct_guess_in_selected_cell)
            self.add_cascade(menu=computer_help_menu, label='Computer help')

        self.parent.parent.parent.configure(menu=self)

    def callback_enable_computer_button_check(self):
        if self.enable_computer_help_check.get():
            self.parent.enable_computer_help()
        else:
            self.parent.disable_computer_help()


class SudokuUI(Frame):
    def __init__(self, parent, game, ui_settings):
        self.ui_settings = ui_settings

        self.game = game
        self.N = self.game.N
        self.parent = parent
        Frame.__init__(self, parent)
        self._enabled = True

        self.row, self.col = -1, -1  # position of the cell currently selected, -1, -1 for no selection

        self._number_of_clicks = 0 # Tracking number of clicks to display hints

        self._init_ui()

    def disable(self):
        self._enabled = False

    def _init_ui(self):
        self.pack(fill='both', expand=1)

        width, height = self.ui_settings.width, self.ui_settings.height
        self.canvas = Canvas(self, width=width, height=height, highlightthickness=0)
        self.canvas.pack(fill='both', side='top')

        self._draw_grid()
        self.draw_sudoku()

        self.canvas.bind("<Button-1>", self._cell_clicked)
        self.canvas.bind("<Key>", self._key_pressed)

    def clear_all_guesses(self):
        N=self.N
        for i, j in itertools.product(range(N*N), range(N*N)):
            if self.game.initial_board[i][j] == 0:
                self.game.guesses[i][j] = [0]
        self.draw_sudoku()

    def _draw_grid(self):
        self.canvas.delete('grid')
        N = self.N
        for i in range(N * N + 1):
            color = self.ui_settings.thick_line_color if i % N == 0 else self.ui_settings.line_color

            margin = self.ui_settings.margin
            side = self.ui_settings.side
            height, width = self.ui_settings.height, self.ui_settings.width
            thickness = 1 if i % N else self.ui_settings.thick_line_thickness

            x0 = margin + i * side
            y0 = margin
            x1 = margin + i * side
            y1 = height - margin
            self.canvas.create_line(x0, y0, x1, y1, fill=color, tags='grid', width=thickness)

            x0 = margin
            y0 = margin + i * side
            x1 = width - margin
            y1 = margin + i * side
            self.canvas.create_line(x0, y0, x1, y1, fill=color, tags='grid', width=thickness)

    def draw_sudoku(self):
        self.canvas.delete('numbers')
        N = self.N
        for i, j in itertools.product(range(N * N), range(N*N)):
            guesses = self.game.guesses[i][j]
            margin = self.ui_settings.margin
            width, height = self.ui_settings.width, self.ui_settings.height
            side = self.ui_settings.side

            x, y = margin+side*(i+1/2), margin+side*(j+1/2)

            if self.game.initial_board[i][j] != 0:
                # TODO: implement initial sudoku with multiple clues
                self.canvas.create_text(
                    x, y,
                    text=str(self.game.initial_board[i][j]),
                    tags="numbers",
                    fill = self.ui_settings.initial_sudoku_color,
                    font = tk.font.Font(**self.ui_settings.initial_sudoku_font_info)
                )

            elif len(guesses) == 1 and guesses[0] != 0:
                self.canvas.create_text(
                    x, y,
                    text=str(guesses[0]),
                    tags="numbers",
                    fill=self.ui_settings.guess_color,
                    font=tk.font.Font(**self.ui_settings.guess_font_info)
                )

            elif len(guesses) == 0 or (len(guesses) == 1 and guesses[0] == 0):
                pass

            elif len(guesses) > 1:
                if guesses[-1]!=0:
                    text = ','.join(map(str,guesses))
                else:
                    text = ','.join(map(str, guesses[:-1]))+','
                x, y = margin + side * (i + 1 / 2), margin + side * (j + 1)-2
                self.canvas.create_text(
                    x, y,
                    text=text,
                    tags="numbers",
                    fill=self.ui_settings.guess_color,
                    font=tk.font.Font(**self.ui_settings.multiple_guesses_font_info),
                    width=side-2,
                    anchor=tk.S
                )

    def _cell_clicked(self, event):
        x, y = event.x, event.y

        N = self.N
        margin = self.ui_settings.margin
        width, height = self.ui_settings.width, self.ui_settings.height
        side = self.ui_settings.side

        if margin < x < width - margin and margin < y < height - margin:
            self.canvas.focus_set()

            row, col = int((x - margin) / side), int((y - margin) / side)

            if (row, col) == (self.row, self.col):
                self.row, self.col = -1, -1
            else:
                self.row, self.col = row, col
        self._draw_cursor()

    def _draw_cursor(self):
        self.canvas.delete("cursor")
        i, j = self.row, self.col
        margin = self.ui_settings.margin
        side = self.ui_settings.side
        width, height = self.ui_settings.width, self.ui_settings.height
        if (i, j) != (-1, -1):
            x_0, y_0 = margin + side * i + 1, margin + side * j + 1
            x_1, y_1 = margin + side * (i + 1) - 1, margin + side * (j + 1) - 1
            self.canvas.create_rectangle(x_0, y_0, x_1, y_1, outline='red', tag='cursor')

    def _key_pressed(self, event):
        """
        Processes keyboard inputs from the user.
        :param event:
        :return:
        """
        i, j = self.row, self.col
        N = self.N

        if not self._enabled:
            pop_up_messages.Hint(self.ui_settings.hints.new_game_hint_info).show(self.canvas)
            return None

        if i >= 0 and j >= 0 and self.game.initial_board[i][j] == 0:
            current_guesses = self.game.guesses[i][j]
            if i >= 0 and j >= 0 and event.char in list('123456789'):
                if N>3:
                    new_guess = int(str(current_guesses[-1])+event.char)
                    if new_guess > N*N:
                        new_guess = int(event.char)
                else:
                    new_guess = int(event.char)

                self.game.guesses[i][j][-1] = new_guess

            elif event.keysym in ['BackSpace']:
                if len(current_guesses) == 1 and current_guesses[0] == 0:
                    pass
                elif len(current_guesses) == 1:
                    self.game.guesses[i][j] = [0]
                elif len(current_guesses) > 1:
                    if current_guesses[-1] == 0:
                        self.game.guesses[i][j].pop()
                    else:
                        self.game.guesses[i][j][-1] = 0

            elif event.keysym in ['Delete']:
                if self.game.initial_board[i][j] == 0:
                    self.game.guesses[i][j] = [0]

            elif event.char in [',', '/', ' '] and not self.game.create_sudoku_mode_is_enabled():
                if current_guesses[-1] == 0:
                    pass
                else:
                    current_guesses.append(0)

        if event.keysym in ['Up', 'Down', 'Left', 'Right']:
            directions_dict = {'Up': (0, -1),
                               'Down': (0, 1),
                               'Right': (1, 0),
                               'Left': (-1, 0)}
            dx, dy = directions_dict[event.keysym]
            if 0 <= i+dx < N*N and 0 <= j+dy < N*N:
                self.col += dy
                self.row += dx

        self.draw_sudoku()
        self._draw_cursor()

        self._number_of_clicks = (self._number_of_clicks + 1)%20
        if self._number_of_clicks == 3:
            pop_up_messages.Hint(self.ui_settings.hints.arrow_control_hint_info).show(self)

    def set_game(self, game):
        self.game = game
        if self.N != self.game.N:
            self.N = self.game.N
            self.col = self.row = -1
            self.update_ui_settings(self.ui_settings)
        else:
            self.draw_sudoku()

    def update_ui_settings(self, new_settings):
        self.ui_settings = new_settings
        width, height = self.ui_settings.width, self.ui_settings.height
        self.canvas.configure(width=width, height=height)

        self._draw_grid()
        self.draw_sudoku()
        self._draw_cursor()
