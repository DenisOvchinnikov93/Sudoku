#  This is used to generate an executable file. running the gui.
#
#

import PyInstaller.__main__
import os


def main():
    program_path = os.getcwd()
    puzzle_bank_path = os.path.join(program_path, "puzzle_banks")
    PyInstaller.__main__.run([
        'Just sudoku.py',
        '--onedir',
        '--windowed',
        '--add-data=puzzle_banks/*;puzzle_banks/',
        '--add-data=README.*;.'
    ])


if __name__ == '__main__':
    main()

