# Main menu UI that allows user to navigate between different options.
#
# Parent has to be MainProgram instance, otherwise functionality is missing.

import tkinter as tk
from tkinter import Tk, Canvas, Frame, Button
import os

import pop_up_messages

class MainMenuUI(Frame):
    def __init__(self, parent, ui_settings):
        """
        :param parent: has to be a FrameManager object
        """
        Frame.__init__(self, parent, width =200, height=500)
        self.pack_propagate(0)
        self.parent = parent
        self.ui_settings = ui_settings

        self._init_ui()

    def _init_ui(self):
        self.pack()
        self.canvas = Canvas(self)

        self.load_autosave_button = Button(self.canvas, text='Load autosave',
                                           command=lambda: self.parent.load_game(filename="save_files/autosave.pkl"))

        self.start_button = Button(self.canvas, text='Start a new game',
                                   command=self.parent.go_to_picking_sudoku)

        self.create_puzzle_button = Button(self.canvas, text='Create a custom game',
                                    command=lambda: self.parent.go_to_sudoku_creator(N=3) )

        self.load_button = Button(self.canvas, text='Load a game', command=self.parent.load_game )

        self.settings_button = Button(self.canvas, text='Settings', command=self.parent.go_to_settings )

        pop_up_messages.Hint(self.ui_settings.hints.starting_menu_hints_info).show(parent=self, relx=0.5,
                                                                             rely=0.8)


        if os.path.exists("save_files/autosave.pkl"):
            self.load_autosave_button.pack(side='top', fill='x', padx=10, pady=10)
        self.start_button.pack(side='top', fill='x', padx=10, pady=10)
        self.create_puzzle_button.pack(side='top', fill='x', padx=10, pady=10)
        self.load_button.pack(side='top', fill='x', padx=10, pady=10)
        self.settings_button.pack(side='top', fill='x', padx=10, pady=10)

        self.canvas.pack()