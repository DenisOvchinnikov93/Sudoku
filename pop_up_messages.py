# Implements custom pop up messages for sudoku interface.
#
# Classes are: Hint for hints and interactive pop-ups, and PopUpWindow for simple non-interactive message.
# Both classes support .show(parent, **kwargs) to display them on a parent Frame. Parent Frame is NOT disabled while
# # the message is active.
#
# TODO: Change all popup-messages and dialog windows to this type.
# TODO: Make Hint and PopUpMessage classes inherit from the common class.
#
#


import tkinter as tk
import game_settings

class Hint():
    def __init__(self, hint_info: game_settings.HintInfo, options='standard'):
        """
        Creates a Hint object to store a certain hint.
        :param hint_info: HintInfo object with fields .text, .disabled
        :param options: dict of the form {"text to display": command} or 'standard'. Only 'standard' is fully tested!
            Standard corresponds to options Ok (dismisses the hint) and "Never show again" (dismisses the hint forever).
            TODO: test arbitrary dict options and change all warnings in the program to this class.
        """
        self.text = hint_info.text
        self.hint_info = hint_info
        if options == 'standard':
            self.options = {'Ok': self.ok, 'Never show again': self.never_show_again}
        else:
            self.options = options
        self.frame = None

    def never_show_again(self):
        self.hint_info.disabled = True

        self.ok()

    def ok(self):
        if self.frame is not None:
            self.frame.destroy()
            self.frame = None

    def show(self, parent, x=None, y=None, relx=None, rely=None, anchor='center'):
        """
        Displays the hint on a parent Frame at a specified location. If no location is specified, it is located in the
        center. Parent Frame is NOT disabled while the message is active.
        :param parent: Frame
        :param x: int or None
        :param y: int or None
        :param relx: float or None
        :param rely: float or None
        :param anchor: see tk.Frame.place() anchor options.
        :return:
        """
        if self.hint_info.disabled:
            return None
        else:
            self.frame = tk.Frame(parent, highlightbackground='black', highlightthickness=1)
            tk.Label(master=self.frame, text=self.text).pack(side=tk.TOP)
            for option_text, option_command in self.options.items():
                tk.Button(self.frame, text=option_text, command=option_command).pack(side=tk.LEFT, padx=5, pady=5)
            if x is None or y is None:
                if relx is None or rely is None:
                    relx = rely = 0.5
                self.frame.place(relx=relx, rely=rely, anchor=anchor)
            else:
                self.frame.place(x=x, y=y, anchor=anchor)


class PopUpWindow():
    def __init__(self, text, ok_button='standard'):
        self.text = text
        if ok_button == 'standard':
            self.options = {'Ok': self.ok}
        else:
            self.options = ok_button
        self.frame = None

    def ok(self):
        if self.frame is not None:
            self.frame.destroy()
            self.frame = None

    def show(self, parent, x=None, y=None, relx=None, rely=None, anchor='center'):
        self.frame = tk.Frame(parent, highlightbackground='black', highlightthickness=1)
        tk.Label(master=self.frame, text=self.text).pack(side=tk.TOP)
        for option_text, option_command in self.options.items():
            tk.Button(self.frame, text=option_text, command=option_command).pack(side=tk.BOTTOM, padx=5, pady=5)
        if x is None or y is None:
            if relx is None or rely is None:
                relx = rely = 0.5
            self.frame.place(relx=relx, rely=rely, anchor=anchor)
        else:
            self.frame.place(x=x, y=y, anchor=anchor)