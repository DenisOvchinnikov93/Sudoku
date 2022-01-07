# This module is responsible for keeping the settings, as well as settings saving and loading functionality.
#
# Settings include: font sizes, types and colors; line colors and thicknesses; cells sizes and margins, N, and hints.
#
# Since UI_settings object is passed to all frames in the app, you should be careful about changing existing
# implementations.
#
# TODO: separate settings into different objects depending on the Frame they are used for.
#  This should make access easier and more intuitive.
#


import pickle
import os


class UI_settings():
    def __init__(self, margin=20, side=40, line_color='gray', thick_line_color='black', N=3):
        self.N=N
        self.width = self.height = margin * 2 + side * (N * N)
        self.margin = margin  # Pixels around the board
        self.side = side  # Side of every board cell

        self.always_allow_computer_help = False

        self.line_color = line_color
        self.thick_line_color = thick_line_color
        self.thick_line_thickness = 2
        self.initial_sudoku_color = 'black'
        self.initial_sudoku_font_info = {'family': "Comic Sans MS",
                                 'size': 20,
                                 'weight': "bold"}

        self.guess_color = 'blue'
        self.guess_font_info = {"family": "Comic Sans MS",
                                 "size": 20,
                                 "weight": "normal"}

        self.multiple_guesses_font_info = {'family': "Comic Sans MS",
                                 'size': 11,
                                 'weight': "normal"}

        self.multiple_guesses_separator = ','

        self.selection_font_info = {'family': "Comic Sans MS",
                                 'size': 7,
                                 'weight': "normal"}
        self.selection_side = 30

        self.selection_widths = [30, 50, 30, 30]
        self.selection_width = sum(self.selection_widths)
        self.selection_height = self.height

        self.hints = HintsUI()

    def set_side(self, side):
        self.side = side
        self.width = self.height = self.margin * 2 + side * (self.N * self.N)

    def set_N(self, N):
        self.N = N
        self.width = self.height = self.margin * 2 + self.side * (N * N)

    def save(self):
        self.save_to_file(self.file_path)

    def save_to_file(self, file_path):
        with open(file_path, 'wb') as out_file:
            pickle.dump(self, out_file)


def load_from_file(file_path):
    """
    :param file_path: path to a pickled UI_settings object.
    :return: UI_settings
    """
    with open(file_path, 'rb') as in_file:
        return pickle.load(in_file)


class HintInfo:
    def __init__(self, text, disabled=False):
        self.text = text
        self.disabled = disabled


class HintsUI:
    def __init__(self):
        """
        An object to store all the hint messages and remember hint display preferences between runs.
        """
        self.save_hint_info = HintInfo('You can save games using any name you like and load them later.')

        self.autosave_hint_info = HintInfo('Your games are autosaved every 5 minutes and on game exit. '
                                           '\n You can also autosave them manually. '
                                                '\n You can easily load last autosave from the main menu. ')

        self.new_game_hint_info = HintInfo('Start new game to solve this sudoku!')

        self.starting_menu_hints_info = HintInfo(text='You can select sudoku\n from a database'
                                                             '\n or load your saved game later.'
                                                             '\n You can also adjust settings, '
                                                             '\n including the size\n and color of sudokus.')

        self.arrow_control_hint_info = HintInfo('You can switch between cells with arrow keys'
                                                            '\n or simply by using your mouse.')

        self.multiple_guesses_hint_info = HintInfo('You can use / . , or space to write multiple guesses '
                                                               'in a cell.')

        self.settings_exist_hint_info = HintInfo('You can change appearance of your puzzles in settings.\n '
                                                             'Your preferences will be saved next time you play!')

        self.sorting_games_hint_info = HintInfo('Click "Difficulty" field to order by difficulty.\n '
                                                'Click on any sudoku to preview it.')


if __name__ == "__main__":
    # Restores settings to default
    program_path=os.getcwd()
    try:
        os.mkdir(program_path+"/settings")
    except OSError:
        pass

    ui_settings = UI_settings()
    ui_settings.save_to_file("settings/settings.pkl")