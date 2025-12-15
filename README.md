# Sudoku-Solver
Sudoku solver that solves using human strategies
Sudokus are a "Constraint Satisfaction Problem", the most common algorithm for solving these uses Backtracking Search. This is NOT a Backtracking Search algorithm.
This program uses human strategies for note eliminations or solving values. The strategies are from https://www.sudokuwiki.org/strategy_families. 
This was performed in jupyterLab using python. 
First I created a basic framework of the program, the node object has an int value of 0 - 9 (0 representing unfilled) and a list of potential or noted in values 0 - 9, when a value is impossible for a node, that value will be replaced with 0. It also has a reference to the problem object.
The Puzzle object has a 9x9 grid of node objects, and boolean 9x9 grids that represent naked pairs found in boxes, rows, and columns. 
So far I have sucessfully implemented all of the "basic" strategies

# Improvement Ideas:
further implementation of getSet.
util general remaining function.
get indexes function?
overall reworking of naked checks (double check hidden candidates works properly).
marriage with loop check functions.
simplify printing functions.
general erasing function (takes coord list and list of vals into parameters) to replace the [eVal-1] functions.
look again at chute remote pairs.
rewrite examples and __init__ function to take in-line strings.
look again @ skyscraper and 2-string kite and see if they're redundant.
look at getStrongX/WeakX functions and see if they're useful/reworkable elsewhere.

# Notes for Usage:
You will probably have to go in and uncomment some of the functions in the strategies section of the code, all strategies other than wxyz wing have been coded and proved to function properly.
I have also heavily optimized all functions up to and including "Unique Rectangles". One of the main changes I made to the usage of the algorithm is the implementation of in-line representation of sudoku problems. Check the example file for cool examples and specific strategy usage. Some strategies will get in the way of others so I recommend commenting out some of the function calls in the strateigies method. One smaller change I made was to implement a simple backtracking search algorithm to brute-force solve the puzzle. There are 2 reasons for this, the first reason is so that I have the solution to compare the current state of the puzzle to determine if it has solved correctly or if any strategies perfomed created critical errors, the second reason is to ensure that the puzzle is a true sudoku, meaning it has a single solution. 
