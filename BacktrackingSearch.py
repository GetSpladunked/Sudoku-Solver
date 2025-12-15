def find_empty(grid):
    for r in range(9):
        for c in range(9):
            if grid[r][c] == 0:
                return r, c
    return None
def is_valid(grid, row, col, val):
    if any(grid[row][c] == val for c in range(9)):
        return False
    if any(grid[r][col] == val for r in range(9)):
        return False
    br = (row // 3) * 3
    bc = (col // 3) * 3
    for r in range(br, br + 3):
        for c in range(bc, bc + 3):
            if grid[r][c] == val:
                return False
    return True
def solve_sudoku(initLayout):
    grid = [[0 if ch in ('.', '0') else int(ch) for ch in initLayout[i*9:(i+1)*9]] for i in range(9)]
    solutions = []
    def backtrack():
        empty = find_empty(grid)
        if not empty:
            solutions.append([row[:] for row in grid])
            return
        r, c = empty
        for val in range(1, 10):
            if is_valid(grid, r, c, val):
                grid[r][c] = val
                backtrack()
                grid[r][c] = 0
    backtrack()
    return solutions
def printSoln(x):
    for i in range(9):
        if i % 3 == 0 and i != 0:
            print("---------------------")
        for j in range(9):
            if j % 3 == 0 and j != 0:
                print("|", end = " ")
            print(x[i][j], end = " ")
            if j == 8:
                print()
    print()
def stringRepX(x):
    return "".join(str(x[r][c]) for r in range(9) for c in range(9))
def compare_puzzles(unsolved, solved):
    for u, s in zip(unsolved, solved):
        if u not in ('.', '0') and u != s:
            return True
    return False
def translate(x):
    grid = [[0 if ch in ('.', '0') else int(ch) for ch in x[i*9:(i+1)*9]] for i in range(9)]
    newGrid = [[0 for x in range(9)] for y in range(9)]
    for i in range(9):
        for j in range(9):
            newGrid[i][j] = grid[8-j][i]
    return stringRepX(newGrid)