# Puzzle generating and recording utilities.
#
# This file contains all functions responsible for generating new sudokus, recording them to files,
# reading them from files, and converting between different formats.
#
# Formats are:
# strings (for recording in puzzle banks),
# numpy entries (for keeping puzzle bank in the memory during run time)
# Sudoku (for working with a specific sudoku during run time)
# TODO: designate formatting to Sudoku methods instead.
# TODO: (quality of life) change numpy entries to custom class (say SudokuInfo) for more natural interface.
#
# Strings and numpy entries are intended to use only for sudokus with unique solution, but they do not know solutions.
# Because of that loading a sudoku from a string might take several seconds.
# TODO: Include solution information into a sudoku, otherwise loading hard 16x16 sudokus takes very long time!
#
# Run the main script for a simple GUI to generate new puzzles. The UI is unresponsive during generating time.


import random
import time
import numpy as np
import itertools
import copy
import os
import tkinter as tk
import pop_up_messages

from sudoku import Sudoku


def read_from_files(file_names, separator=','):
    sudoku_info_list = []
    for file_name in file_names:
        with open(file_name, 'r') as in_f:
            while True:
                line1 = in_f.readline()
                if not line1:
                    break
                elif line1 == '\n' or line1[0] == "#":
                    continue
                else:
                    try:
                        line2 = in_f.readline()
                        sudoku_info_list.append(full_information_from_lines(line1, line2, separator=','))
                        sudoku = sudoku_from_string(line2, N=sudoku_info_list[-1][0], separator=',')
                    except:
                        #raise Warning("Couldn't process a string "+line1+line2)
                        sudoku_info_list.pop()
                        pass

    sudokus_info = np.array(sudoku_info_list, dtype=[('N', 'uint8'),
                                       ('number_of_clues', 'int16'),
                                       ('complexity_of_solution', 'uint8'),
                                       ('tried_before', '?'),
                                       ('done_before', '?'),
                                       ('sudoku_string', 'object')])

    return sudokus_info

def complexity_from_numpy_entry(entry):
    """
    Rough estimation of Sudoku difficulty.
    :param entry: numpy entry of the form [('N', 'uint8'),
                                       ('number_of_clues', 'int16'),
                                       ('complexity_of_solution', 'uint8'),
                                       ('tried_before', '?'),
                                       ('done_before', '?'),
                                       ('sudoku_string', 'object')]
    :return: int
    """
    return (entry['N'] == 3).astype('int')*(entry['complexity_of_solution']*5-entry['number_of_clues']+40)*2 + \
           (entry['N'] == 2).astype('int')*10 + \
           (entry['N'] > 3).astype('int')*100
    # Changed from normal if-else statement to make the function broadcastable. Old code below.
    # If the function is not broadcastable, deifficulty calculation is pick_gamy.py must be changed.

    #   if entry['N'] == 3:
        #   return max((entry['complexity_of_solution']*5-entry['number_of_clues']+40)*2, 0)
    #   elif entry['N'] == 2:
        #   return 10
    #   else:
        #   return 100

def generate_to_file(file_path, append_to_existing_file = True, overwrite_file=False,
                     number_of_sudokus=100, time_for_each_sudoku=10, N=3, target_missing_cells=float(61/81),
                     minimal_missing_cells=float(0), passing_difficulty=100):
    """
    Generates a target number of sudokus to a target file.
    :param file_path: File path to output generated sudokus.
    append_to_existing_file: If True, will append to existing file.
    :param overwrite_file: If False will look for a different file name or append.
        If True, and append_to_existing_file is False, will overwrite the file.
    :param number_of_sudokus: Number of sudokus to generate
    :param time_for_each_sudoku: Time limit for generation of each sudoku.
        Might be 1-2 seconds longer in practice for sudokus with less than 25 hints.
    :param N: size of a cell of each sudoku. 3 is standard/
    :param target_missing_cells: float. Target missing cells proportion.
    :param minimal_missing_cells: float. Sudokus with less passing cells proportion will not be recorded.
    :param passing_difficulty: int. Minimal difficulty after which all sudokus will be entered
    :return:
    """
    found_path = True
    if not append_to_existing_file and os.path.exists(file_path) and not overwrite_file:
        found_path = False
        dot_pos = file_path.find(".")
        for i in range(100):
            if not os.path.exists(file_path[:dot_pos]+"("+str(i)+")"+file_path[dot_pos:]):
                file_path = file_path[:dot_pos]+"("+str(i)+")"+file_path[dot_pos:]
                found_path = True
                break
    if not found_path:
        return None
    else:
        start_time = time.time()
        number_of_recorded_sudokus = 0
        for sudoku_number in range(number_of_sudokus):
            sudoku = generate_sudoku_from_a_full_puzzle(
                N=N, proportion_of_missing_cells=target_missing_cells, maximal_time=time_for_each_sudoku)[1]
            string = to_string(sudoku)
            difficulty = complexity_from_numpy_entry(string_to_new_numpy_entry(string))
            if ((sudoku.number_of_clues())/(N**4)) <= 1 - minimal_missing_cells or \
                    difficulty[0] > passing_difficulty:
                number_of_recorded_sudokus += 1
                with open(file_path, "a") as out_file:
                    out_file.write(string+"\n")
                print(f"Sudoku {str(sudoku_number)} with {sudoku.number_of_clues()} "
                      f"clues was generated in {time.time()-start_time} s. Difficulty is {difficulty[0]}\n")
            else:
                pass
                #print(f"Sudoku {str(sudoku_number)} with {sudoku.number_of_clues()} clues"
                      #f" and difficulty {difficulty[0]}"
                      #f" was generated in {time.time()-start_time} s."
                      #f" but was discarded.\n")

    print(f"Total {number_of_recorded_sudokus} were written in {time.time() - start_time}")
def file_name(board, N):
    ans = 'autosaves/autosave_'
    for i in range(N*N):
        for j in range(N*N):
            ans+= str(board[i][j])
    ans = ans[:100]
    ans += '.pkl'
    return ans

def file_name_from_entry(entry):
    ans = 'autosaves/autosave_'
    line_2 = entry[-1]
    line_2.strip('\n')
    line_2.replace(',', '')
    ans = (ans+line_2)[:100]
    return ans + '.pkl'

def to_string(sudoku: Sudoku, tried_before=False, done_before=False, separator=",", solution_unique=False,
              solution_complexity_precomputed=None):
    """
    If sudoku is solvable, provides a string representation of it, and information about it, else returns empty string.
    Format is "N,number_of_clues,complexity_of_solution,tried_before,done_before \n Sudoku".
    Sudoku is a sequence of N**4 numbers separated by separator.
    tried_before and
    Any other information can be added at the end of the string.
    :param sudoku: Sudoku
    :param tried_before: bool
    :param done_before: bool
    :param separator: str
    :param solution_unique: bool. If we know that the solution is unique, might be specified to True.
    :param solution_complexity_precomputed: int or None. If None, will use that complexity. Speeds up the generation if
        the solution was pre-computed. solution_unique must be True for this to take effect.
    :return: str
    """
    solution_complexity = []
    if solution_unique and solution_complexity_precomputed is not None:
        solution_complexity = [solution_complexity_precomputed]
    else:
        solutions = sudoku.solve(number_of_guesses_tracker=solution_complexity)
        if len(solutions) == 0:
            return ""
    N = sudoku.N
    out_str = ""

    done_before = 1 if done_before else 0
    tried_before = 1 if tried_before else 0

    out_str += f"{sudoku.N}{separator}{sudoku.number_of_clues()}" \
               f"{separator}{solution_complexity[0]}{separator}{tried_before}{separator}{done_before}\n"

    for i in range(N * N):
        for j in range(N * N):
            if i == 0 and j == 0:
                out_str += str(sudoku[i][j])
            else:
                out_str += (separator + str(sudoku[i][j]))

    return out_str

def sudoku_to_new_numpy_entry(sudoku, tried_before=False, done_before=False):
    string = to_string(sudoku, tried_before, done_before)
    return string_to_new_numpy_entry(string)

def string_to_new_numpy_entry(string):
    string = string.rstrip("\n")
    line_1 = string[:string.find('\n')]
    line_2 = string[string.find('\n') + 1:]
    return np.array([full_information_from_lines(line_1, line_2)], dtype=[('N', 'uint8'),
                                                                          ('number_of_clues', 'int16'),
                                                                          ('complexity_of_solution', 'uint8'),
                                                                          ('tried_before', '?'),
                                                                          ('done_before', '?'),
                                                                          ('sudoku_string', 'object')])

def sudoku_from_string(string, N, separator=","):
    """
    Reads a sudoku from a string, with no other information.
    :param string: str
    :return: Sudoku
    """
    if N <= 1:
        raise ValueError("N has to be at least 2")
    list = string.split(separator)
    if len(list) != (N**4):
        raise ValueError('String has to contain exactly (N**2)**2 elements')
    table = np.zeros((N*N, N*N))
    count = 0
    for i in range(N*N):
        for j in range(N*N):
            table[i][j] = list[count]
            count+=1
    sudoku = Sudoku(table, N)
    return sudoku

def full_information_from_lines(line_1, line_2, separator=","):
    """
    Reads all information from a string
    :param line_1: str.
    :param line_2: str. Two lines produced as an output of to_string(sudoku)
    :return tuple: N, number_of_clues, complexity_of_solution, tried_before, done_before, Sudoku,
        ( int, int, int, bool, bool, str)
    """
    line_1 = line_1.rstrip("\n")
    line_2 = line_2.rstrip("\n")
    list = line_1.split(separator)
    list.append(line_2)
    for i in range(3):
        list[i] = int(list[i])
    list[3] = bool(int(list[3]))
    list[4] = bool(int(list[4]))
    return tuple(list)



def generate_solved_sudoku(N=3, random_state = None):
    """
    Randomly generates a correct filled (N**2, N**2) puzzle.
    Specify a random_state for deterministic behaviour.
    :return: Sudoku
    Current implementation always returns a Sudoku, if the generation is changed it might return None
    """

    random.seed(a=random_state)

    board = np.zeros((N*N, N*N), dtype='int16')  # initialize an empty board
    board[0] = random.sample(range(1, N*N+1), k=N*N)  # fill the top row at random
    sudoku = Sudoku(board, N=N)

    solution = sudoku.solve(random_state=random_state)  # find a random solution. A solution is guaranteed to exist
    return solution[0] if len(solution) > 0 else None


def generate_sudoku_from_a_full_puzzle(
        input_full_puzzle=None, N=3, proportion_of_missing_cells=0.5, random_state=None,
        maximal_time=10
):
    """
    Generates a random Sudoku puzzle with proportion_of_missing_cells*(N**4) missing cells within maximal_time seconds.
        If no solution is found, returns a Sudoku found that has the maximal number of missing cells.
        For N == 3 will stay in the loop until a minimal solution is found (potentially up to 10 seconds slowdown)
    :param input_full_puzzle: either a valid solved Sudoku, or None. None will generate a full puzzle using generate_solved_sudoku
    :param N: size of Sudoku, default is standard N=3
    :param proportion_of_missing_cells: float in the interval 0 to 1. Number of missing cells / number of all cells
        in the resulting sudoku.
    :param random_state: None or int. Use int for deterministic behaviour.
    :param maximal_time: float, in seconds. Maximal time that the function is allowed to look for a required Sudoku.
    :return: (bool, Sudoku). First item is True if the required sudoku was found,
        second item is the found Sudoku, or a Sudoku with the minimal number of clues found in allotted time.
    """

    target_number_of_clues = int((N**4)*(1-proportion_of_missing_cells))
    random.seed(random_state)

    """def number_of_cells_to_remove(sudoku):
        current_number_of_clues = (sudoku != 0).sum()
        if proportion_of_missing_cells<0.5:
            return current_number_of_clues - target_number_of_clues
        elif current_number_of_clues-target_number_of_clues > (N**4)/4:
            return (current_number_of_clues - target_number_of_clues)//2
        elif current_number_of_clues-target_number_of_clues > (N**4)/8:
            return (current_number_of_clues - target_number_of_clues)//2
        else:
            return 1"""

    if input_full_puzzle is None:
        full_puzzle = generate_solved_sudoku(N=N, random_state=random_state)
    else:
        full_puzzle = copy.copy(input_full_puzzle)

    minimal_hints_sudoku = full_puzzle
    sudoku = full_puzzle
    clues_are_removable = np.ones((N*N, N*N))
    number_of_clues_to_remove = (N**4 - target_number_of_clues)

    start_time = time.time()
    random_counter = 0

    minimal_found = False  # Stopping only when a minimal puzzle was achieved for each cycle.
    #  Only present in N == 3 case, due to the difficulty of finding minimal puzzles for bigger N.

    while (not minimal_found and N ==3) or \
            (time.time()-start_time < maximal_time and sudoku.number_of_clues() > target_number_of_clues):
        minimal_found = False
        if number_of_clues_to_remove != 1:
            number_of_clues_to_remove = min(
                number_of_clues_to_remove//2, (sudoku.number_of_clues()-target_number_of_clues)//2)
        else:
            pass
        random_counter += 1
        if number_of_clues_to_remove > 1:
            removed = False
            for i in range(5):
                positions_of_removable_clues = np.argwhere(clues_are_removable == 1).tolist()
                positions_to_remove = random.sample(positions_of_removable_clues, k=number_of_clues_to_remove)
                if sudoku.can_remove_positions(positions_to_remove):
                    removed = True
                    new_table = np.zeros((N**2, N**2))
                    for i, j in itertools.product(range(N**2), range(N**2)):
                        new_table[i][j] = sudoku[i][j]
                    for position in positions_to_remove:
                        i, j = position
                        new_table[i][j] = 0
                        clues_are_removable[i][j] = 0
                    sudoku = Sudoku(new_table, N=N)
                    break

        if number_of_clues_to_remove == 1:
            removed = False

            while (clues_are_removable == 1).any():
                positions_of_removable_clues = np.argwhere(clues_are_removable == 1).tolist()
                position = random.choice(positions_of_removable_clues)
                if sudoku.can_remove_positions([position]):
                    removed = True
                    new_table = np.zeros((N ** 2, N ** 2))
                    for i, j in itertools.product(range(N ** 2), range(N ** 2)):
                        new_table[i][j] = sudoku[i][j]
                    i, j = position
                    new_table[i][j] = 0
                    clues_are_removable[i][j] = 0

                    sudoku = Sudoku(new_table, N=N)
                    break
                else:
                    i, j = position
                    clues_are_removable[i][j] = 0

            if not removed:
                #  print(f"Minimal sudoku with {sudoku.number_of_clues()} clues found.") # debugging
                minimal_found = True
                if sudoku.number_of_clues() < minimal_hints_sudoku.number_of_clues():
                    minimal_hints_sudoku = sudoku
                sudoku = full_puzzle
                clues_are_removable = np.ones((N*N, N*N))
                number_of_clues_to_remove = (N**4 - target_number_of_clues)//2

    if sudoku.number_of_clues() < minimal_hints_sudoku.number_of_clues():
        minimal_hints_sudoku = sudoku

    solutions = minimal_hints_sudoku.solve(maximal_number_of_solutions=2)
    if len(solutions) != 1:
        print("Generated sudoku has "+str(len(solutions))+" solutions.")
        print("Generated board is:")
        print(minimal_hints_sudoku)
        print("Initial board is:")
        print(full_puzzle)
        print("Random seed is "+str(random.getstate()))

    return minimal_hints_sudoku.number_of_clues() <= target_number_of_clues, minimal_hints_sudoku

def main():
    # Use this to generate new Sudokus

    #generate_to_file("puzzle_banks/puzzle_bank.txt",
                     #number_of_sudokus=100, time_for_each_sudoku=1,
                     #target_missing_cells=61/81, minimal_missing_cells=57/81, passing_difficulty=110)


    root = tk.Tk()
    mainframe = tk.Frame()
    root.title("Generating new sudokus")

    variable_N = tk.IntVar(value=3)

    frame_0 = tk.Frame(mainframe)
    N_is_3_button = tk.Radiobutton(frame_0, text="9x9 sudoku", variable=variable_N, value=3)
    N_is_4_button = tk.Radiobutton(frame_0, text="16x16 sudoku", variable=variable_N, value=4)
    N_is_3_button.pack(anchor=tk.W, side='left', padx=10)
    N_is_4_button.pack(anchor=tk.W, side='left', padx=10)
    frame_0.pack(side='top', fill='x')

    frame_1 = tk.Frame(mainframe)
    tk.Label(frame_1, text="Enter the desired number of clues:").pack(side='left')
    target_number_of_clues_field = tk.Text(frame_1, width=4, height=1)
    target_number_of_clues_field.pack(side='right')
    frame_1.pack(side='top', fill='x')

    frame_2 = tk.Frame(mainframe)
    tk.Label(frame_2, text="Enter minimum desired number of clues:").pack(side='left')
    minimal_number_of_clues_field = tk.Text(frame_2, width=4, height=1)
    minimal_number_of_clues_field.pack(side='right')
    frame_2.pack(side='top', fill='x')

    frame_3 = tk.Frame(mainframe)
    tk.Label(frame_3, text="Enter the desired difficulty.").pack(side='left')
    desired_difficulty_field = tk.Text(frame_3, width=4, height=1)
    desired_difficulty_field.insert("1.0", "100")
    desired_difficulty_field.pack(side='right')
    frame_3.pack(side='top', fill='x')
    #tk.Label(mainframe, text='If you only want sudokus of certain difficulty regardless of '
                             #'\n the number of clues, enter 17 as the minimal number of clues')

    frame_4 = tk.Frame(mainframe)
    tk.Label(frame_4, text="Enter the number of sudokus you want to generate:").pack(side='left')
    number_of_sudokus_to_generate_field = tk.Text(frame_4, width=4, height=1)
    number_of_sudokus_to_generate_field.insert("1.0", "20")
    number_of_sudokus_to_generate_field.pack(side='right')
    frame_4.pack(side='top', fill='x')

    frame_5 = tk.Frame(mainframe)
    tk.Label(frame_5, text="Enter the file name, if you want ").pack(side='left')
    file_name_field = tk.Text(frame_5, width=20, height=1)
    file_name_field.insert('1.0', "sudoku_bank.txt")
    file_name_field.pack(side='right')
    frame_5.pack(side='top', fill='x')

    def start_generating():
        clues_dict = {21: (30, "long time"), 22: (2, "2 minutes"), 23: (1, "1 minute"), 24: (0.5, "30 seconds"),
                      25: (1/3, "20 seconds"), 26: (1/6, "10 seconds"), 27: (1/12, "5 seconds"), 28: (1/15, "4 seconds"),
                      29: (1/30, "2 seconds"), 30: (1/60, "1 second"), 20: (100, "very long time")}
        complexity_dict = {110: (2, "2 minutes"), 100: (0.5, "1 minute"),
                           130: (30, "long time"), 140: (100, "very long time")}

        def time_required(clues_dict, complexity_dict, clues, complexity):
            minimal_clues = None
            for clues_number, time_for_this_number_of_clues in clues_dict.items():
                if clues_number >= clues and ( minimal_clues is None or clues_number < minimal_clues):
                    minimal_clues = clues_number
            if minimal_clues is None:
                minimal_clues = 20
            minimal_complexity = None
            for complexity_number, time_for_this_complexity in complexity_dict.items():
                if complexity_number >= complexity and \
                    (minimal_complexity is None or complexity_number < complexity_number):
                    minimal_complexity = complexity_number
            if minimal_complexity is None:
                minimal_complexity = 140

            if clues_dict[minimal_clues][0] < complexity_dict[minimal_complexity][0]:
                return f"Generating each puzzle with {minimal_clues} clues \n takes about {clues_dict[minimal_clues][1]}. " \
                       f"\n Please wait."
            else:
                return f"Generating each puzzle of difficulty {minimal_complexity} \n takes about " \
                       f"{complexity_dict[minimal_complexity][1]}. " \
                       f"\n Please wait."

        N = variable_N.get()
        try:
            target_number_of_missing_cells = (N**4 - int(target_number_of_clues_field.get("1.0", tk.END)))/ (N**4)
        except:
            target_number_of_missing_cells = 61/81 if N == 3 else 150/256
        try:
            minimal_number_of_clues = (N**4 - int(minimal_number_of_clues_field.get("1.0", tk.END)))/N**4
        except:
            minimal_number_of_clues = 0
        try:
            desired_difficulty = int(desired_difficulty_field.get("1.0", tk.END))
        except:
            desired_difficulty = 120
        try:
            number_of_sudokus_to_generate = int(number_of_sudokus_to_generate_field.get("1.0", tk.END))
        except:
            pop_up_messages.PopUpWindow("Please enter valid number of sudokus").show(mainframe)
            return None
        time_for_each_sudoku = 1 if N==3 else 30

        if N == 3:
            message = time_required(clues_dict, complexity_dict, minimal_number_of_clues, desired_difficulty)
        if N == 4:
            message = "Generating 16x16 sudokus takes a long time!"
        else:
            message = ""

        pop_up_messages.PopUpWindow("Generating sudokus.\n "+message)

        generate_to_file("puzzle_banks/puzzle_bank.txt",
                         N=N,
                         number_of_sudokus=number_of_sudokus_to_generate, time_for_each_sudoku=time_for_each_sudoku,
                         target_missing_cells=target_number_of_missing_cells,
                         minimal_missing_cells=minimal_number_of_clues,
                         passing_difficulty=desired_difficulty)


    go_button = tk.Button(mainframe, text="Start!", command=start_generating)
    go_button.pack()

    mainframe.pack()

    root.mainloop()


if __name__ == "__main__":
    main()