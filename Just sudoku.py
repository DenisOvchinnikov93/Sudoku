import tkinter as tk
import os
import frame_manager


def main():
    root = tk.Tk()
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

    main_frame = frame_manager.MainProgram(root)

    root.mainloop()

    main_frame.save_puzzle_list()
    main_frame.autosave_current_game()
    main_frame.save_settings()

if __name__ == '__main__':
    main()