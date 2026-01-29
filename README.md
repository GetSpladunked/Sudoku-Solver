# Sudoku-Solver
Sudoku solver that solves using human strategies
Sudokus are a "Constraint Satisfaction Problem", the most common algorithm for solving these uses Backtracking Search. This is NOT a Backtracking Search algorithm.
This program uses human strategies for note eliminations or solving values. The strategies are from https://www.sudokuwiki.org/strategy_families. 
This was performed in jupyterLab using python. 
First I created a basic framework of the program, the node object has an int value of 0 - 9 (0 representing unfilled) and a list of potential or noted in values 0 - 9, when a value is impossible for a node, that value will be replaced with 0. It also has a reference to the problem object.
The Puzzle object has a 9x9 grid of node objects, and boolean 9x9 grids that represent naked pairs found in boxes, rows, and columns. 
So far I have sucessfully implemented all of the "basic" strategies

# Changes made:
Heavy optimizations for every single function up to and including "Unique Rectangles". So far with my optimizations I have removed 1400 lines of code, which means that my initial code was pretty garbage. Another large change that I made was the implementation of "Utility" functions with are simple functions that perform the same actions among many strategies. One change I made to the usage of the algorithm is the implementation of in-line representation of sudoku problems. Check the www.sudokuwiki.org for cool examples and specific strategy usage. Another smaller change in the usage was to implementing a simple backtracking search algorithm to brute-force solve the puzzle. There are 2 reasons for this, the first reason is so that I have the solution to compare the current state of the puzzle to determine if it has solved correctly or if any strategies perfomed created critical errors, the second reason is to ensure that the puzzle is a true sudoku, meaning it has a single solution. If there are multiple solutions to a problem, then the algorithm is pretty much guaranteed to make a mistake other than sheer luck fringe cases where it solves correctly. Some strategies like y-wing have countermeasures for this but I know that other strategies will not.

# Notes for Usage:
You will probably have to go in and uncomment some of the functions in the strategies section of the code, all strategies other than wxyz wing have been coded and proved to function properly.
