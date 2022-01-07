# Defines a UI for changing and visualizing settings in-game.
#
# TODO: add other options (font and line color most importantly).
#  Background color should be implemented in game_settings.py and all the Frames first.
#


import tkinter as tk
import copy
import sudoku_game
import sudoku_game_gui
import pop_up_messages
import game_settings

class SettingsUI(tk.Frame):
    def __init__(self, parent, ui_settings):
        """
        :param parent: Must be a FrameManager object
        :param ui_settings:
        """
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.new_settings = copy.deepcopy(ui_settings)

        self._init_ui()
        self._init_game()
        self.pack()



    def _init_ui(self):
        width = 200
        self.controls = tk.Frame(self, width=width)
        self.menu_controls = tk.Frame(self.controls)
        tk.Button(self.menu_controls, text='Save changes and return to the main menu', command=self.save_return_to_menu).pack(side='top', fill='x')
        tk.Button(self.menu_controls, text='Cancel changes and return to the main menu', command=self.return_to_menu).pack(side='top', fill='x')
        #tk.Button(self.menu_controls, text='Try changes', command=self.try_changes).pack(side='left', fill='x')

        self.menu_controls.pack(side='bottom', fill='x')


        self.buttons = tk.Frame(self.controls, width=width, height=500)
        tk.Button(self.buttons, text='Apply changes', command=self.apply_changes).pack(side='top', fill='x')

        self.buttons = tk.Frame(self.controls, width=width, height=500)
        tk.Button(self.buttons, text='Default settings', command=self.default_settings).pack(side='top', fill='x')


        self.initial_sudoku_size_scale = tk.Scale(self.buttons, label='Clues font size', from_=5, to=60,
                                             orient=tk.HORIZONTAL, length=width, showvalue=0,
                                                  command=lambda x: self.try_font_changes(),
                                        relief=tk.RIDGE)
        self.initial_sudoku_size_scale.pack(side='top', fill='x')

        self.guesses_size_scale = tk.Scale(self.buttons, label='Guesses font size', from_=5, to=60,
                                             orient=tk.HORIZONTAL, length=width, showvalue=0,
                                                  command=lambda x: self.try_font_changes(),
                                        relief=tk.RIDGE)
        self.guesses_size_scale.pack(side='top', fill='x')

        self.multiple_guesses_size_scale = tk.Scale(self.buttons, label='Multiple guesses font size', from_=3, to=30,
                                             orient=tk.HORIZONTAL, length=width, showvalue=0,
                                                  command=lambda x: self.try_font_changes(),
                                        relief=tk.RIDGE)
        self.multiple_guesses_size_scale.pack(side='top', fill='x')

        self.cell_side_scale = tk.Scale(self.buttons, label='Grid size', from_=15, to=90,
                                             orient=tk.HORIZONTAL, length=width, showvalue=0,
                                                  command=lambda x: self.try_changes(),
                                        relief=tk.RIDGE)
        self.cell_side_scale.pack(side='top', fill='x')

        self.buttons.pack(side='top', fill='y')

        self._transfer_settings_to_controls()

        self.controls.pack(side='left', fill='y')


    def _init_game(self):
        initial_board = [[0, 4, 3, 6, 1, 0, 5, 0, 0],
                        [0, 0, 0, 0, 0, 0, 0, 0, 0],
                        [0, 2, 0, 0, 4, 0, 0, 0, 0],
                        [0, 1, 0, 5, 0, 0, 0, 0, 6],
                        [4, 0, 7, 3, 0, 0, 0, 0, 1],
                        [0, 0, 8, 0, 0, 2, 4, 5, 0],
                        [5, 0, 0, 0, 8, 0, 0, 4, 0],
                        [7, 6, 0, 9, 2, 0, 0, 3, 5],
                        [0, 0, 1, 4, 3, 0, 9, 0, 0]]
        self.test_sudoku_game = sudoku_game.SudokuGame(initial_board=initial_board, N=3)
        self.test_sudoku_game.guesses[0][0] = [2, 8, 9]
        self.test_sudoku_game.guesses[2][3] = [4, 8, 9]
        self.test_sudoku_game.guesses[5][3] = [1]
        self.test_sudoku_game.guesses[7][2] = [4]
        self.sudoku_ui = sudoku_game_gui.SudokuUI(self, game=self.test_sudoku_game, ui_settings=self.new_settings)

    def _transfer_settings_to_controls(self):
        self.cell_side_scale.set(self.new_settings.side)
        self.multiple_guesses_size_scale.set(self.new_settings.multiple_guesses_font_info['size'])
        self.guesses_size_scale.set(self.new_settings.guess_font_info['size'])
        self.initial_sudoku_size_scale.set(self.new_settings.initial_sudoku_font_info['size'])


    def default_settings(self):
        old_hints_settings = copy.deepcopy(self.new_settings.hints)
        self.new_settings = game_settings.UI_settings()
        #  self.new_settings.hints = old_hints_settings
        self._transfer_settings_to_controls()
        self.try_changes()

    def apply_changes(self):
        self.parent.ui_settings = copy.deepcopy(self.new_settings)

    def try_changes(self):
        self.new_settings.set_side(self.cell_side_scale.get())
        self.sudoku_ui.update_ui_settings(self.new_settings)

    def try_font_changes(self):
        self.ask_to_confirm_exit = True
        self.new_settings.initial_sudoku_font_info['size'] = self.initial_sudoku_size_scale.get()
        self.new_settings.guess_font_info['size'] = self.guesses_size_scale.get()
        self.new_settings.multiple_guesses_font_info['size'] = self.multiple_guesses_size_scale.get()
        self.sudoku_ui.draw_sudoku()

    def save_return_to_menu(self):
        self.apply_changes()
        self.return_to_menu()

    def return_to_menu(self):
        self.parent.save_settings()
        self.parent.go_to_the_main_menu()
