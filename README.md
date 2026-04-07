# Sudoku-Solver
Sudoku solver that solves using human strategies
Sudokus are a "Constraint Satisfaction Problem", the most common algorithm for solving these uses Backtracking Search. This is NOT a Backtracking Search algorithm.
This program uses human strategies for note eliminations or solving values. The strategies are from https://www.sudokuwiki.org/strategy_families. 
This was performed in jupyterLab using python. 
First I created a basic framework of the program, the node object has an int value of 0 - 9 (0 representing unfilled) and a list of potential or noted in values 0 - 9, when a value is impossible for a node, that value will be replaced with 0. It also has a reference to the problem object.
The Puzzle object has a 9x9 grid of node objects, and boolean 9x9 grids that represent naked pairs found in boxes, rows, and columns. 
So far I have sucessfully implemented all of the "basic" strategies

# Changes made:
This version has lots of time complexity alterations for several functions. Particularly for computation-heavy functions like 3D Medusa, X-Cycles, Unique Rectangles, and Simple Coloring. I also did rewrites for smaller functions like tridagon, and probably added new utility functions since I last updated the branch. IDK if this was in the last update but I added a backtracking search just to check if the strategies are screwing everything up as well as to check if there are multiple solutions to a given puzzle (meaning it's not a true sudoku, and that it will break my code). It says at the bottom if it's on the right track, if a mistake was made, or if it's the correct solution. I also implemented another strategies fucntion that includes timestamps for how long each function takes to perform. If you're looking at this text, you most likely know me IRL, so please reach out if you have any advice for my code. I'm also looking to use a binary tree to create lots of different solve orders for the strategies. But that requires a absolutely massive rewrite that I might just get claude to do or something. I'll update the progress on that on my next branch. Thank you for reading and I love you. 

# Notes for Usage:
I don't know which strategies fucntion in the sudoku.py function you're going to want to use but you'll probably need to un-comment some of the functions out. So far everything works until wxyz function so you can use all until then. This program takes in-line representations of puzzles so just type out a long string of what you're looking for and it should be hunky dory. It does not accept puzzles with pre-noted nodes so heads up, you're probably going to have to compare your current puzzle's notes to what is shown when the puzzle loads in if you know something is where it shouldn't be.
