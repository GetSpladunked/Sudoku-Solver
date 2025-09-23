# Sudoku-Solver
Sudoku solver that solves using human strategies
Sudokus are a "Constraint Satisfaction Problem", the most common algorithm for solving these uses Backtracking Search. This is NOT a Backtracking Search algorithm.
This program uses human strategies for note eliminations or solving values. The strategies are from https://www.sudokuwiki.org/strategy_families. 
This was performed in jupyterLab using python. 
First I created a basic framework of the program, the node object has an int value of 0 - 9 (0 representing unfilled) and a list of potential or noted in values 0 - 9, when a value is impossible for a node, that value will be replaced with 0. It also has a reference to the problem object.
The Puzzle object has a 9x9 grid of node objects, and boolean 9x9 grids that represent naked pairs found in boxes, rows, and columns. 
So far I have sucessfully implemented all of the "basic" strategies
