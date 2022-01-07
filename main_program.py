# Provides the main program functionality and allows one to transfer between different windows during the runtime.
# MainProgram object should be only initiated once and be kept alive during the UI runtime.
#
# One should be careful about changing existing functionality as most other objects in the UI have MainProgram as
# their parent (or parent of parent).
#
# TODO: maybe it is better to separate Frame functionality from frame_manager functionality of MainProgram.
#  It would take some effort to change that and does not seem worth it at the moment.
#
# Run the main function to execute the app.
# The puzzle banks and settings files will be overwritten during the run.
#

import numpy as np
import tkinter as tk
import tkinter.messagebox, tkinter.font, tkinter.filedialog
from tkinter import Tk, Canvas, Frame, Button
import os

from sudoku_game import SudokuGame
import sudoku_game
from main_menu_gui import MainMenuUI
import game_settings
from game_settings import UI_settings
from sudoku_game_gui import GameFrame
import puzzle_generator
import pick_game_ui
import settings_ui
import pop_up_messages

class MainProgram(Frame):
    def __init__(self, parent,
                 puzzle_list_file_name="puzzle_banks/puzzle_bank.txt",
                 settings_file_name="settings/settings.pkl"):
        """
        A class that manages all other Frames in the GUI.
        :param parent: tk.Root or a Frame
        :param puzzle_list_file_name: str or None. File name where the puzzle list is stored. If None, all
        :param settings_file_name: str. File name where the settings are stored. If no settings exist, or formatting is
            wrong, new settings file would be created at that location with default settings.
        """
        Frame.__init__(self, parent)
        self.parent = parent

        if puzzle_list_file_name is None:
            self.puzzle_list_file_names = [ "puzzle_banks/"+file_name for file_name in os.listdir('puzzle_banks')]
        else:
            self.puzzle_list_file_names = [puzzle_list_file_name]
        try:  # If debugging remove this  # Try loading puzzle list from a file.
            self.puzzle_list = puzzle_generator.read_from_files(self.puzzle_list_file_names)
        except Exception:
            tk.messagebox.showwarning(title="", message="Error reading puzzles from files")

        self.settings_file_name = settings_file_name
        try:  # If debugging remove this  # Try loading settings from the file
            self.ui_settings = game_settings.load_from_file(settings_file_name)
        except Exception:    # If could not load settings or no settings found, starts with default settings
            self.ui_settings = UI_settings()

        self.current_frame = MainMenuUI(self, ui_settings=self.ui_settings)
        self.pack()
        self.current_frame.pack()

        self.current_entry = None  # Tracks the sudoku entry currently played. None if playing custom game.
        self.state = 'main menu'  # Tracks the current window. Options are
        # 'main menu', 'solving sudoku', 'creating sudoku', 'picking sudoku', 'settings'


    def go_to_picking_sudoku(self):
        pick_ui = pick_game_ui.PickGameUI(parent=self, sudokus_info=self.puzzle_list, ui_settings=self.ui_settings)
        self.current_frame.destroy()

        self.current_frame = pick_ui
        self.state = 'picking sudoku'

    def go_to_sudoku_creator(self, N):
        empty_board = np.zeros((N*N, N*N))
        self.ui_settings.set_N(N)
        create_game = SudokuGame(empty_board, N=N)
        create_game.enable_create_sudoku_mode()
        self.current_frame.destroy()
        self.current_frame = GameFrame(parent=self, game=create_game, ui_settings=self.ui_settings)
        self.state = 'creating sudoku'


    def go_to_sudoku_solver(self, game, entry = None):

        self.current_frame.destroy()
        self.ui_settings.set_N(game.N)
        self.current_frame = GameFrame(parent=self, game=game, ui_settings=self.ui_settings, entry=entry)
        self.state = 'solving_sudoku'
        self.current_frame.pack()
        self.save_puzzle_list()
        self.save_puzzle_list()


    def go_to_the_main_menu(self):
        self.current_frame.destroy()
        self.current_frame = MainMenuUI(parent=self, ui_settings=self.ui_settings)
        self.state = 'main menu'

    def go_to_settings(self):
        self.current_frame.destroy()
        self.current_frame = settings_ui.SettingsUI(self, self.ui_settings)
        self.state = 'settings'

    def load_game(self, filename=None, entry=None):
        if filename is None:
            filename = tk.filedialog.askopenfilename(initialdir=os.getcwd()+'/save_files')
        if filename == '':
            return
        else:
            #try:
                new_game = sudoku_game.load_game(filename)
                self.go_to_sudoku_solver(new_game, entry=entry)
            #except:
                #self.go_to_the_main_menu()
                #tk.messagebox.showwarning(title='', message='Could not load the game')

    def save_puzzle_list(self):
        file_name = "puzzle_banks/puzzle_bank.txt"
        file_out = open(file_name, "w")
        if len(self.puzzle_list) > 0:
            for entry in self.puzzle_list:
                file_out.write(str(entry['N'])+','+str(entry['number_of_clues'])+
                               ','+str(entry['complexity_of_solution'])
                               +','+str(int(entry['tried_before']))
                               +','+str(int(entry['done_before']))
                               +'\n'+entry['sudoku_string']+'\n')

    def autosave_current_game(self):
        if self.state == 'solving_sudoku':
            self.current_frame.autosave_current_game()

    def save_settings(self):
        self.ui_settings.save_to_file(file_path=self.settings_file_name)


def main():
    root = Tk()
    root.geometry("")
    root.title('Just sudoku')
    root.resizable(False, False)
    root.option_add('*tearOff', tk.FALSE)

    program_path = os.getcwd()
    try:
        os.mkdir(program_path + "/save_files")
    except OSError:
        pass
    try:
        os.mkdir(program_path + "/save_files/autosaves")
    except OSError:
        pass
    try:
        os.mkdir(program_path + "/puzzle_banks")
    except OSError:
        pass
    try:
        os.mkdir(program_path + "/settings")
    except OSError:
        pass

    main_frame = MainProgram(root)

    root.mainloop()

    main_frame.save_puzzle_list()
    main_frame.autosave_current_game()
    main_frame.save_settings()

if __name__ == '__main__':
    main()