# Sudoku-Solver
Sudoku solver that solves using human strategies
Sudokus are a "Constraint Satisfaction Problem", the most common algorithm for solving these uses Backtracking Search. This is NOT a Backtracking Search algorithm.
This program uses human strategies for note eliminations or solving values. The strategies are from https://www.sudokuwiki.org/strategy_families. 
This coded in jupyterLab using python, but I recently made the move to VS Code.

#Implemented strategies
- X-Wing
- Chute Remote Pairs
- Simple Coloring
- W-Wing
- Y-Wing
- Rectangle Elimination
- Swordfish
- XYZ-Wing
- X-Cycles
- 3D Medusa
- Jellyfish
- Unique Rectangles
- Tridagon
- Fireworks
- Twin XY-Chains
- SK-Loops
- Extended Unique Rectangles
- Hidden Unique Rectangles

# Changes made:
The largest change is that now this is a branching algorithm. It now will find every possible solving order for each possible strategy implemented (see list below). 
Alongside this, heavy optimization for many strategy functions.
Some minor changes to how the strategy functions work, creates a list of new puzzle objects to be returned whenever a change gets made plus some extra checks that are now inert and should be ignored.

# Notes for Branching algorithm:
There were a couple of things that I tried and failed to do when making this a branching algorithm. There's artifacts of it in the code but for the most part I made them inert.
- **1. Pruning:** I created a sort of pruning checker "uberPrune" for when the branches get out of control, but I left it sort of unfinished. The idea is that if a strategy leaves a puzzle in a solvable state (regarding basic elimination using naked and hidden groups), it will log that change, and ignore strategies that make that EXACT change. 3D medusa really blows up the tree and this was made to combat it. It gets passed into the solve function, and to every subsequent strategy function (in hindsight I should have just made it part of the sudoku object itself or made it global). But lately I've been setting it to not prune (0) at all so I can stress test the whole program, but also because I cannot confirm if it's functioning the way I want it to. 
- **2. Tree Display:** This was a disappointing investment of my time. I tried to create a display tree for all possible solution paths, but because of adding more and more strategies (especially 3D medusa), it made it incomprehensible. There's some tree organization stuff at the bottom of the solve function that I'm too afraid to remove, maybe some remnants of tree stuff in the main that's commented out, and some stuff that got changed if you print the puzzle's report. I'll probably come back to this once I figure out the pruning and tree restructuring.

# Notes for Usage:
In the code's current state, it just solves the function without telling you what it's doing, but I do know that it's working. To use it, set "currentPuzzle" (in the 2nd box) to the string representation of your puzzle. To see results of any of the solves, pick the index of a "good solution" and paste said index into the 3rd box's "goodSolvePile[X].displayFullReport()". 

# Future work
- Currently I'm working on a sudoku generator algorithm that uses custom strategy & difficulty inputs. Still a very early work in progress.
- GUI for inputting sudokus.
- Web application for puzzle generation and solving sudokus.
