import os
import itertools
import random
from pyomo.environ import *
import sys, pygame as pg
from sudoku_class import Button

os.getcwd()
os.chdir('/Users/min/Desktop/Blog/sudoku')

pg.init()

screen_size = 750, 800
font = pg.font.SysFont(None, 80)
screen = pg.display.set_mode(screen_size)

pg.display.set_caption("Sudoku Solver")

def generate_sudoku():
    base = 3
    side = base * base

    # Pattern for a baseline valid solution
    def pattern(r, c): return (base*(r % base)+r//base+c) % side

    # Randomly shuffle rows, columns, and numbers
    def shuffle(s): return random.sample(s, len(s))
    rBase = range(base)
    rows = [g*base + r for g in shuffle(rBase) for r in shuffle(rBase)]
    cols = [g*base + c for g in shuffle(rBase) for c in shuffle(rBase)]
    nums = shuffle(range(1, side + 1))

    # Produce a randomized board based on the baseline pattern
    board = [[nums[pattern(r, c)] for c in cols] for r in rows]

    # Remove some cells randomly to create a puzzle
    squares = side * side
    empties = random.randint(40, 55)
    for p in random.sample(range(squares), empties):
        board[p // side][p % side] = 0

    return board

#https://www.youtube.com/watch?v=Xw0xxvyxFuE&t=309s
def draw_background():
    screen.fill(pg.Color("white"))
    pg.draw.rect(screen, pg.Color("black"), pg.Rect(15, 15, 720, 720), 10)
    i = 1
    while (i * 80) < 720:
        line_width = 4 if i %3 > 0 else 10
        pg.draw.line(screen, pg.Color("black"), pg.Vector2((i*80)+15, 15), pg.Vector2((i*80)+15, 735), line_width)
        pg.draw.line(screen, pg.Color("black"), pg.Vector2(15, (i*80)+15), pg.Vector2(735, (i*80)+15), line_width)
        i+=1

def draw_numbers(puzzle):
    offset = 35
    cell_size = 80  # Assuming each cell is 80x80 pixels
    for row in range(9):
        for col in range(9):
            number = puzzle[row][col]
            if number != 0:
                n_text = font.render(str(number), True, pg.Color('black'))
                position = (col * cell_size + offset + 4, row * cell_size + offset - 2)
                screen.blit(n_text, position)

def is_puzzle_correct(user_puzzle, solved_puzzle):
    for i in range(9):
        for j in range(9):
            if user_puzzle[i][j] != solved_puzzle[i][j]:
                return False
    return True

def solve_sudoku(puzzle):
    rows = range(0, 9)
    cols = range(0, 9)
    nums = range(1, 10)

    group_dict = {}
    group_dict_rev= {}
    index = 0

    for i in range(0, 3):
        c = (rows[0+(3*i):3+(3*i)])
        for j in range(0, 3):
            r = cols[0+(3*j):3+(3*j)]
            group_dict[index] = list(itertools.product(c, r))
            
            group_dict_rev[tuple(list(itertools.product(c, r)))] = index
            index +=1

    model = ConcreteModel()

    model.r = Set(initialize = rows)
    model.c = Set(initialize = cols)
    model.n = Set(initialize = nums)
    model.x = Var(model.r, model.c, model.n, within=Binary)

    def one_num_each_col(model, j, k):
        return sum(model.x[i,j,k] for i in model.r) == 1

    def one_num_each_row(model, i, k):
        return sum(model.x[i,j,k] for j in model.c) == 1

    def one_num_each_group(model, k, group):
        return sum(model.x[i, j, k] for (i, j) in group_dict[group]) == 1

    def one_num_each_entry(model, i, j):
        return sum(model.x[i,j,k] for k in model.n)  == 1

    def fixed_numbers(model, i, j, k):
        if puzzle[i][j] != 0: 
            return model.x[i, j, puzzle[i][j]] == 1
        else:
            return Constraint.Skip

    model.fixed_values = Constraint(model.r, model.c, model.n, rule=fixed_numbers)
    model.one_num_each_entry = Constraint(model.r, model.c, rule = one_num_each_entry)
    model.one_num_each_col = Constraint(model.c, model.n, rule=one_num_each_col)
    model.one_num_each_row = Constraint(model.r, model.n, rule=one_num_each_row)
    model.one_num_each_group = Constraint(model.n, group_dict.keys(), rule=one_num_each_group)

    solver = SolverFactory('glpk', executable='/opt/homebrew/Cellar/glpk/5.0/bin/glpsol')
    result = solver.solve(model)

    print('Status:', result.solver.status)
    print('Termination Condition:', result.solver.termination_condition)

    solution = [[0 for _ in range(9)] for _ in range(9)]

    for i in rows:
        for j in cols:
            for k in nums:
                if model.x[i, j, k].value == 1:
                    solution[i][j] = k


    return solution

def game_loop():
    puzzle = generate_sudoku()
    original_puzzle = [row[:] for row in puzzle]
    solved_puzzle = None

    selected_cell = None  # Currently selected cell (row, col)

    running = True
    solution_shown = False

    # Button positions
    show_button_pos = (300, 750)
    back_button_pos = (500, 750)
    new_button_pos = (100, 750)
    button_size = (150, 40)
    button_font = pg.font.SysFont(None, 30)
    button_color = pg.Color("lightgray")
    text_color = pg.Color("black")

    show_solution_button = Button("Show Solution", show_button_pos, button_size, button_font, button_color, text_color)
    go_back_button = Button("Go Back", back_button_pos, button_size, button_font, button_color, text_color)
    new_puzzle_button = Button("New Puzzle", new_button_pos, button_size, button_font, button_color, text_color)

    running = True
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

            elif event.type == pg.MOUSEBUTTONDOWN:
                pos = pg.mouse.get_pos()

                if show_solution_button.rect.collidepoint(pos):
                    if solved_puzzle is None:
                        solved_puzzle = solve_sudoku(original_puzzle)
                    solution_shown = True

                elif go_back_button.rect.collidepoint(pos):
                    solution_shown = False

                elif new_puzzle_button.rect.collidepoint(pos):
                    puzzle = generate_sudoku()
                    original_puzzle = [row[:] for row in puzzle]
                    solved_puzzle = None
                    solution_shown = False

                elif 15 <= pos[0] <= 735 and 15 <= pos[1] <= 735:
                    selected_row = (pos[1] - 15) // 80
                    selected_col = (pos[0] - 15) // 80
                    selected_cell = (selected_row, selected_col)


                # Selecting a cell
                elif 15 <= pos[0] <= 735 and 15 <= pos[1] <= 735:
                    selected_row = (pos[1] - 15) // 80
                    selected_col = (pos[0] - 15) // 80
                    selected_cell = (selected_row, selected_col)

            elif event.type == pg.KEYDOWN and selected_cell:
                row, col = selected_cell
                if original_puzzle[row][col] == 0:
                    if event.unicode in '123456789':
                        puzzle[row][col] = int(event.unicode)
                    elif event.key in [pg.K_BACKSPACE, pg.K_DELETE]:
                        puzzle[row][col] = 0

                # Check puzzle completion whenever a cell is updated
                if puzzle == solved_puzzle:
                    puzzle_completed = True
                else:
                    puzzle_completed = False

        draw_background()

        if solution_shown and solved_puzzle is not None:
            draw_numbers(solved_puzzle)
            go_back_button.draw(screen)
        else:
            draw_numbers(puzzle)
            show_solution_button.draw(screen)

        new_puzzle_button.draw(screen)

        # Display Correct message
        if puzzle == solved_puzzle:
            correct_font = pg.font.SysFont(None, 200)  # clearly set large font size here
            correct_text = correct_font.render("Correct!", True, pg.Color("green"))
            correct_rect = correct_text.get_rect(center=(375, 375))  # center of your 750x750 Sudoku grid
            screen.blit(correct_text, correct_rect)
        pg.display.flip()

    pg.quit()


game_loop()
