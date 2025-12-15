import itertools
import copy

def solve(Puzzle):
    iterations = 0
    Puzzle.displayAll()
    # Puzzle.resetLocks()
    while not Puzzle.solved():
        print(f"Iteration: {iterations}")
        tempCopy = copy.deepcopy(Puzzle)
        Puzzle.cleanup()
        Puzzle.checkBoxLock(tempCopy)
        Puzzle.checkRowLock(tempCopy)
        Puzzle.checkColLock(tempCopy)
        # Puzzle.resetLocks()
        iterations += 1
        if Puzzle.solved():
            break
        if Puzzle.stuck(tempCopy):
            Puzzle.displayAll()
            print("Using some strategies")
            Puzzle = strategies(Puzzle, tempCopy)
            if Puzzle.stuck(tempCopy):
                break
            else:
                Puzzle.displayAll()
                continue
    if Puzzle.solved():
        print("Puzzle solved!\n")
        Puzzle.displayAll()
    else:
        print("Puzzle got stuck :(\n")
        Puzzle.displayAll()

def strategies(Puzzle, tempCopy):
    # Puzzle.xWing(tempCopy)
    # if not Puzzle.stuck(tempCopy):
    #     return Puzzle
    # Puzzle.chuteRemotePairs(tempCopy)
    # if not Puzzle.stuck(tempCopy):
    #     return Puzzle
    # Puzzle.simpleColoringUtil(tempCopy)
    # if not Puzzle.stuck(tempCopy):
    #     return Puzzle
    # Puzzle.yWing()
    # if not Puzzle.stuck(tempCopy):
    #     return Puzzle
    # Puzzle.rectangleElimination(tempCopy)
    # if not Puzzle.stuck(tempCopy):
    #     return Puzzle
    # Puzzle.swordfishUtil(tempCopy)
    # if not Puzzle.stuck(tempCopy):
    #     return Puzzle
    # Puzzle.xyzWing(tempCopy)
    # if not Puzzle.stuck(tempCopy):
    #     return Puzzle
    # Puzzle.bug()
    # Puzzle.xCycles(tempCopy)
    # if not Puzzle.stuck(tempCopy):
    #     return Puzzle
    # Puzzle.medusa3D(tempCopy)
    # if not Puzzle.stuck(tempCopy):
    #     return Puzzle
    # Puzzle.jellyFish(tempCopy)
    # if not Puzzle.stuck(tempCopy):
    #     return Puzzle
    # Puzzle.uniqueRectangles(tempCopy)
    # if not Puzzle.stuck(tempCopy):
    #     return Puzzle
    # Puzzle.uniqueRectangleUtil(tempCopy)
    # if not Puzzle.stuck(tempCopy):
    #     return Puzzle
    # Puzzle.tridagonUtil()
    # if not Puzzle.stuck(tempCopy):
    #     # print("Tridagon Worked")
    #     return Puzzle
    # Puzzle.fireworkUtil()
    # if not Puzzle.stuck(tempCopy):
    #     # print("Firework Worked")
    #     return Puzzle
    # Puzzle.twinXYChains()
    # if not Puzzle.stuck(tempCopy):
    #     # print("Twin XY Chains Worked")
    #     return Puzzle
    # Puzzle.SKLoops()
    # if not Puzzle.stuck(tempCopy):
    #     # print("SK Loops Worked")
    #     return Puzzle
    # Puzzle.extUniqueRectanglesUtil()
    # if not Puzzle.stuck(tempCopy):
    #     # print("Extended Unique Rectangles Worked")
    #     return Puzzle
    # Puzzle.hiddenUniqueRectanglesUtil()
    # if not Puzzle.stuck(tempCopy):
    #     # print("Hidden Unique Rectangles Worked")
    #     return Puzzle
    # Puzzle.skyscraperUtil()
    # if not Puzzle.stuck(tempCopy):
    #     print("Skyscraper Worked")
    #     return Puzzle
    # Puzzle.twoStringKiteUtil()
    # if not Puzzle.stuck(tempCopy):
    #     print("2-String Kite Worked")
    #     return Puzzle
    return Puzzle
def EZstrategies(Puzzle, tempCopy):
    Puzzle.chuteRemotePairs(tempCopy)
    Puzzle.simpleColoringUtil(tempCopy)
    Puzzle.yWing(tempCopy)
    Puzzle.rectangleElimination(tempCopy)
    Puzzle.swordfishUtil(tempCopy)
    Puzzle.xyzWing(tempCopy)
    Puzzle.bug()
    Puzzle.xCycles(tempCopy)
    Puzzle.medusa3DUtil(tempCopy)
    # Puzzle.jellyFishUtil()
    # Puzzle.uniqueRectangleUtil()
    # Puzzle.tridagonUtil()
    # Puzzle.fireworkUtil()
    # Puzzle.twinXYChains()
    # Puzzle.SKLoops()
    # Puzzle.extUniqueRectanglesUtil()
    # Puzzle.hiddenUniqueRectanglesUtil()
    return Puzzle
# improvement Ideas:
# further implementation of getSet. 
# look again at chute remote pairs.
# look again @ skyscraper and 2-string kite and see if they're redundant. 
# look at getStrongX/WeakX functions and see if they're useful/reworkable elsewhere.

    # ********************************************************************************************************************
    # Object declaration functions
class Puzzle:
    # the node class references the problem, as well as holds the notes (current possibilities) for an unsolved node
    # it will be 0 if it is not filled in, and when it has been confirmed as a number it will change it's notes to be a list of 9 0's to make it easier for printing the notes 
    class Node:
        def __init__(self, hardVal, prob):
            self.problem = prob
            self.val = hardVal
            self.note = [1,2,3,4,5,6,7,8,9]
            if self.val != 0:
                self.note = [0,0,0,0,0,0,0,0,0]
        # setval changes the value of the current Node and changes the notes for the current node to a list of 9 0's
        # then it calls updateNotes on the problem to remove the current value from all nodes in its x & y axis as well as the box it resides in
        def setVal(self, hardVal):
            self.val = hardVal
            self.note = [0,0,0,0,0,0,0,0,0]
            self.problem.updateNotes()
        def equals(self, x):
            return self.val == x.val and self.note == x.note
            
    # The problem class has 5 data structures, 
    # layout: a 9x9 grid of the node objects 
    # locked: a 9x9 bool grid that represents if a node has more than 2 locked attributes
    # softboxlocked: a 9x9 bool grid that represents if a box has two or more nodes with ironed out possibilities, used for filtering out unecessary searches
    # softlinelockedx: a 9x9 bool grid that represents if a row has two or more nodes with ironed out possibilities
    # soflinelockedy: a 9x9 bool grid that represents if a column has two or more nodes with ironed out possibilities
    # all of these are initialized with an initial layout, all lockeded data structures will be initialized to False and changed to true if a node has a value
    # after initialization it will call the update notes function to get rid of incorrect guesses for a node
    def __init__(self, initLayout):
        if len(initLayout) != 81:
            raise ValueError("Layout must contain exactly 81 characters.")
        grid = [
            [0 if ch in ('.', '0') else int(ch) for ch in initLayout[i*9:(i+1)*9]]
            for i in range(9)
        ]
        self.layout = [[None for _ in range(9)] for _ in range(9)]
        self.locked = [[False for _ in range(9)] for _ in range(9)]
        self.softboxlocked = [[False for _ in range(9)] for _ in range(9)]
        self.softlinelockedx = [[False for _ in range(9)] for _ in range(9)]
        self.softlinelockedy = [[False for _ in range(9)] for _ in range(9)]
        for r in range(9):
            for c in range(9):
                val = grid[r][c]
                self.layout[r][c] = self.Node(grid[r][c], self)
                if val:
                    self.locked[r][c] = self.softboxlocked[r][c] = self.softlinelockedx[r][c] = self.softlinelockedy[r][c] = True
        self.updateNotes()
    # resets the locked 2D arrays for every iteration
    def resetLocks(self):
        self.locked = [[self.layout[r][c].val != 0 for c in range(9)] for r in range(9)]
        self.softboxlocked, self.softlinelockedx, self.softlinelockedy = ([row[:] for row in self.locked] for _ in range(3))
    def singleLockReset(self, coords):
        i, j = coords
        rowOffset, colOffset = self.getOffset(i), self.getOffset(j)
        for row in range(9): self.softlinelockedy[row][j] = False
        for col in range(9): self.softlinelockedx[i][col] = False
        for row in range(rowOffset, rowOffset + 3):
            for col in range(colOffset, colOffset + 3):
                self.softboxlocked[row][col] = False
    # sets locks if a value is found
    def setLocks(self, r, c):
        self.locked[r][c] = self.softboxlocked[r][c] = self.softlinelockedx[r][c] = self.softlinelockedy[r][c] = True
    
    # ********************************************************************************************************************
    # PRINT FUNCTIONS
    # displays problem (empty space if non-existant)
    def display(self):
        for i in range(9):
            if i % 3 == 0 and i != 0:
                print("---------------------")
            for j in range(9):
                if j % 3 == 0 and j != 0:
                    print("|", end = " ")
                print(" ", end = " ") if self.layout[i][j].val == 0 else print(self.layout[i][j].val, end = " ")
                if j == 8:
                    print()
        print()
        
    # display notes, for nodes with values displays 3x3 grid of 0's, for nodes w/o values displays empty space if note doesn't exist
    def notesDisplay(self):
        horizontal_line = "-" * 73
        for i in range(9):
            if i % 3 == 0 and i != 0:
                print(horizontal_line)
            for note_row in range(3):
                for j in range(9):
                    if j % 3 == 0 and j != 0:
                        print("|", end=" ")
                    start = note_row * 3
                    end = start + 3
                    for k in range(start, end):
                        val = self.layout[i][j].note[k]
                        if self.layout[i][j].val != 0:
                            print("0", end=" ")
                        else:
                            print(val if val != 0 else " ", end=" ")
                    if j != 8:
                        print("|", end=" ")
                print()
            if i != 8:
                print(horizontal_line)
        print()
    # displays puzzle followed by the notes
    def displayAll(self):
        self.display()
        self.notesDisplay()
        print()
    def stringRep(self):
        return "".join(str(self.layout[r][c].val or ".") for r in range(9) for c in range(9))
    # ********************************************************************************************************************
    # Update notes functions
    # the updateNotes function combs through all current values in the problem and removes the redundant notes from their rows, columns, and boxes 
    def updateNotes(self):
        for i in range(9):
            for j in range(9):
                x = self.layout[i][j].val
                if x == 0:
                    continue
                for a in range(9):
                    if a != j:
                        self.layout[i][a].note[x-1] = 0
                    if a != i:
                        self.layout[a][j].note[x-1] = 0
                rowOffset, colOffset = self.getOffset(i), self.getOffset(j)
                for a in range(rowOffset, rowOffset + 3):
                    for b in range(colOffset, colOffset + 3):                           
                        self.layout[a][b].note[x-1] = 0
    
    def subUpdateNotes(self, x, coords, vals):
        if x == 'box':
            rowOffset, colOffset = self.getOffset(coords[0][0]), self.getOffset(coords[0][1])
            cells = [(i, j) for i in range(rowOffset, rowOffset + 3) for j in range(colOffset, colOffset + 3)]
        elif x == 'row':
            row = coords[0][0]
            cells = [(row, j) for j in range(9)]
        elif x == 'col':
            col = coords[0][1]
            cells = [(i, col) for i in range(9)]
        for (i, j) in cells:
            if (i, j) in coords or self.layout[i][j].val != 0:
                continue
            for k in vals:
                self.layout[i][j].note[k-1] = 0
                
    # updates specific values (optimization purposes)
    def updateNotesDX(self, coordList, vals):
        for i, j in coordList:
            for eVal in vals:
                self.layout[i][j].note[eVal-1] = 0
    # ********************************************************************************************************************
    # Termination & "stuck" binary functions, also a differenceCount function to determine the effectivity of changes made to a puzzle object
    # basic termination function
    def solved(self):
        for i in range(9):
            for j in range(9):
                if self.layout[i][j].val == 0:
                    return False
        return True
    # conditional to determine if there are any differences between current build and a tempCopy
    def stuck(self, tempCopy):
        for i in range(9):
            for j in range(9):
                if not self.layout[i][j].equals(tempCopy.layout[i][j]):
                    return False
        return True
    
    def differenceCount(self, origCopy):
        hardCount = 0 
        softCount = 0
        for i in range(9):
            for j in range(9):
                if origCopy.layout[i][j].val == 0 and self.layout[i][j].val == 0:
                    tempSet1 = set(origCopy.layout[i][j].note) - {0}
                    tempSet2 = set(self.layout[i][j].note) - {0}
                    softCount += len(tempSet1) - len(tempSet2)
                elif origCopy.layout[i][j].val == 0 and self.layout[i][j].val != 0:
                    hardCount += 1
        return hardCount, softCount
    def compare(self, solvedArry):
        for i in range(9):
            for j in range(9):
                if self.layout[i][j].val == solvedArry[i][j]:
                    continue
                if solvedArry[i][j] not in self.layout[i][j].note:
                    return False
        return True
    # ********************************************************************************************************************
    # Utility functions
    
    # Returns a set of remaining noted values from the puzzle object
    def getRemaining(self):
        return {v for r in range(9) for c in range(9) for v in self.layout[r][c].note if v != 0}
    
    # Returns a set of the notes at a given coordinate (minus 0)
    def getSet(self, coord):
        return set(self.layout[coord[0]][coord[1]].note) - {0}
    
    # Returns the box idx of a given idx (done twice to find a box)
    def getOffset(self, val):
        return (val//3) * 3

    # Checks if values exist in a box/row/col outside of the provided coordinates
    def singleBoxCheck(self, coords, vals):
        r0, c0 = (coords[0][0]//3)*3, (coords[0][1]//3)*3
        return all(all(k not in self.layout[i][j].note for k in vals) 
                   for i in range(r0, r0+3) for j in range(c0, c0+3) if (i, j) not in coords)
    
    def singleRowCheck(self, coords, vals):
        row = coords[0][0]
        return all(all(k not in self.layout[row][j].note for k in vals) 
                   for j in range(9) if (row, j) not in coords)
    
    def singleColCheck(self, coords, vals):
        col = coords[0][1]
        return all(all(k not in self.layout[i][col].note for k in vals) 
                   for i in range(9) if (i, col) not in coords)
    
    # Boolean functions to check if coordList is in the same box, row, or column
    def inBox(self, coordsList):
        r0, c0 = coordsList[0][0] // 3, coordsList[0][1] // 3
        return all(i // 3 == r0 and j // 3 == c0 for i, j in coordsList)
    def inRow(self, coordsList):
        row = coordsList[0][0]
        return all(i == row for i, _ in coordsList)
    def inCol(self, coordsList):
        col = coordsList[0][1]
        return all(j == col for _, j in coordsList)
    def hasConnection(self, coordsList):
        return self.inBox(coordsList) or self.inRow(coordsList) or self.inCol(coordsList)
    
    # returns a set of all indexes where the notes are equivalent to a given set vals
    def getExBoxIdxs(self, pos, vals):
        x, y = pos
        r0, c0 = self.getOffset(x), self.getOffset(y)
        return {(r, c) for r in range(r0, r0+3) for c in range(c0, c0+3) if vals == self.getSet((r, c))}
    def getExRowIdxs(self, pos, vals):
        x, _ = pos
        return {(x, c) for c in range(9) if vals == self.getSet((x, c))}
    def getExColIdxs(self, pos, vals):
        _, y = pos
        return {(r, y) for r in range(9) if vals == self.getSet((r, y))}

    # returns a set of all indexes that contain a set of notes that set vals is a subset of
    def getBoxSubsets(self, pos, vals):
        x, y = pos
        r0, c0 = self.getOffset(x), self.getOffset(y)
        return {(r, c) for r in range(r0, r0 + 3) for c in range(c0, c0 + 3) if not self.locked[r][c] and self.getSet((r, c)) <= vals}
    def getRowSubsets(self, pos, vals):
        x, _ = pos
        return {(x, c) for c in range(9) if not self.locked[x][c] and self.getSet((x, c)) <= vals}
    def getColSubsets(self, pos, vals):
        _, y = pos
        return {(r, y) for r in range(9) if not self.locked[r][y] and self.getSet((r, y)) <= vals}

    def getAnyBoxIdxs(self, pos, vals):
        r0, c0 = self.getOffset(pos[0]), self.getOffset(pos[1])
        return {(r, c) for r in range(r0, r0+3) for c in range(c0, c0+3) if vals <= self.getSet((r, c))}
    def getAnyRowIdxs(self, pos, vals):
        x, _ = pos
        return {(x, c) for c in range(9) if not self.locked[x][c] and vals <= self.getSet((x, c))}
    def getAnyColIdxs(self, pos, vals):
        _, y = pos
        return {(r, y) for r in range(9) if not self.locked[r][y] and vals <= self.getSet((r, y))}

    # returns if 2 nodes are in same row/col chute
    def sameRowChute(self, node1, node2):
        return node1[0]//3 == node2[0]//3
    def sameColChute(self, node1, node2):
        return node1[1]//3 == node2[1]//3
    # ********************************************************************************************************************
    # ***********************************************BASIC STRATEGIES*****************************************************
    # ********************************************************************************************************************
    # Fundamental updating function
    def cleanup(self):
        # loop that goes through all nodes
        for i in range(9):
            for j in range(9):
                # skips iteration if value exists in current Node
                if self.locked[i][j]:
                    continue
                # creates a temporary set of all nonzero notes in the current node
                tempSet = self.getSet((i, j))
                if len(tempSet) == 1:
                    a = tempSet.pop()
                    print(f"Cleanup found {a} at index {(i, j)}")
                    self.layout[i][j].setVal(a)
                    self.singleLockReset((i, j))
                    self.setLocks(i, j)
                    self.cleanup()
                    continue
                for a in tempSet:
                    if any([self.singleBoxCheck([(i,j)], {a}),
                            self.singleRowCheck([(i,j)], {a}),
                            self.singleColCheck([(i,j)], {a})]):
                        print(f"Cleanup found {a} at index {(i,j)}")
                        self.layout[i][j].setVal(a)
                        self.singleLockReset((i, j))
                        self.setLocks(i, j)
                        self.cleanup()
                        break
    # These functions check for naked groups within the puzzle object
    def checkBoxLock(self, tempCopy):
        remaining = self.getRemaining()
        for size in range(2, len(remaining)):
            for combo in itertools.combinations(remaining, size):
                vals = set(combo)
                for r in range(9):
                    for c in range(9):
                        if self.locked[r][c] or self.softboxlocked[r][c]:
                            continue
                        nodeSet = self.getSet((r, c))
                        if nodeSet == vals:
                            boxCells = list(self.getExBoxIdxs((r, c), vals))
                            if len(boxCells) == size: 
                                for x, y in boxCells:
                                    self.softboxlocked[x][y] = True
                                if self.inRow(boxCells):
                                    for x, y in boxCells:
                                        self.softlinelockedx[x][y] = True
                                    self.subUpdateNotes('row', boxCells, vals)
                                    self.subUpdateNotes('box', boxCells, vals)
                                    # if not self.stuck(tempCopy):
                                    #     print(f"CheckBoxLock Sit 1 found {vals} in {boxCells}, recorded box & row locks.")
                                elif self.inCol(boxCells):
                                    for x, y in boxCells:
                                        self.softlinelockedy[x][y] = True
                                    self.subUpdateNotes('col', boxCells, vals)
                                    self.subUpdateNotes('box', boxCells, vals)
                                    # if not self.stuck(tempCopy):
                                    #     print(f"CheckBoxLock Sit 1 found {vals} in {boxCells}, recorded box & col locks.")
                                else:
                                    self.subUpdateNotes('box', boxCells, vals)
                                    # if not self.stuck(tempCopy):
                                    #     print(f"CheckBoxLock Sit 1 found {vals} in {boxCells}, recorded box locks.")
                        boxCells = list(self.getExBoxIdxs((r, c), vals))
                        if 2 <= len(boxCells) and len(boxCells) == size:
                            for x, y in boxCells:
                                self.softboxlocked[x][y] = True
                            if self.inRow(boxCells):
                                for x, y in boxCells:
                                    self.softlinelockedx[x][y] = True
                                self.subUpdateNotes('row', boxCells, vals)
                                self.subUpdateNotes('box', boxCells, vals)
                                # if not self.stuck(tempCopy):
                                #     print(f"CheckBoxLock Sit 2 found {vals} in {boxCells}, recorded box & row locks.")
                            elif self.inCol(boxCells):
                                for x, y in boxCells:
                                    self.softlinelockedy[x][y] = True
                                self.subUpdateNotes('col', boxCells, vals)
                                self.subUpdateNotes('box', boxCells, vals)
                                # if not self.stuck(tempCopy):
                                #     print(f"CheckBoxLock Sit 2 found {vals} in {boxCells}, recorded box & col locks.")
                            else:
                                self.subUpdateNotes('box', boxCells, vals)
                                # if not self.stuck(tempCopy):
                                #     print(f"CheckBoxLock Sit 2 found {vals} in {boxCells}, recorded box locks.")
    def checkRowLock(self, tempCopy):
        remaining = self.getRemaining()
        for size in range(2, len(remaining)):
            for combo in itertools.combinations(remaining, size):
                vals = set(combo)
                for r in range(9):
                    for c in range(9):
                        if self.locked[r][c] or self.softlinelockedx[r][c]:
                            continue
                        nodeSet = self.getSet((r, c))
                        if nodeSet == vals:
                            rowCells = list(self.getExRowIdxs((r, c), vals))
                            if len(rowCells) == size:
                                for x, y in rowCells:
                                    self.softlinelockedx[x][y] = True
                                if self.inBox(rowCells):
                                    for x, y in rowCells:
                                        self.softboxlocked[x][y] = True
                                    self.subUpdateNotes('row', rowCells, vals)
                                    self.subUpdateNotes('box', rowCells, vals)
                                    # if not self.stuck(tempCopy):
                                    #     print(f"CheckRowLock Sit 1 found {vals} in {rowCells}, recorded row & box locks.")
                                else:
                                    self.subUpdateNotes('row', rowCells, vals)
                                    # if not self.stuck(tempCopy):
                                    #     print(f"CheckRowLock Sit 1 found {vals} in {rowCells}, recorded row locks.")
                        rowCells = list(self.getExRowIdxs((r, c), vals))
                        if 2 <= len(rowCells) and len(rowCells) == size:
                            for x, y in rowCells:
                                self.softlinelockedx[x][y] = True
                            if self.inBox(rowCells):
                                for x, y in rowCells:
                                    self.softboxlocked[x][y] = True
                                self.subUpdateNotes('row', rowCells, vals)
                                self.subUpdateNotes('box', rowCells, vals)
                                # if not self.stuck(tempCopy):
                                #     print(f"CheckRowLock Sit 2 found {vals} in {rowCells}, recorded row & box locks.")
                            else:
                                self.subUpdateNotes('row', rowCells, vals)
                                # if not self.stuck(tempCopy):
                                #     print(f"CheckRowLock Sit 2 found {vals} in {rowCells}, recorded row locks.")
    def checkColLock(self, tempCopy):
        remaining = self.getRemaining()
        for size in range(2, len(remaining)):
            for combo in itertools.combinations(remaining, size):
                vals = set(combo)
                for r in range(9):
                    for c in range(9):
                        if self.locked[r][c] or self.softlinelockedy[r][c]:
                            continue
                        nodeSet = self.getSet((r, c))
                        if nodeSet == vals:
                            colCells = list(self.getExColIdxs((r, c), vals))
                            if len(colCells) == size:
                                for x, y in colCells:
                                    self.softlinelockedy[x][y] = True
                                if self.inBox(colCells):
                                    for x, y in colCells:
                                        self.softboxlocked[x][y] = True
                                    self.subUpdateNotes('col', colCells, vals)
                                    self.subUpdateNotes('box', colCells, vals)
                                    # if not self.stuck(tempCopy):
                                    #     print(f"CheckColLock Sit 1 found {vals} in {colCells}, recorded col & box locks.")
                                else:
                                    self.subUpdateNotes('col', colCells, vals)
                                    # if not self.stuck(tempCopy):
                                    #     print(f"CheckColLock Sit 1 found {vals} in {colCells}, recorded col locks.")
                        colCells = list(self.getExColIdxs((r, c), vals))
                        if 2 <= len(colCells) and len(colCells) == size:
                            for x, y in colCells:
                                self.softlinelockedy[x][y] = True
                            if self.inBox(colCells):
                                for x, y in colCells:
                                    self.softboxlocked[x][y] = True
                                self.subUpdateNotes('col', colCells, vals)
                                self.subUpdateNotes('box', colCells, vals)
                                # if not self.stuck(tempCopy):
                                #     print(f"CheckColLock Sit 2 found {vals} in {colCells}, recorded col & box locks.")
                            else:
                                self.subUpdateNotes('col', colCells, vals)
                                # if not self.stuck(tempCopy):
                                #     print(f"CheckColLock Sit 2 found {vals} in {colCells}, recorded col locks.")

    # ********************************************************************************************************************
    # ***********************************************TOUGH STRATEGIES*****************************************************
    # ********************************************************************************************************************
    def xWing(self, tempCopy):
        for val in self.getRemaining():
            self.squareFind(val, tempCopy)
            if not self.stuck(tempCopy):
                return
    def squareFind(self, val, tempCopy):
        for r1 in range(9):
            row1Cells = {c for r, c in self.getAnyRowIdxs((r1, 0), {val})}
            if len(row1Cells) != 2:
                continue
            for r2 in range(r1 + 1, 9):
                row2Cells = {c for r, c in self.getAnyRowIdxs((r2, 0), {val})}
                if row2Cells == row1Cells:
                    for c in row1Cells:
                        self.subUpdateNotes('col', [(r1, c), (r2, c)], {val})
                    if not self.stuck(tempCopy):
                        print(f"X-Wing removed {val} in columns {row1Cells}")
                        return
        for c1 in range(9):
            col1Cells = {r for r, c in self.getAnyColIdxs((0, c1), {val})}
            if len(col1Cells) != 2:
                continue
            for c2 in range(c1 + 1, 9):
                col2Cells = {r for r, c in self.getAnyColIdxs((0, c2), {val})}
                if col1Cells == col2Cells:
                    for r in col1Cells:
                        self.subUpdateNotes('row', [(r, c1), (r, c2)], {val})
                    if not self.stuck(tempCopy):
                        print(f"X-Wing removed {val} in rows {col1Cells}")
                        return
    # ********************************************************************************************************************
    # Performs chute remote pairs strategy & updates accordingly, "naked" pairs which exist in different rows and columns (within square sight of a node)
    def chuteRemotePairs(self, tempCopy):
        remaining = self.getRemaining()
        for combo in itertools.combinations(remaining, 2):
            comboSet = set(combo)
            rowPairs = self.getRowChuteRemotePairs(comboSet)
            if len(rowPairs) != 0:
                for (a, b), (x, y) in rowPairs:
                    rowOffset1, colOffset1, colOffset2 = self.getOffset(a), self.getOffset(b), self.getOffset(y)
                    otherCells = {(r, c) for r in range(rowOffset1, rowOffset1 + 3) for c in range(9) if r not in {a, x} and not (colOffset1 <= c < colOffset1 + 3 or colOffset2 <= c < colOffset2 + 3)}
                    pencilSet, pennedSet = set(), set()
                    for r, c in otherCells:
                        if self.locked[r][c]:
                            pennedSet.add(self.layout[r][c].val)
                        else:
                            pencilSet |= self.getSet((r, c))
                    remoteIntersection = comboSet & (pencilSet | pennedSet)
                    pencilIntersection = comboSet & pencilSet
                    pennedIntersection = comboSet & pennedSet
                    eNodes = [(x,eCol) for eCol in range(colOffset1, colOffset1 + 3)] + [(a,eCol) for eCol in range(colOffset2, colOffset2 + 3)]
                    if len(pencilSet) == 0 and len(pennedIntersection) == 0:
                        # if neither value in the remote pair is penned in, then performs double elimination
                        eNodes += [(x, eCol) for eCol in range(colOffset2, colOffset2 + 3) if eCol != y] + [(a, eCol) for eCol in range(colOffset1, colOffset1 + 3) if eCol != b]
                        self.updateNotesDX(eNodes, comboSet)
                        if not self.stuck(tempCopy):
                            print(f"Remote Pair (Row) 1: {[(a, b), (x, y)]} removed {comboSet} from {eNodes}")
                            return
                    elif len(pennedIntersection) == 1 and len(pencilIntersection) == 0:
                        # if only one remote pair value is penned in, erases that value from the appropraite nodes
                        self.updateNotesDX(eNodes, pennedIntersection)
                        if not self.stuck(tempCopy):
                            print(f"Remote Pair (Row) 2: {[(a, b), (x, y)]} removed {pennedIntersection} from {eNodes}")
                            return
                    # otherwise it checks for what values are pencilled in
                    elif len(remoteIntersection) == 1 and len(pencilIntersection) == 1:
                        self.updateNotesDX(eNodes, pencilIntersection)
                        if not self.stuck(tempCopy):
                            print(f"Remote Pair (Row) 3: {[(a, b), (x, y)]} removed {pencilIntersection} from {eNodes}")
                            return
            colPairs = self.getColChuteRemotePairs(comboSet)
            if len(colPairs) != 0:
                for (a, b), (x, y) in colPairs:
                    colOffset1, rowOffset1, rowOffset2 = self.getOffset(b), self.getOffset(a), self.getOffset(x)
                    otherCells = {(r, c) for r in range(9) for c in range(colOffset1, colOffset1 + 3) if c not in {b, y} and not (rowOffset1 <= r < rowOffset1 + 3 or rowOffset2 <= r < rowOffset2 + 3)}
                    pencilSet, pennedSet = set(), set()
                    for r, c in otherCells:
                        if self.locked[r][c]:
                            pennedSet.add(self.layout[r][c].val)
                        else:
                            pencilSet |= self.getSet((r, c))
                    remoteIntersection = comboSet & (pencilSet | pennedSet)
                    pencilIntersection = comboSet & pencilSet
                    pennedIntersection = comboSet & pennedSet
                    eNodes = [(eRow, y) for eRow in range(rowOffset1, rowOffset1 + 3)] + [(eRow, b) for eRow in range(rowOffset2, rowOffset2 + 3)]
                    # if neither value in the remote pair is penned in, then performs double elimination
                    if len(pencilSet) == 0 and len(pennedIntersection) == 0:
                        eNodes += [(eRow, y) for eRow in range(rowOffset2, rowOffset2 + 3) if eRow != x] + [(eRow, b) for eRow in range(rowOffset1, rowOffset1 + 3) if eRow != a]
                        self.updateNotesDX(eNodes, comboSet)
                        if not self.stuck(tempCopy):
                            print(f"Remote Pair (Col) 1: {[(a, b), (x, y)]} removed {comboSet} from {eNodes}")
                            return
                        # if only one remote pair is penned in, erases that value from the appropraite nodes
                    elif len(pennedIntersection) == 1 and len(pencilIntersection) == 0:
                        self.updateNotesDX(eNodes, pennedIntersection)
                        if not self.stuck(tempCopy):
                            print(f"Remote Pair (Col) 3: {[(a, b), (x, y)]} removed {pennedIntersection} from {eNodes}")
                            return
                    # otherwise it checks for what values are pencilled in
                    elif len(remoteIntersection) == 1 and len(pencilIntersection) == 1:
                        self.updateNotesDX(eNodes, pencilIntersection)
                        if not self.stuck(tempCopy):
                            print(f"Remote Pair (Col) 3: {[(a, b), (x, y)]} removed {pencilIntersection} from {eNodes}")
                            return
    def getRowChuteRemotePairs(self, combo):
        remotePairs = []
        for rowBlock in range(0, 9, 3):
            for i in range(rowBlock, rowBlock + 3):
                for j in range(9):
                    if self.locked[i][j]:
                        continue
                    tempSet = self.getSet((i, j))
                    if tempSet != combo:
                        continue
                    for a in range(rowBlock, rowBlock + 3):
                        if a == i:
                            continue
                        for b in range(9):
                            if (j//3) == (b//3) or self.locked[a][b]:
                                continue
                            temp = self.getSet((a, b))
                            if temp == combo and [(a, b), (i, j)] not in remotePairs:
                                remotePairs.append([(i, j), (a, b)])
        return remotePairs
    def getColChuteRemotePairs(self, combo):
        remotePairs = []
        for colBlock in range(0, 9, 3):
            for j in range(colBlock, colBlock + 3):
                for i in range(9):
                    if self.locked[i][j]:
                        continue
                    tempSet = self.getSet((i, j))
                    if tempSet != combo:
                        continue
                    for b in range(colBlock, colBlock + 3):
                        if b == j:
                            continue
                        for a in range(9):
                            if (i // 3) == (a // 3) or self.locked[a][b]:
                                continue
                            temp = self.getSet((a, b))
                            if temp == combo and [(a, b), (i, j)] not in remotePairs:
                                remotePairs.append([(i, j), (a, b)])
        return remotePairs
    # ********************************************************************************************************************
    def simpleColoringUtil(self, tempCopy):
        for val in self.getRemaining():
            self.simpleColoring(val, tempCopy)
            if not self.stuck(tempCopy):
                return
    def simpleColoring(self, val, tempCopy):
        nodesDone, completedGroups = [], []
        for i in range(9):
            for j in range(9):
                if not tempCopy.stuck(self):
                    return
                if val not in self.layout[i][j].note or (i, j) in nodesDone:
                    continue
                fullLoop, newNodes = [[(i, j)]], [(i, j)]
                nodesDone.append((i, j))
                while newNodes:
                    tempLoop = []
                    for node in newNodes:
                        temp = self.getConnectedSCNodes(val, node, nodesDone)
                        tempLoop += temp
                        nodesDone += temp
                    if not tempLoop:
                        break
                    newNodes = tempLoop
                    fullLoop.append(tempLoop)
                if len(fullLoop) > 1:
                    completedGroups += [fullLoop]
                # rule 2
                for group in completedGroups:
                    colorNodes, colorNodesDict, color, badColor = [], {}, 'yellow', ''
                    for layer in group:
                        color = 'green' if color == 'yellow' else 'yellow'
                        for node in layer:
                            colorNodes.append((node, color))
                            colorNodesDict[node] = color
                    # rule2
                    if len(colorNodes) <= 2:
                        continue
                    for (a, colorA), (b, colorB) in itertools.combinations(colorNodes, 2):
                        if colorA != colorB:
                            continue
                        if self.inBox([a, b]) or self.inRow([a, b]) or self.inCol([a, b]):
                            badColor = colorA
                            for node, color in colorNodes:
                                if color != badColor:
                                    x, y = node
                                    print(f"SimpleColoring rule 2 found {val} at index {(x, y)}")
                                    self.layout[x][y].setVal(val)
                                    self.singleLockReset((x, y))
                            if not tempCopy.stuck(self):
                                return
                    # rule 4
                    rawNodes = list(colorNodesDict.keys())
                    endNodes = [n for n in rawNodes if len(self.getConnectedSCNodes(val, n, [])) == 1]
                    if len(endNodes) != 2:
                        continue
                    n1, n2 = endNodes
                    if colorNodesDict[n1] == colorNodesDict[n2]:
                        continue
                    n1x, n1y = n1
                    n2x, n2y = n2
                    # rule 4 sit 1
                    if not self.sameRowChute(n1, n2) and not self.sameColChute(n1, n2):
                        otherNodes = [a for a in rawNodes if a not in (n1, n2)]
                        n1Check = all(not self.inBox([(n1x, n2y), a]) for a in otherNodes)
                        n2Check = all(not self.inBox([(n2x, n1y), a]) for a in otherNodes)
                        if n1Check:
                            self.updateNotesDX([(n1x, n2y)], {val})
                        if n2Check:
                            self.updateNotesDX([(n2x, n1y)], {val})
                        if not self.stuck(tempCopy):
                            print(f"Simple Coloring rule 4 sit 1 removed {val} from {(n1x, n2y)} and/or {(n2x, n1y)}")
                            return
                    # rule 4 sit 2 (rows)
                    elif self.sameRowChute(n1, n2) and not self.sameColChute(n1, n2) and n1[0] != n2[0]:
                        eNodes = [(n2x, a) for a in range((n1y//3) * 3, ((n1y//3) * 3) + 3)] + [(n1x, a) for a in range((n2y//3) * 3, ((n2y//3) * 3) + 3)]
                        self.updateNotesDX(eNodes, {val})
                        if not self.stuck(tempCopy):
                            print(f"Simple Coloring rule 4 sit 2 (row) removed {val} from {eNodes}")
                            return
                    # rule 4 sit 3 (cols)
                    elif not self.sameRowChute(n1, n2) and self.sameColChute(n1, n2) and n1[1] != n2[1]:
                        eNodes = [(a, n2y) for a in range((n1x//3) * 3, ((n1x//3) * 3) + 3)] + [(a, n1y) for a in range((n2x//3) * 3, ((n2x//3) * 3) + 3)]
                        self.updateNotesDX(eNodes, {val})
                        if not self.stuck(tempCopy):
                            print(f"Simple Coloring rule 4 sit 3 (col) removed {val} from {eNodes}")
                            return
    def getConnectedSCNodes(self, val, coord, visited):
        i, j = coord
        rowOffset, colOffset = self.getOffset(i), self.getOffset(j)
        connectedNodes, tempDone = [], []
        for a in range(rowOffset, rowOffset + 3):
            for b in range(colOffset, colOffset + 3):
                if (a, b) == (i, j) or (a, b) in visited:
                    continue
                if val in self.layout[a][b].note:
                    if self.singleBoxCheck([(i, j), (a, b)], {val}):
                        connectedNodes.append((a, b))
                        tempDone.append((a, b))
                    else:
                        break
        for b in range(9):
                if b == j or (i, b) in visited or (i, b) in tempDone:
                    continue
                if val in self.layout[i][b].note and self.singleRowCheck([(i, j), (i, b)], {val}):
                    if self.singleRowCheck([(i, j), (i, b)], {val}):
                        connectedNodes.append((i, b))
                    else:
                        break
        for a in range(9):
            if a == i or (a, j) in visited or (a, j) in tempDone:
                continue
            if val in self.layout[a][j].note:
                if self.singleColCheck([(i, j), (a, j)], {val}):
                    connectedNodes.append((a, j))
                else:
                    break
        return connectedNodes
    # ********************************************************************************************************************
    # y wing
    def yWing(self):
        tempCopy = copy.deepcopy(self)
        for i in range(9):
            for j in range(9):
                if self.layout[i][j].val != 0:
                    continue
                tempSet = self.getSet((i, j))
                if len(tempSet) != 2:
                    continue
                rowOffset, colOffset = self.getOffset(i), self.getOffset(j)
                colWing, rowWing = set(), set()
                # looks for candidate in column
                for row in range(9):
                    if rowOffset <= row < rowOffset + 3 or self.locked[row][j]:
                        continue
                    temp = self.getSet((row, j))
                    if len(temp) == 2 and len(temp & tempSet) == 1:
                        colWing.add((row, j))
                # looks for candidate in row
                for col in range(9):
                    if colOffset <= col < (colOffset + 3) or self.locked[i][col]:
                        continue
                    temp = self.getSet((i, col))
                    if len(temp) == 2 and len(temp & tempSet) == 1:
                        rowWing.add((i, col))
                if len(rowWing) > 0 and len(colWing) > 0:
                    for rx, ry in rowWing:
                        tempRowSet = self.getSet((rx, ry))
                        for cx, cy in colWing:
                            tempColSet = self.getSet((cx, cy))
                            if len(tempRowSet | tempColSet | tempSet) != 3 or self.layout[rx][ry].note == self.layout[cx][cy].note:
                                continue
                            tempRowSet, tempColSet = self.getSet((rx, ry)), self.getSet((cx, cy))
                            eVal = tempRowSet & tempColSet
                            if len(eVal) != 1:
                                continue
                            self.updateNotesDX([(cx, ry)], eVal)
                            if not self.stuck(tempCopy):
                                print(f"Y-Wing Sit 1, Root: {(i, j)}, rowWing {(rx, ry)}, colWing{(cx, cy)}\nErasing {eVal} at {(cx, ry)}")
                                return
                elif len(rowWing) > 0 and len(colWing) == 0:
                    for rx, ry in rowWing:
                        tempRowSet = self.getSet((rx, ry))
                        targetSet = (tempSet | tempRowSet) - (tempSet & tempRowSet)
                        for a in range(rowOffset, rowOffset + 3):
                            if a == i:
                                continue
                            for b in range(colOffset, colOffset + 3):
                                if b == j:
                                    continue
                                tempBoxSet = self.getSet((a, b))
                                if tempBoxSet == targetSet and len(self.getExRowIdxs((a, b), targetSet)) == 1:
                                    eVal = tempRowSet & tempBoxSet
                                    eCells = set()
                                    for eCol in range(colOffset, colOffset + 3):
                                        eCells.add((i, eCol))
                                    for eCol in range((ry//3) * 3, ((ry//3) * 3) + 3):
                                        eCells.add((a, eCol))
                                    eCells = eCells - {(i, j)}
                                    self.updateNotesDX(eCells, eVal)
                                    if not self.stuck(tempCopy):
                                        print(f"Y-Wing Sit 2.Row, Root: {(i, j)}, rowWing: {(rx, ry)}, boxNode: {(a, b)}\nRow Erasing {eVal} at {eCells}")
                                        return
                elif len(colWing) > 0 and len(rowWing) == 0:
                    for cx, cy in colWing:
                        tempColSet = self.getSet((cx, cy))
                        targetSet = (tempSet | tempColSet) - (tempSet & tempColSet)
                        for b in range(colOffset, colOffset + 3):
                            if b == j:
                                continue
                            for a in range(rowOffset, rowOffset + 3):
                                if a == i:
                                    continue
                                tempBoxSet = self.getSet((a, b))
                                if tempBoxSet == targetSet and len(self.getExColIdxs((a, b), targetSet)) == 1:
                                    eVal = tempColSet & tempBoxSet
                                    eCells = set()
                                    for eRow in range(rowOffset, rowOffset + 3): 
                                        eCells.add((eRow, j))
                                    for eRow in range((cx//3) * 3,((cx//3) * 3) + 3):
                                        eCells.add((eRow, b))
                                    eCells = eCells - {(i, j)}
                                    self.updateNotesDX(eCells, eVal)
                                    if not self.stuck(tempCopy):
                                        print(f"Y-Wing Sit 2.Col, Root: {(i, j)}, colWing: {(cx, cy)}, boxNode: {(a, b)}\nCol Erasing {eVal} at {eCells}")
                                        return
    # ********************************************************************************************************************
    # rectangle elimination
    def rectangleElimination(self, tempCopy):
        remaining = self.getRemaining()
        currentRow = {val: {r: idxs for r in range(9) if (idxs := self.getAnyRowIdxs((r, 0), {val}))} for val in remaining}
        currentCol = {val: {c: idxs for c in range(9) if (idxs := self.getAnyColIdxs((0, c), {val}))} for val in remaining}
        for val in currentRow:
            for row in currentRow[val]:
                if len(currentRow[val][row]) != 2 or self.inBox(list(currentRow[val][row])):
                    continue
                for i, j in currentRow[val][row]:
                    rowNode = set(currentRow[val][row] - {(i, j)}).pop()
                    if (i, j) not in currentCol[val][j]:# or len(currentCol[val][j]) == 2:
                        continue
                    for colNode in currentCol[val][j]:
                        if self.inBox([colNode, (i, j)]) or not self.recCheck(rowNode, colNode, val):
                            continue
                        self.updateNotesDX([colNode], {val})
                        if not self.stuck(tempCopy):
                            print(f"Rectangle Elimination (row) removed {val} from {colNode}. Root: {(i, j)}, rowNode: {rowNode}")
                if not self.stuck(tempCopy):
                    return
            for col in currentCol[val]:
                if len(currentCol[val][col]) != 2 or self.inBox(list(currentCol[val][col])):
                    continue
                for i, j in currentCol[val][col]:
                    colNode = set(currentCol[val][col] - {(i, j)}).pop()
                    if (i, j) not in currentRow[val][i]:# or len(currentRow[val][i]) == 2:
                        continue
                    for rowNode in currentRow[val][i]:
                        if self.inBox([rowNode, (i, j)]) or not self.recCheck(rowNode, colNode, val):
                            continue
                        self.updateNotesDX([rowNode], {val})
                        if not self.stuck(tempCopy):
                            print(f"Rectangle Elimination (col) removed {val} from {rowNode}. Root: {(i, j)}, colNode: {colNode}")
                if not self.stuck(tempCopy):
                    return
    def recCheck(self, rowNode, colNode, val):
        rowOffset, colOffset = self.getOffset(colNode[0]), self.getOffset(rowNode[1])
        currentBox = self.getAnyBoxIdxs((rowOffset,colOffset), {val})
        if not currentBox:
            return False
        for row in range(rowOffset, rowOffset + 3):
            if row == colNode[0]:
                continue
            for col in range(colOffset, colOffset + 3):
                if col == rowNode[1]:
                    continue
                if val in self.layout[row][col].note:
                    return False
        return True
    # ********************************************************************************************************************
    # sword fish works the same way as an xwing, except its for triples includes triples
    def swordfishUtil(self, tempCopy):
        tempCopy = copy.deepcopy(self)
        for val in self.getRemaining():
            self.swordfish(val, tempCopy)
            if not self.stuck(tempCopy):
                return
                
    def swordfish(self, val, tempCopy):
        # works the same way as xwing
        rowSet = {r: {c for c in range(9) if val in self.layout[r][c].note} for r in range(9) if any(val in self.layout[r][c].note for c in range(9))}
        rowKeys = [r for r in rowSet if 2 <= len(rowSet[r]) <= 3]
        for i in range(len(rowKeys)):
            for j in range(i + 1, len(rowKeys)):
                for k in range(j + 1, len(rowKeys)):
                    r1, r2, r3 = rowKeys[i], rowKeys[j], rowKeys[k]
                    cols = rowSet[r1] | rowSet[r2] | rowSet[r3]
                    if len(cols) == 3:
                        tempRowSet = {r1, r2, r3}
                        tempColSet = cols
                        for c in tempColSet:
                            ignore_nodes = [(r, c) for r in tempRowSet]
                            self.subUpdateNotes('col', ignore_nodes, {val})
                        if not self.stuck(tempCopy):
                            print(f"Swordfish on value {val}: rows {sorted(tempRowSet)}, columns {sorted(tempColSet)}")
                            return
        colSet = {c: {r for r in range(9) if val in self.layout[r][c].note} for c in range(9) if any(val in self.layout[r][c].note for r in range(9))}
        colKeys = [c for c in colSet if 2 <= len(colSet[c]) <= 3]
        for i in range(len(colKeys)):
            for j in range(i + 1, len(colKeys)):
                for k in range(j + 1, len(colKeys)):
                    c1, c2, c3 = colKeys[i], colKeys[j], colKeys[k]
                    rows = colSet[c1] | colSet[c2] | colSet[c3]
                    if len(rows) == 3:
                        tempColSet = {c1, c2, c3}
                        tempRowSet = rows
                        for r in tempRowSet:
                            ignore_nodes = [(r, c) for c in tempColSet]
                            self.subUpdateNotes('row', ignore_nodes, {val})
                        if not self.stuck(tempCopy):
                            print(f"Swordfish on value {val}: columns {sorted(tempColSet)}, rows {sorted(tempRowSet)}")
                            return

    # ********************************************************************************************************************
    # xyz-wing
    def xyzWing(self, tempCopy):
        tempCopy = copy.deepcopy(self)
        for i in range(9):
            for j in range(9):
                if self.layout[i][j].val != 0:
                    continue
                tempSet = self.getSet((i, j))
                if len(tempSet) != 3:
                    continue
                colWing, rowWing = set(), set()
                rowOffset, colOffset = self.getOffset(i), self.getOffset(j)
                # looks for candidate in column
                for row in range(9):
                    if row == i or self.locked[row][j]:
                        continue
                    temp = self.getSet((row, j))
                    if len(temp) == 2 and len(temp & tempSet) == 2:
                        colWing.add((row,j))
                # looks for candidate in row
                for col in range(9):
                    if col == j or self.locked[i][col]:
                        continue
                    temp = self.getSet((i, col))
                    if len(temp) == 2 and len(temp & tempSet) == 2:
                        rowWing.add((i,col))
                if len(rowWing) > 0 and len(colWing) > 0:
                    for a, b in rowWing:
                        tempRowSet = self.getSet((a, b))
                        for c, d in colWing:
                            tempColSet = self.getSet((c, d))
                            if len(tempRowSet | tempColSet | tempSet) == 3 and self.layout[a][b].note != self.layout[c][d].note:
                                valToErase, eNodes = tempRowSet & tempColSet, set() 
                                if len(valToErase) != 1:
                                    continue
                                val = valToErase.pop()
                                if self.inBox([(i, j), (a, b)]) and not self.inBox([(i, j), (c, d)]):
                                    eNodes = set()
                                    for eRow in range(rowOffset, rowOffset + 3):
                                        if eRow == i:
                                            continue
                                        eNodes.add((eRow, j))
                                elif self.inBox([(i, j), (c, d)]) and not self.inBox([(i, j), (a, b)]):
                                    for eCol in range(colOffset, colOffset + 3):
                                        if eCol == j:
                                            continue 
                                        eNodes.add((i, eCol))
                                self.updateNotesDX(list(eNodes), {val})
                                if not self.stuck(tempCopy):
                                    print(f"XYZ-Wing Sit 1 Root: {(i, j)}, rowWing {(a, b)}, colWing{(c, d)}\nErasing {val} at {eNodes}")
                                    return
                elif len(rowWing) > 0 and len(colWing) == 0:
                    for x, y in rowWing:
                        if self.inBox([(x, y), (i, j)]):
                            continue
                        tempRowSet = self.getSet((x, y))
                        for a in range(rowOffset, rowOffset + 3):
                            if a == i:
                                continue
                            for b in range(colOffset, colOffset + 3):
                                if b == j:
                                    continue
                                tempBoxSet = self.getSet((a, b))
                                if len(tempBoxSet) == 2 and len(tempBoxSet | tempRowSet | tempSet) == 3 and tempBoxSet != tempRowSet:
                                    eVal, eNodes = (tempRowSet & tempBoxSet).pop(), set()
                                    for eCol in range(colOffset, colOffset + 3):
                                        if eCol == j:
                                            continue
                                        eNodes.add((i, eCol))
                                    self.updateNotesDX(list(eNodes), {eVal})
                                    if not self.stuck(tempCopy):
                                        print(f"XYZ-Wing Sit 2 Row, Root: ({i}, {j}), rowWing {(x, y)}, boxWing {(a, b)}")
                                        return
                elif len(colWing) > 0 and len(rowWing) == 0:
                    for x, y in colWing:
                        if self.inBox([(x, y), (i, j)]):
                            continue
                        tempColSet = self.getSet((x, y))
                        for a in range(rowOffset, rowOffset + 3):
                            if a == i:
                                continue
                            for b in range(colOffset, colOffset + 3):
                                if b == j:
                                    continue
                                tempBoxSet = self.getSet((a, b))
                                if len(tempBoxSet) == 2 and len(tempBoxSet | tempColSet | tempSet) == 3 and tempBoxSet != tempColSet:
                                    eVal, eNodes = (tempColSet & tempBoxSet).pop(), set()
                                    for eRow in range(rowOffset, rowOffset + 3):
                                        if eRow == i:
                                            continue
                                        eNodes.add((eRow, j))
                                    self.updateNotesDX(list(eNodes), {eVal})
                                    if not self.stuck(tempCopy):
                                        print(f"XYZ-Wing Sit 2 Col, Root: ({i}, {j}), colWing {(x, y)}, boxWing {(a, b)}")
                                        return
    # ********************************************************************************************************************
    def bug(self):
        bugFound = False
        for i in range(9):
            for j in range(9):
                if self.locked[i][j]:
                    continue
                tempSet = self.getSet((i, j))
                if len(tempSet) > 3 or (len(tempSet) == 3 and bugFound):
                    return
                if len(tempSet) == 3 and not bugFound:
                    bugx, bugy = i, j
                    bugFound = True
        if not bugFound:
            return
        valCount = {val: 0 for val in self.getSet((bugx, bugy))}
        for val in valCount:
            for row in range(9):
                if val in self.layout[row][bugy].note:
                    valCount[val] = valCount[val] + 1
            for col in range(9):
                if val in self.layout[bugx][col].note:
                    valCount[val] = valCount[val] + 1
            for row in range((bugx//3) * 3,((bugx//3) * 3) + 3):
                for col in range((bugy//3) * 3,((bugy//3) * 3) + 3):
                    if val in self.layout[row][col].note:
                        valCount[val] = valCount[val] + 1
        for val in valCount:
            if valCount[val] == 9:
                print(f"BUG found {val} at ({bugx}, {bugy})")
                self.layout[bugx][bugy].setVal(val)
                self.singleLockReset((bugx, bugy))
    # ********************************************************************************************************************
    # Spots deadly patterns. Unsure if it's a valid strategy because some puzzles actually require deadly patterns to exist in the first place. Currently disabled
    def avoidableRectangles(self, tempCopy):
        remaining = self.getRemaining()
        for val in remaining:
            for i in range(9):
                for j in range(9):
                    if val != self.layout[i][j].val:
                        continue
                    rowOffset, colOffset = self.getOffset(i), self.getOffset(j)
                    for col in range(colOffset, colOffset + 3):
                        if col == j or not self.locked[i][col]:
                            continue
                        for row in range(9):
                            if rowOffset <= row < rowOffset + 3:
                                continue
                            if self.layout[i][col].val == self.layout[row][j].val and len(self.getSet((row, col))) == 2:
                                self.updateNotesDX([(row, col)], {val})
                            if not self.stuck(tempCopy):
                                return print(f"Avoidable Rectangles 2 (in row) removed {val} from {(row, col)} because of pair {(i, j), (i, col)} & node {(row, j)}")
                    for row in range(rowOffset, rowOffset + 3):
                        if row == i or not self.locked[row][j]:
                            continue
                        for col in range(9):
                            if colOffset <= col < colOffset + 3:
                                continue
                            if self.layout[row][j].val == self.layout[i][col].val and len(self.getSet((row, col))) == 2:
                                self.updateNotesDX([(row, col)], {val})
                            if not self.stuck(tempCopy):
                                return print(f"Avoidable Rectangles 2 (in col) removed {val} from {(row, col)} because of pair {(i, j), (row, j)} & node {(i, col)}")
        for i in range(9):
            for j in range(0, 9, 3):
                rowOffset = self.getOffset(i)
                valSet1 = {self.layout[i][x].val for x in range(j, j + 3)}
                if 0 in valSet1 or len(valSet1 & remaining) != 2:
                    continue
                for row1 in range(9):
                    if rowOffset <= row1 < rowOffset + 3:
                        continue
                    valSet2 = {self.layout[row1][x].val for x in range(j, j + 3)}
                    if 0 not in valSet2 or len(valSet1 & valSet2) != 2:
                        continue
                    for col in range(j, j + 3):
                        if self.layout[row1][col].val == 0:
                            eCol1 = col
                    rowOffset1 = self.getOffset(row1)
                    for row2 in range(9):
                        if rowOffset <= row2 < rowOffset + 3 or rowOffset1 <= row2 < rowOffset1 + 3:
                            continue
                        valSet3 = {self.layout[row2][x].val for x in range(j, j + 3)}
                        if 0 not in valSet3 or (len(valSet3 & valSet1) != 2 and len((valSet3 & valSet2) - {0}) != 1):
                            continue
                        for col in range(j, j + 3):
                            if self.layout[row2][col].val == 0:
                                eCol2 = col
                        if eCol1 != eCol2:
                            self.updateNotesDX([(row1, eCol1), (row2, eCol2)], valSet1)
                        if not self.stuck(tempCopy):
                            return print(f"Avoidable Rectangles 3 (inRow) removed {valSet1} from {(row1, eCol1), (row2, eCol2)}")
        for j in range(9):
            for i in range(0, 9, 3):
                colOffset = self.getOffset(j)
                valSet1 = {self.layout[x][j].val for x in range(i, i + 3)}
                if 0 in valSet1 or len(valSet1 & remaining) != 2:
                    continue
                for col1 in range(9):
                    if colOffset <= col1 < colOffset + 3:
                        continue
                    valSet2 = {self.layout[x][col1].val for x in range(i, i + 3)}
                    if 0 not in valSet2 or len(valSet1 & valSet2) != 2:
                        continue
                    for row in range(i, i + 3):
                        if self.layout[row][col1].val == 0:
                            eRow1 = row
                    colOffset1 = self.getOffset(col1)
                    for col2 in range(9):
                        if colOffset <= col2 < colOffset + 3 or colOffset1 <= col2 < colOffset1 + 3:
                            continue
                        valSet3 = {self.layout[x][col2].val for x in range(i, i + 3)}
                        if 0 not in valSet3 or (len(valSet3 & valSet1) != 2 and len((valSet3 & valSet2) - {0}) != 1):
                            continue
                        for row in range(i, i + 3):
                            if self.layout[row][col2].val == 0:
                                eRow2 = row
                        if eRow1 != eRow2:
                            self.updateNotesDX([(eRow1, col1), (eRow2, col2)], valSet1)
                        if not self.stuck(tempCopy):
                            return print(f"Avoidable Rectangles 3 (inCol) removed {valSet1} from {(eRow1, col1), (eRow2, col2)}")
    # ********************************************************************************************************************
    # ***********************************************DIABOLICAL STRATEGIES************************************************
    # ********************************************************************************************************************
    # Right now I don't think xCycles rules 2 and 3 work. mostly because rule 1 and rectangle elimination keep getting in the way
    def xCycles(self, tempCopy):
        remaining = self.getRemaining()
        functions = {(self.inRow, self.getAnyRowIdxs), (self.inCol, self.getAnyColIdxs), (self.inBox, self.getAnyBoxIdxs)}
        for val in remaining:
            doneCycles = set()
            rule2Crits, rule3Crits = [], []
            for i in range(9):
                for j in range(9):
                    if self.locked[i][j] or val not in self.layout[i][j].note:
                        continue
                    firstFuncs = {}
                    for _, func in functions:
                        if func((i, j), {val}): firstFuncs[func] = func((i, j), {val}) - {(i, j)}
                    cycles = self.getCycle([(i, j)], val, doneCycles, [], firstFuncs, rule2Crits, rule3Crits)
                    if not cycles:
                        continue
                    for ruleType, cycle in cycles:
                        eCells = set()
                        if ruleType == 1:
                            for x in range(len(cycle) - 1):
                                for funcType, getFunc in functions:
                                    if funcType([cycle[x], cycle[x + 1]]):
                                        eCells |= getFunc(cycle[x], {val}) - {cycle[x], cycle[x + 1]}
                            if eCells:
                                self.updateNotesDX(eCells, {val})
                                if not self.stuck(tempCopy):
                                    print(f"Cycle: {cycle}\nNice loops Rule 1 removed {val} from {list(eCells)}")
                        elif ruleType == 2:
                            solvedNodeX, solvedNodeY = cycle[-3]
                            self.layout[solvedNodeX][solvedNodeY].setVal(val)
                            self.singleLockReset((solvedNodeX, solvedNodeY))
                            print(f"Cycle: {cycle}\nNice loops Rule 2 found {val} at {(solvedNodeX, solvedNodeY)}")
                        elif ruleType == 3:
                            solvedNodeX, solvedNodeY = cycle[-2]
                            self.layout[solvedNodeX][solvedNodeY].note[val-1] = 0
                            print(f"Cycle: {cycle}\nNice loops Rule 3 removed {val} from {(solvedNodeX, solvedNodeY)}")
                    if not self.stuck(tempCopy):
                        return
                            
    def getCycle(self, coords, val, doneCycles, allCycles, firstFuncs, rule2Crits, rule3Crits, lastWeak=None):
        current = coords[-1]
        strongFuncs = {self.getAnyRowIdxs, self.getAnyColIdxs, self.getAnyBoxIdxs}
        for strongFunc in strongFuncs - {lastWeak}:
            strongSet = strongFunc(current, {val}) - {current}
            weakFuncs = strongFuncs - {strongFunc}
            if any(otherFunc(current, {val}) - {current} == strongSet for otherFunc in weakFuncs):
                continue
            for strongNode in strongSet:
                for weakFunc in weakFuncs:
                    weakCandidates = weakFunc(strongNode, {val}) - {strongNode}
                    for weakNode in weakCandidates:
                        currentCycle = coords + [strongNode, weakNode]
                        cycleKey = tuple(sorted(set(currentCycle)))
                        if cycleKey in doneCycles:
                            continue
                        if len(currentCycle) > 3 and weakNode == coords[0] and len(strongSet) == 1 and len(set(currentCycle)) == len(currentCycle) - 1:
                            allCycles.append((1, coords + [strongNode, weakNode]))
                            doneCycles.add(cycleKey)
                        if weakNode != coords[0] and len(strongSet) == 1 and strongNode not in coords:
                            self.getCycle(currentCycle, val, doneCycles, allCycles, firstFuncs, rule2Crits, rule3Crits, weakFunc)
        discCycle = coords + [coords[0]]
        discKey = tuple(sorted(set(discCycle)))
        if len(coords) > 3 and discKey not in discCycle and coords[-2] not in rule2Crits and current not in rule3Crits:
            for func, startSet in firstFuncs.items():
                if current in startSet:
                    if len(lastWeak(coords[-2], {val})) == 2:
                        if discKey not in doneCycles:
                            rule2Crits.append(coords[-2])
                            allCycles.append((2, discCycle))
                            doneCycles.add(discKey)
                        break
                    if len(lastWeak(coords[-2], {val})) > 2 and len(func(coords[0], {val})) > 2:
                        if discKey not in doneCycles:
                            rule3Crits.append(current)
                            allCycles.append((3, discCycle))
                            doneCycles.add(discKey)
        return allCycles
    # ********************************************************************************************************************
    def medusa3D(self, tempCopy):
        # print("Welcome to medusa")
        remaining = sorted(self.getRemaining())
        completedGroups = []
        for val in remaining:
            nodesDone = []
            for i in range(9):
                for j in range(9):
                    if val not in self.layout[i][j].note or any((i, j, val, color) in nodesDone for color in {'yellow','green'}): continue
                    firstNode = (i, j, val, 'green')
                    fullLoop, newNodes = [[firstNode]], [firstNode]
                    while True:
                        tempLoop = []
                        for currentNode in newNodes:
                            temp = self.getMedusaNodes(currentNode, nodesDone)
                            nodesDone += [currentNode]
                            tempLoop += temp
                            if temp: nodesDone += temp
                        if len(tempLoop) == 0:
                            break
                        newNodes = tempLoop
                        fullLoop += [tempLoop]
                    if len(fullLoop) > 2:
                        completedGroups += [fullLoop]
        eCells4 = {}
        for group in completedGroups:
            normalized, eCells, eCells5 = [], {}, {}
            for subGroup in group:
                for node in subGroup:
                    normalized += [node]
            for a, b in itertools.combinations(normalized, 2):
                ax, ay, aVal, aColor = a
                bx, by, bVal, bColor = b
                if a != b:
                    # rule 1
                    if (ax, ay, aColor) == (bx, by, bColor) and aVal != bVal:
                        print(f"3D Medusa Rule 1 found {aVal} at {(ax, ay)} and {bVal} at {(bx, by)}, removing all {aColor} nodes")
                        for x, y, val, color in normalized:
                            if color == aColor == bColor:
                                if val not in eCells:
                                    eCells[val] = set()
                                eCells[val].add((x, y))
                        for val, cells in eCells.items():
                            print(f"Removing {val} from {cells}")
                            self.updateNotesDX(cells, {val})
                        return
                    # Rule 2
                    if (aVal, aColor) == (bVal, bColor) and self.hasConnection([(ax, ay), (bx, by)]):
                        print(f"3D Medusa Rule 2 found {aVal} at {(ax, ay)} and {bVal} at {(bx, by)}, removing all {aColor} nodes")
                        for x, y, val, color in normalized:
                            if color == aColor == bColor:
                                if val not in eCells:
                                    eCells[val] = set()
                                eCells[val].add((x, y))
                        for val, cells in eCells.items():
                            print(f"Removing {val} from {cells}")
                            self.updateNotesDX(cells, {val})
                        return
                    
                    # Rule 3
                    if (ax, ay) == (bx, by) and aColor != bColor and aVal != bVal and len(self.getMedusaNodes((ax, ay, aVal, aColor), [])) == 1 and len(self.getMedusaNodes((bx, by, bVal, bColor), [])) == 1 and len(self.getSet((ax, ay))) > 2:
                        print(f"3D Medusa Rule 3 {(ax, ay, aVal, aColor)} {(bx, by, bVal, bColor)}")
                        for val in self.getSet((ax, ay)):
                            if val == aVal or val == bVal: continue
                            eCells[val] = set()
                            eCells[val].add((ax, ay))
                        for val, cells in eCells.items():
                            print(f"Removing {val} from {cells}")
                            self.updateNotesDX(cells, {val})
                        return
            # Rule 4
            for val in remaining:
                for i in range(9):
                    for j in range(9):
                        if val not in self.layout[i][j].note or any((i, j, val, color) in normalized for color in {'yellow', 'green'}): continue
                        for a, b in itertools.combinations(normalized, 2):
                            ax, ay, aVal, aColor = a
                            bx, by, bVal, bColor = b
                            if a == b or aColor == bColor or val != aVal or aVal != bVal: continue
                            if self.hasConnection([(i, j), (ax, ay)]) and self.hasConnection([(i, j), (bx, by)]):
                                if val not in eCells4:
                                    eCells4[val] = set()
                                eCells4[val].add((i, j))
            # Rule 5
            for a, b in itertools.combinations(normalized, 2):
                ax, ay, aVal, aColor = a
                bx, by, bVal, bColor = b
                if (ax, ay) == (bx, by) or aColor == bColor or aVal == bVal or not self.hasConnection([(ax, ay), (bx, by)]):
                    continue
                if bVal in self.getSet((ax, ay)):
                    if bVal not in eCells5:
                        eCells5[bVal] = set()
                    eCells5[bVal].add((ax, ay))
                if aVal in self.getSet((bx, by)):
                    if aVal not in eCells5:
                        eCells5[aVal] = set()
                    eCells5[aVal].add((bx, by))
            # Rule 6
            for i in range(9):
                for j in range(9):
                    if self.locked[i][j] or any((i, j, val, color) in normalized for val in remaining for color in {'yellow', 'green'}): continue
                    tempSet = self.getSet((i, j))
                    goal = {color: {val: set() for val in tempSet} for color in {'yellow', 'green'}}
                    for x, y, val, color in normalized:
                        if val in tempSet and self.hasConnection([(i, j), (x, y)]):
                            goal[color][val].add((x, y))
                    for color, vals in goal.items():
                        if any(not coords for coords in vals.values()): continue
                        print(f"3D Medusa Rule 6 removing all {color} nodes")
                        for x, y, val, eColor in normalized:
                            if eColor != color: continue
                            if val not in eCells:
                                eCells[val] = set()
                            eCells[val].add((x, y))
                        for val, cells in eCells.items():
                            self.updateNotesDX(cells, {val})
                            print(f"Removing {val} from {cells}.")
                        return     
        if eCells4:
            print("3D Medusa Rule 4")
            for val, cells in eCells4.items():
                self.updateNotesDX(cells, {val})
                print(f"Removing {val} from {cells}")
        if eCells5:
            print("3D Medusa Rule 5")
            for val, cells in eCells5.items():
                print(f"Removing {val} from {cells}")
                self.updateNotesDX(cells, {val})
        if not self.stuck(tempCopy):
            return                   
    def getMedusaNodes(self, current, visited):
        i, j, currentVal, currentColor = current
        if currentColor == 'yellow': newColor = 'green'
        else: newColor = 'yellow'
        connectedNodes, newNodes = [], []
        tempSet = self.getSet((i, j))
        if len(tempSet) == 2:
            newVal = (tempSet - {currentVal}).pop()
            if not any((i, j, newVal, color) in visited for color in {'yellow', 'green'}):
                # connectedNodes += [(i, j, newVal, newColor)]
                connectedNodes.append((i, j, newVal, newColor))
        for func in {self.getAnyBoxIdxs, self.getAnyRowIdxs, self.getAnyColIdxs}:
            tempNodes = func((i, j), {currentVal}) - {(i, j)}
            if len(tempNodes) == 1:
                newNodes += tempNodes
        for x, y in newNodes:
            if any((x, y, currentVal, color) in visited for color in {'yellow', 'green'}): continue
            # connectedNodes += [(x, y, currentVal, newColor)]
            connectedNodes.append((x, y, currentVal, newColor))
        return connectedNodes
    # ********************************************************************************************************************
    def jellyFish(self, tempCopy):
        for val in self.getRemaining():
            rowSet = {r: {c for c in range(9) if val in self.layout[r][c].note} for r in range(9) if any(val in self.layout[r][c].note for c in range(9))}
            rowKeys = [r for r in rowSet if 2 <= len(rowSet[r]) <= 4]
            for rowCombo in itertools.combinations(rowKeys, 4):
                r1, r2, r3, r4 = rowCombo
                cols = rowSet[r1] | rowSet[r2] | rowSet[r3] | rowSet[r4]
                if len(cols) == 4:
                    tempRowSet = set(rowCombo)
                    tempColSet = cols
                    for c in tempColSet:
                        ignoreNodes = [(r, c) for r in tempRowSet]
                        self.subUpdateNotes('col', ignoreNodes, {val})
                    if not self.stuck(tempCopy):
                        print(f"Jellyfish on value {val}: rows {sorted(tempRowSet)}, columns {sorted(tempColSet)}")
                        return
            colSet = {c: {r for r in range(9) if val in self.layout[r][c].note} for c in range(9) if any(val in self.layout[r][c].note for r in range(9))}
            colKeys = [c for c in colSet if 2 <= len(colSet[c]) <= 4]
            for colCombo in itertools.combinations(colKeys, 4):
                c1, c2, c3, c4 = colCombo
                rows = colSet[c1] | colSet[c2] | colSet[c3] | colSet[c4]
                if len(rows) == 4:
                    tempColSet = set(colCombo)
                    tempRowSet = rows
                    for r in tempRowSet:
                        ignoreNodes = [(r, c) for c in tempColSet]
                        self.subUpdateNotes('row', ignoreNodes, {val})
                    if not self.stuck(tempCopy):
                        print(f"Jellyfish on value {val}: columns {sorted(tempColSet)}, rows {sorted(tempRowSet)}")
                        return
    # ********************************************************************************************************************

    def uniqueRectangles(self, tempCopy):
        rowSets, colSets, rowRPSets, colRPSets = set(), set(), set(), set()
        for combo in itertools.combinations(self.getRemaining(), 2):
            comboSet = set(combo)
            for row in range(9):
                matchingCols = [c for c in range(9) if self.getSet((row, c)) == comboSet]
                if len(matchingCols) == 2: rowSets.add((combo, row, matchingCols[0], matchingCols[1]))
            for col in range(9):
                matchingRows = [r for r in range(9) if self.getSet((r, col)) == comboSet]
                if len(matchingRows) == 2: colSets.add((combo, col, matchingRows[0], matchingRows[1]))
            rowRP = sorted(self.getRowChuteRemotePairs(comboSet))
            colRP = sorted(self.getColChuteRemotePairs(comboSet))
            for n1, n2 in rowRP: rowRPSets.add((combo, n1, n2))
            for n1, n2 in colRP: colRPSets.add((combo, n1, n2))
        print("RowSets")
        if rowSets:
            for combo, row, col1, col2 in rowSets:
                print(f"{combo}: {(row, col1)} {(row, col2)}")
        print("ColSets")
        if colSets:
            for combo, col, row1, row2 in colSets:
                print(f"{combo}: {(row1, col)} {(row2, col)}")
        for combo, row, col1, col2 in rowSets:
            comboSet = set(combo)
            n1, n2 = (row, col1), (row, col2)
            for tempRow in range(9):
                if row == tempRow or self.locked[tempRow][col1] or self.locked[tempRow][col2]: continue
                n3, n4 = (tempRow, col1), (tempRow, col2)
                n3Set, n4Set = self.getSet(n3), self.getSet(n4)
                if not (comboSet <= (n3Set & n4Set)): continue
                # Type 1
                if n3Set == comboSet and n4Set != comboSet:
                    self.updateNotesDX([n4], comboSet)
                    return print(f"Unique Rectangles Row Type 1 with floor {n1} & {n2} and vals {combo}, found vals {combo} at {n3}\nRemoving {combo} from {n4}")
                elif n4Set == comboSet and n3Set != comboSet:
                    self.updateNotesDX([n3], comboSet)
                    return print(f"Unique Rectangles Row Type 1 with floor {n1} & {n2} and vals {combo}, found vals {combo} at {n4}\nremoving {combo} from {n3}")
                
                if self.inBox([n1, n2]) and not self.inBox([n1, n3]): 
                    # Type 2A
                    if len(n3Set | n4Set) == 3 and n3Set == n4Set:
                        eVal = (n3Set - comboSet).pop()
                        self.subUpdateNotes('box', [n3, n4], {eVal})
                        self.subUpdateNotes('row', [n3, n4], {eVal})
                        if not self.stuck(tempCopy): return print(f"Unique Rectangles Row Type 2A with floor {n1} & {n2} and vals {combo}, found vals {n3Set} at {n3} & {n4}\nRemoving {eVal} from row and box")
                    if len(n3Set | n4Set) >= 3 and n3Set != n4Set:
                        # Type 3B
                        if len(n3Set) == len(n4Set) == 3:
                            targetSet = (n3Set | n4Set) - comboSet
                            targetNodes = self.getExRowIdxs((tempRow, col1), targetSet)
                            if targetNodes:
                                targetNode = targetNodes.pop()
                                self.subUpdateNotes('row', [targetNode, n3, n4], targetSet)
                            targetNodes = self.getExBoxIdxs((tempRow, col1), targetSet)
                            if targetNodes:
                                targetNode = targetNodes.pop()
                                self.subUpdateNotes('box', [targetNode, n3, n4], targetSet)
                            if not self.stuck(tempCopy): return print(f"Unique Rectangles Row Type 3B with floor {n1} & {n2} and vals {combo}, found {n3Set} at {n3} and {n4Set} at {n4}\nFound conditions to erase {targetSet} from row/box or both")
                        # Type 3/3B Pseudo
                        if (len(n3Set) == 3 and len(n4Set) == 4) or (len(n3Set) == 4 and len(n4Set) == 3):
                            x, y, z = self.findPseudoLoop('row', comboSet, [n3, n4])
                            if x: 
                                self.subUpdateNotes('row', y, z)
                                if not self.stuck(tempCopy): return print(f"Unique Rectangles Row Type 3/3B pseudo with floor {n1} & {n2} and vals {combo}, found ceiling {n3} & {n4}\nFound found a loop containing vals {z} at {y}, erasing {z} from row")
                        # Type 4A 
                        if self.singleRowCheck([n3, n4], {combo[0]}) ^ self.singleRowCheck([n3, n4], {combo[1]}):
                            if self.singleRowCheck([n3, n4], {combo[0]}): critVal, eVal = combo[0], combo[1]
                            else: critVal, eVal = combo[1], combo[0]
                            self.updateNotesDX([n3, n4], {eVal})
                            if not self.stuck(tempCopy): return print(f"Unique Rectangles Row Type 4A with floor {n1} & {n2} and vals {combo}, found {critVal} exclusive to row containing {n3} & {n4}\nRemoving {eVal} from nodes {n3} & {n4}")
                if not self.inBox([n1, n2]) and self.inBox([n1, n3]):
                    # Type 2B
                    if len(n3Set | n4Set) == 3 and n3Set == n4Set:
                        eVal = (n3Set - comboSet).pop()
                        self.subUpdateNotes('row', [n3, n4], {eVal})
                        if not self.stuck(tempCopy): return print(f"Unique Rectangles Row Type 2B with floor {n1} & {n2} and vals {combo}, found vals {n3Set} at {n3} & {n4}\nRemoving {eVal} from row")
                    # Type 3A
                    if len(n3Set | n4Set) == 4 and n3Set != n4Set and len(n3Set) == len(n4Set) == 3:
                        targetSet = (n3Set | n4Set) - comboSet
                        targetNodes = self.getExRowIdxs((tempRow, col1), targetSet)
                        if targetNodes:
                            targetNode = targetNodes.pop()
                            self.subUpdateNotes('row', [targetNode, n3, n4], targetSet)
                        if not self.stuck(tempCopy): return print(f"Unique Rectangles Row Type 3A with floor {n1} & {n2} and vals {combo}, found {n3Set} at {n3} and {n4Set} at {n4}\nFound {targetSet} at {targetNode}, erasing {targetSet} in row {tempRow}")
                    if self.singleRowCheck([n3, n4], {combo[0]}) ^ self.singleRowCheck([n3, n4], {combo[1]}):
                        if self.singleRowCheck([n3, n4], {combo[0]}): critVal, eVal = combo[0], combo[1]
                        else: critVal, eVal = combo[1], combo[0]
                        self.updateNotesDX([n3, n4], {eVal})
                        if not self.stuck(tempCopy): return print(f"Unique Rectangles Row Type 4B with floor {n1} & {n2} and vals {combo}, found {critVal} exclusive to row containing {n3} & {n4}\nRemoving {eVal} from nodes {n3} & {n4}")

        for combo, col, row1, row2 in colSets:
            comboSet = set(combo)
            n1, n2 = (row1, col), (row2, col)
            for tempCol in range(9):
                if col == tempCol or self.locked[row1][tempCol] or self.locked[row2][tempCol]: continue
                n3, n4 = (row1, tempCol), (row2, tempCol)
                n3Set, n4Set = self.getSet(n3), self.getSet(n4)
                if not (comboSet <= (n3Set & n4Set)): continue
                # Type 1
                if n3Set == comboSet and comboSet < n4Set:
                    self.updateNotesDX([n4], comboSet)
                    return print(f"Unique Rectangles Col Type 1 with floor {n1} & {n2} and vals {combo}, found vals {combo} at {n3}\nRemoving {combo} from {n4}")
                elif n4Set == comboSet and comboSet < n3Set:
                    self.updateNotesDX([n3], comboSet)
                    return print(f"Unique Rectangles Col Type 1 with floor {n1} & {n2} and vals {combo}, found vals {combo} at {n4}\nremoving {combo} from {n3}")
                
                if self.inBox([n1, n2]) and not self.inBox([n1, n3]):
                    # Type 2A
                    if len(n3Set | n4Set) == 3 and n3Set == n4Set:
                        eVal = (n3Set - comboSet).pop()
                        self.subUpdateNotes('box', [n3, n4], {eVal})
                        self.subUpdateNotes('col', [n3, n4], {eVal})
                        if not self.stuck(tempCopy): return print(f"Unique Rectangles Col Type 2A with floor {n1} & {n2} and vals {combo}, found vals {n3Set} at {n3} & {n4}\nRemoving {eVal} from row and box")
                            
                    if len(n3Set | n4Set) >= 3 and n3Set != n4Set:
                        # Type 3B
                        if len(n3Set) == len(n4Set) == 3:
                            targetSet = (n3Set | n4Set) - comboSet
                            targetNodes = self.getExColIdxs((row1, tempCol), targetSet)
                            if targetNodes:
                                targetNode = targetNodes.pop()
                                self.subUpdateNotes('col', [targetNode, n3, n4], targetSet)
                            targetNodes = self.getExBoxIdxs((row1, tempCol), targetSet)
                            if targetNodes:
                                targetNode = targetNodes.pop()
                                self.subUpdateNotes('box', [targetNode, n3, n4], targetSet)
                            if not self.stuck(tempCopy): return print(f"Unique Rectangles Col Type 3B with floor {n1} & {n2} and vals {combo}, found {n3Set} at {n3} and {n4Set} at {n4}\nFound conditions to erase {targetSet} from col/box or both")
                        # Type 3/3B Pseudo
                        if (len(n3Set) == 3 and len(n4Set) == 4) or (len(n3Set) == 4 and len(n4Set) == 3):
                            x, y, z = self.findPseudoLoop('col', comboSet, [n3, n4])
                            if x: 
                                self.subUpdateNotes('col', y, z)
                                if not self.stuck(tempCopy): return print(f"Unique Rectangles Col Type 3 pseudo with floor {n1} & {n2} and vals {combo}, found ceiling {n3} & {n4}\nFound found a loop containing vals {z} at {y}, erasing {z} from row")
                    # Type 4A
                    if self.singleColCheck([n3, n4], {combo[0]}) ^ self.singleColCheck([n3, n4], {combo[1]}):
                        if self.singleColCheck([n3, n4], {combo[0]}): critVal, eVal = combo[0], combo[1]
                        else: critVal, eVal = combo[1], combo[0]
                        self.updateNotesDX([n3, n4], {eVal})
                        if not self.stuck(tempCopy): return print(f"Unique Rectangles Col Type 4A with floor {n1} & {n2} and vals {combo}, found {critVal} exclusive to col containing {n3} & {n4}\nRemoving {eVal} from nodes {n3} & {n4}")
                                
                if not self.inBox([n1, n2]) and self.inBox([n1, n3]):
                    # Type 2B
                    if len(n3Set | n4Set) == 3 and n3Set == n4Set:
                        eVal = (n3Set - comboSet).pop()
                        self.subUpdateNotes('col', [n3, n4], {eVal})
                        if not self.stuck(tempCopy): return print(f"Unique Rectangles Col Type 2B with floor {n1} & {n2} and vals {combo}, found vals {n3Set} at {n3} & {n4}\nRemoving {eVal} from row")
                    # Type 3A
                    if len(n3Set | n4Set) == 4 and n3Set != n4Set and len(n3Set) == len(n4Set) == 3 and comboSet == (n3Set & n4Set):
                        targetSet = (n3Set | n4Set) - comboSet
                        targetNodes = self.getExColIdxs((row1, tempCol), targetSet)
                        if targetNodes:
                            targetNode = targetNodes.pop()
                            self.subUpdateNotes('col', [targetNode, n3, n4], targetSet)
                        if not self.stuck(tempCopy): return print(f"Unique Rectangles Col Type 3A with floor {n1} & {n2} and vals {combo}, found {n3Set} at {n3} and {n4Set} at {n4}\nFound {targetSet} at {(tempRow, tempCol)}, erasing {targetSet} in col {tempCol}")
                    # Type 4B
                    if self.singleColCheck([n3, n4], {combo[0]}) ^ self.singleColCheck([n3, n4], {combo[1]}):
                        if self.singleColCheck([n3, n4], {combo[0]}): critVal, eVal = combo[0], combo[1]
                        else: critVal, eVal = combo[1], combo[0]
                        self.updateNotesDX([n3, n4], {eVal})
                        if not self.stuck(tempCopy): return print(f"Unique Rectangles Col Type 4B with floor {n1} & {n2} and vals {combo}, found {critVal} exclusive to col containing {n3} & {n4}\nRemoving {eVal} from nodes {n3} & {n4}")
                    
        for combo, n1, n2 in colRPSets | rowRPSets:
            comboSet = set(combo)
            x1, y1 = n1
            x2, y2 = n2
            n3, n4 = (x1, y2), (x2, y1)
            r5Vals = {(node, val): [0, 0] for node in [n1, n2] for val in combo}
            n3Set, n4Set = self.getSet(n3), self.getSet(n4)
            if not(comboSet <= (n3Set & n4Set)): continue 
            if n3Set == n4Set and len(n3Set) == 3:
                eVal, eNodes = (n3Set - comboSet).pop(), []
                if self.sameColChute(n1, n2):
                    rowOffset1, rowOffset2 = self.getOffset(x1), self.getOffset(x2)
                    for row in range(rowOffset1, rowOffset1 + 3):
                        if row == x1: continue
                        eNodes += [(row, y1)]
                    for row in range(rowOffset2, rowOffset2 + 3):
                        if row == x2: continue
                        eNodes += [(row, y2)]
                if self.sameRowChute(n1, n2):
                    colOffset1, colOffset2 = self.getOffset(y1), self.getOffset(y2)
                    for col in range(colOffset1, colOffset1 + 3):
                        if col == y1: continue
                        eNodes += [(x1, col)]
                    for col in range(colOffset2, colOffset2 + 3):
                        if col == y2: continue
                        eNodes += [(x2, col)]
                self.updateNotesDX(eNodes, {eVal})
                if not self.stuck(tempCopy):
                    return print(f"Unique Rectangles Type 2C found {comboSet} in {n1} and {n2}, erasing {eVal} from {eNodes}")
            for val in combo:
                funcs = [self.singleRowCheck, self.singleColCheck]
                for base in [n1, n2]:
                    for check in [n3, n4]:
                        for func in funcs:
                            if not func([base, check], {val}):
                                r5Vals[(base, val)][0] += 1
                        if self.singleBoxCheck([base, check], {val}):
                            r5Vals[(base, val)][1] += 1
            for (node, critVal), countArry in r5Vals.items():
                print(node, critVal, countArry)
                if countArry[0] == 2 and countArry[1] == 1: 
                    eVal = (comboSet - {critVal}).pop()
                    self.updateNotesDX([node], {eVal})
            if not self.stuck(tempCopy): return print(f"Unique Rectangles Type 5 found {comboSet} in {n1} & {n2}\nFound that one of {combo} had strong links in the square, rows, and columns\nRemoving one of {combo} from either {n1}, {n2} or both")
                
    def findPseudoLoop(self, typeof, combo, ceilingNodes):
        ceiling = (self.getSet(ceilingNodes[0]) | self.getSet(ceilingNodes[1])) - combo
        for idx in range(9):
            if typeof == 'row': r, c = ceilingNodes[0][0], idx
            else: r, c = idx, ceilingNodes[0][1]
            if self.locked[r][c]: continue
            cand = self.getSet((r, c))
            if cand & combo: continue
            if not (cand & ceiling): continue
            coords = [(r, c)] + ceilingNodes
            master = set(cand)
            for step in range(idx + 1, 9):
                if typeof == 'row': rr, cc = r, step
                else: rr, cc = step, c
                if self.locked[rr][cc]: continue
                temp = self.getSet((rr, cc))
                if temp & combo: continue
                if not (temp & ceiling): continue
                coords.append((rr, cc))
                master |= temp
                if len(coords) >= 3 and len(master) == len(coords) - 1:
                    return True, coords, master
        return False, None, None
    # ********************************************************************************************************************
    def tridagonUtil(self):
        tempCopy = copy.deepcopy(self)
        remaining = self.getRemaining()
        for combo in itertools.combinations(remaining, 3):
            self.tridagon(set(combo), tempCopy)
            if not self.stuck(tempCopy):
                return
    def tridagon(self, combo, tempCopy):
        remaining = self.getRemaining()
        for combo in itertools.combinations(remaining, 3):
            for rBox in range(9):
                if rBox%3 != 0:
                    continue
                for cBox in range(9):
                    if cBox%3 != 0:
                        continue
                    rootPattern = self.getAscPattern((rBox, cBox), combo)
                    if rootPattern is not None and len(rootPattern) >= 3:
                        if not any(len(set(self.layout[r][c].note) - {0} - combo) > 0 for (r, c) in rootPattern):
                            # print(f"Ascending {combo} root {(rBox, cBox)}: {rootPattern}")
                            newBoxes = self.getFullBox((rBox, cBox))
                            for newSet in newBoxes:
                                allNodes = []
                                guardians = {i : set() for i in range(9)}
                                for x in newSet:
                                    temp = self.getDscPattern(x, combo)
                                    if temp is not None:
                                        allNodes += temp
                                if len(allNodes) != 9:
                                    continue
                                for tempX, tempY in allNodes:
                                    tempSet = set(self.layout[tempX][tempY].note) - {0} - combo
                                    if len(tempSet) > 0:
                                        for x in tempSet:
                                            guardians[x].add((tempX, tempY))
                                tempCount = 0
                                for x in guardians:
                                    tempCount += len(guardians[x])
                                if tempCount == 1:
                                    for x in guardians:
                                        if len(guardians[x]) == 1:
                                            current = guardians[x].pop()
                                            goodVal = set(self.layout[current[0]][current[1]].note) - {0} - combo
                                            goodVal = goodVal.pop()
                                            self.layout[current[0]][current[1]].setVal(goodVal)
                                            self.singleLockReset((current[0], current[1]))
                                            print(f"Tritagon ASC found {goodVal} at node {current}")
                                            return
                                elif tempCount == 2:
                                    for x in guardians:
                                        if len(guardians[x]) != 2 or not self.inBox(list(guardians[x])): 
                                            continue
                                        self.subUpdateNotes('box', list(guardians[x]), {x})
                                        if not self.stuck(tempCopy):
                                            print(f"Tritagon ASC found 2 gaurdians with {x} at nodes {guardians[x]}")
                                            return
                            
                    rootPattern = self.getDscPattern((rBox, cBox), combo)
                    if rootPattern is not None and len(rootPattern) >= 3:
                        if not any(len(set(self.layout[r][c].note) - {0} - combo) > 0 for (r, c) in rootPattern):
                            newBoxes = self.getFullBox((rBox, cBox))
                            for newSet in newBoxes:
                                allNodes = []
                                guardians = {i : set() for i in range(9)}
                                for x in newSet:
                                    temp = self.getAscPattern(x, combo)
                                    if temp is not None:
                                        allNodes += temp
                                if len(allNodes) != 9:
                                    continue
                                for tempX, tempY in allNodes:
                                    tempSet = set(self.layout[tempX][tempY].note) - {0} - combo
                                    if len(tempSet) > 0:
                                        for x in tempSet:
                                            guardians[x].add((tempX, tempY))
                                tempCount = 0
                                for x in guardians:
                                    tempCount += len(guardians[x])
                                if tempCount == 1:
                                    for x in guardians:
                                        if len(guardians[x]) == 1:
                                            current = guardians[x].pop()
                                            goodVal = set(self.layout[current[0]][current[1]].note) - {0} - combo
                                            goodVal = goodVal.pop()
                                            self.layout[current[0]][current[1]].setVal(goodVal)
                                            self.singleLockReset((current[0], current[1]))
                                            print(f"Tritagon DSC found {goodVal} at node {current}")
                                            return
                                elif tempCount == 2:
                                    for x in guardians:
                                        if len(guardians[x]) != 2 or not self.inBox(list(guardians[x])):
                                            continue
                                        self.subUpdateNotes('box', list(guardians[x]), {x}) 
                                        if not self.stuck(tempCopy):
                                            print(f"Tritagon DSC found 2 gaurdians with {x} at nodes {guardians[x]}")
                                            return
                    
        def getNodes(self, boxRoot, combo):
            rowOffset, colOffset = boxRoot
            goodNodes = []
            for row in range(rowOffset, rowOffset + 3):
                for col in range(colOffset, colOffset + 3):
                    tempSet = set(self.layout[row][col].note) - {0}
                    if self.layout[row][col].val == 0 and (tempSet <= combo or combo <= tempSet):
                        goodNodes.append((row, col))
            goodNodes.sort(key=lambda item: (item[1], -item[0]))
            return goodNodes
            
        def getAscPattern(self, boxRoot, combo):
            nodes = self.getNodes(boxRoot, combo)
            if len(nodes) < 3:
                return None
            possibleASCTriples = [{(0, 0), (2, 1), (1, 2)},
                                  {(1, 0), (0, 1), (2, 2)},
                                  {(0, 2), (1, 1), (2, 0)}]
            for triple in itertools.combinations(nodes, 3):
                normalized = {(r - boxRoot[0], c - boxRoot[1]) for r, c in triple}
                if normalized in possibleASCTriples:
                    return list(triple)
            return None
            
        def getDscPattern(self, boxRoot, combo):
            nodes = self.getNodes(boxRoot, combo)
            if len(nodes) < 3:
                return None
            possibleDSCTriples = [{(0, 0), (1, 1), (2, 2)},
                                  {(1, 0), (2, 1), (0, 2)},
                                  {(2, 0), (0, 1), (1, 2)}]
            for triple in itertools.combinations(nodes, 3):
                normalized = {(r - boxRoot[0], c - boxRoot[1]) for r, c in triple}
                if normalized in possibleDSCTriples:
                    return list(triple)
            return None
    
        def getFullBox(self, boxRoot):
            rBox, cBox = boxRoot
            boxes = [0, 3, 6]
            groups = []
            for r in boxes:
                for c in boxes:
                    if r <= rBox <= r + 3 and c <= cBox <= c + 3:
                        frameR = min(r+3, 6)
                        frameC = min(c+3, 6)
                        cornerBoxes = [(r, c), (r, frameC), (frameR, c), (frameR, frameC)]
                        if boxRoot in cornerBoxes:
                            cornerBoxes.remove(boxRoot)
                        groups.append(cornerBoxes)
            return groups
    # ********************************************************************************************************************
    def fireworkUtil(self):
        tempCopy = copy.deepcopy(self)
        remaining = self.getRemaining()
        for combo in itertools.combinations(remaining, 3):
            self.firework(set(combo), tempCopy)
            if not self.stuck(tempCopy):
                return
        comboPairs = list(itertools.combinations(remaining, 2))
        comboPairDoubles = list(itertools.permutations(comboPairs, 2))
        for combo1, combo2 in comboPairDoubles:
            if len(set(combo1) & set(combo2)) > 0:
                continue
            self.quadFirework(set(combo1), set(combo2), tempCopy)
            if not self.stuck(tempCopy):
                return
    def firework(self, combo, tempCopy):
        for i in range(9):
            for j in range(9):
                if self.layout[i][j].val != 0:
                    continue
                tempSet = set(self.layout[i][j].note) - {0}
                if not (combo <= tempSet):
                    continue
                rowOffset = (i//3) * 3
                colOffset = (j//3) * 3
                inCol = set()
                outCol = dict()
                inRow = set()
                outRow = dict()
                for col in range(9):
                    tempSet = set(self.layout[i][col].note) - {0}
                    if colOffset <= col < colOffset + 3:
                        if col == j:
                            continue
                        inCol = inCol.union(set(tempSet & combo))
                    else:
                        if len(tempSet & combo) > 0:
                            outCol[col] = set(tempSet & combo)
                            colWing = col
                if len(outCol) != 1 or outCol[colWing] | inCol != combo:
                    continue
                for row in range(9):
                    tempSet = set(self.layout[row][j].note) - {0}
                    if rowOffset <= row < rowOffset + 3:
                        if row == i:
                            continue
                        inRow = inRow.union(set(tempSet & combo))
                    else:
                        if len(tempSet & combo) > 0:
                            outRow[row] = set(tempSet & combo)
                            rowWing = row
                if len(outRow) != 1 or outRow[rowWing] | inRow != combo:
                    continue
                if len(outRow[rowWing]) < 3 and len(outCol[colWing]) < 3 and outRow[rowWing] == outCol[colWing]:
                    continue
                for eVal in range(1, 10):
                    if eVal not in combo:
                        self.layout[i][j].note[eVal-1] = 0
                        self.layout[rowWing][j].note[eVal-1] = 0
                        self.layout[i][colWing].note[eVal-1] = 0
                if not self.stuck(tempCopy):
                    print(f"Combo: {combo} Root: {(i, j)}")
                    print(f"colWing: {(i, colWing)}, inCol: {inCol}, outCol {outCol}")
                    print(f"rowWing: {(rowWing, j)}, inRow: {inRow}, outRow {outRow}")
                    if len(combo) == 3:
                        print("Triple Firework")
                    return
    
    def quadFirework(self, combo1, combo2, tempCopy):
        for i in range(9):
            for j in range(9):
                if self.layout[i][j].val != 0:
                    continue
                tempSet = set(self.layout[i][j].note) - {0}
                if not (combo1 <= tempSet):
                    continue
                rowOffset1 = (i//3) * 3
                colOffset1 = (j//3) * 3
                inCol1 = set()
                outCol1 = dict()
                inRow1 = set()
                outRow1 = dict()
                for col in range(9):
                    tempSet = set(self.layout[i][col].note) - {0}
                    if colOffset1 <= col < colOffset1 + 3:
                        if col == j:
                            continue
                        inCol1 = inCol1.union(set(tempSet & combo1))
                    else:
                        if len(tempSet & combo1) == 2:
                            outCol1[col] = set(tempSet & combo1)
                            colWing = col
                if len(outCol1) != 1:
                    continue
                for row in range(9):
                    tempSet = set(self.layout[row][j].note) - {0}
                    if rowOffset1 <= row < rowOffset1 + 3:
                        if row == i:
                            continue
                        inRow1 = inRow1.union(set(tempSet & combo1))
                    else:
                        if len(tempSet & combo1) == 2:
                            outRow1[row] = set(tempSet & combo1)
                            rowWing = row
                if len(outRow1) != 1:
                    continue
                # first double firework found, now checking for other double firework
                tempSet = set(self.layout[rowWing][colWing].note) - {0}
                if not (combo2 <= tempSet):
                    continue
                rowOffset2 = (rowWing//3) * 3
                colOffset2 = (colWing//3) * 3
                inCol2 = set()
                outCol2 = dict()
                inRow2 = set()
                outRow2 = dict()
                for col in range(9):
                    tempSet = set(self.layout[rowWing][col].note) - {0}
                    if colOffset2 <= col < colOffset2 + 3:
                        if col == colWing:
                            continue
                        inCol2 = inCol2.union(set(tempSet & combo2))
                    else:
                        if len(tempSet & combo2) > 0:
                            outCol2[col] = set(tempSet & combo2)
                            colWingCheck = col
                if len(outCol2) != 1:
                    continue
                for row in range(9):
                    tempSet = set(self.layout[row][colWing].note) - {0}
                    if rowOffset2 <= row < rowOffset2 + 3:
                        if row == rowWing:
                            continue
                        inRow2 = inRow2.union(set(tempSet & combo2))
                    else:
                        if len(tempSet & combo2) > 0:
                            outRow2[row] = set(tempSet & combo2)
                            rowWingCheck = row
                if len(outRow2) != 1:
                    continue
                if (i, colWing) != (rowWingCheck, colWing) or (rowWing, j) != (rowWing, colWingCheck):
                    continue
                print(f"Combo1: {combo1} Root: {(i, j)}")
                print(f"colWing: {(i, colWing)}, inCol: {inCol1}, outCol {outCol1}")
                print(f"rowWing: {(rowWing, j)}, inRow: {inRow1}, outRow {outRow1}")
                print(f"Combo2: {combo2} Root: {(rowWing, colWing)}")
                print(f"colWing: {(rowWing, colWingCheck)}, inCol: {inCol2}, outCol {outCol2}")
                print(f"rowWing: {(rowWingCheck, colWing)}, inRow: {inRow2}, outRow {outRow2}")
                safeSet = combo1 | combo2
                for eVal in range(1, 10):
                    if eVal not in safeSet:
                        self.layout[i][colWing].note[eVal-1] = 0
                        self.layout[rowWing][j].note[eVal-1] = 0
                    if eVal not in combo1:
                        self.layout[i][j].note[eVal-1] = 0
                    if eVal not in combo2:
                        self.layout[rowWing][colWing].note[eVal-1] = 0
                if not self.stuck(tempCopy):
                    return
                
    # ********************************************************************************************************************
    def twinXYChains(self):
        tempCopy = copy.deepcopy(self)
        for i in range(9):
            for j in range(9):
                if self.layout[i][j].val != 0:
                    continue
                startSet = set(self.layout[i][j].note) - {0}
                if len(startSet) != 3:
                    continue
                goodChain = self.getXYChainHoz((i, j))
                if len(goodChain) != 6:
                    goodChain = self.getXYChainVert((i, j))
                if len(goodChain) == 6:
                    rows = set()
                    cols = set()
                    for x, y in goodChain:
                        rows.add(x)
                        cols.add(y)
                    rowNodes = {row: set() for row in rows}
                    colNodes = {col: set() for col in cols}
                    for row in rowNodes:
                        for x, y in goodChain:
                            if row == x:
                                rowNodes[row].add((x, y))
                    for col in colNodes:
                        for x, y in goodChain:
                            if col == y:
                                colNodes[col].add((x, y))
                    for row, coords in rowNodes.items():
                        sets = [set(self.layout[r][c].note) - {0} for (r, c) in coords]
                        common = set()
                        if len(coords) == 2:
                            common |= sets[0] & sets[1]
                        if len(coords) == 3:
                            common |= (sets[0] & sets[1]) | (sets[1] & sets[2]) | (sets[0] & sets[2])
                        self.subUpdateNotes('row', list(coords), common)
                    for col, coords in colNodes.items():
                        sets = [set(self.layout[r][c].note) - {0} for (r, c) in coords]
                        common = set()
                        if len(coords) == 2:
                            common |= sets[0] & sets[1]
                        if len(coords) == 3:
                            common |= (sets[0] & sets[1]) | (sets[1] & sets[2]) | (sets[0] & sets[2])
                        self.subUpdateNotes('col', list(coords), common)
                    if not self.stuck(tempCopy):
                        print(f"XY Chain: {goodChain}")
                        return
    def getXYChainHoz(self, currentCoords):
        i, j = currentCoords
        tempSet = set(self.layout[i][j].note) - {0}
        for col1 in range(9):
            if col1 == j:
                continue
            tempSet1 = set(self.layout[i][col1].note) - {0}
            if len(tempSet | tempSet1) > 4 or len(tempSet1) not in (2,3):
                continue
            for col2 in range(9):
                if col2 in (j, col1):
                    continue
                tempSet2 = set(self.layout[i][col2].note) - {0}
                if len(tempSet | tempSet1 | tempSet2) > 5 or len(tempSet2) not in (2,3):
                    continue
                common = (tempSet & tempSet1) | (tempSet & tempSet2) | (tempSet1 & tempSet2)
                if len(common) < 2:
                    continue
                for row in range(9):
                    if row == i:
                        continue
                    tempSet3 = set(self.layout[row][j].note) - {0}
                    tempSet4 = set(self.layout[row][col1].note) - {0}
                    tempSet5 = set(self.layout[row][col2].note) - {0}
                    if len(tempSet3) != 2 or len(tempSet4) != 2 or len(tempSet5) != 2 or len(tempSet3 | tempSet4 | tempSet5) < 1:
                        continue
                    common = (tempSet3 & tempSet4) | (tempSet3 & tempSet5) | (tempSet4 & tempSet5)
                    if len(tempSet | tempSet1 | tempSet2 | tempSet3 | tempSet4 | tempSet5) != 6 or len(common) != 1:
                        continue
                    finalList = [currentCoords, (row, j), (i, col1), (row, col1), (i, col2), (row, col2)]
                    note_sets = [frozenset(set(self.layout[r][c].note) - {0}) for r, c in finalList]
                    if len(note_sets) == len(set(note_sets)):
                        return finalList
        return [currentCoords]
        
    def getXYChainVert(self, currentCoords):
        i, j = currentCoords
        tempSet = set(self.layout[i][j].note) - {0}
        for row1 in range(9):
            if row1 == i:
                continue
            tempSet1 = set(self.layout[row1][j].note) - {0}
            if len(tempSet | tempSet1) > 4 or len(tempSet1) not in (2,3):
                continue
            for row2 in range(9):
                if row2 in (i, row1):
                    continue
                tempSet2 = set(self.layout[row2][j].note) - {0}
                if len(tempSet | tempSet1 | tempSet2) > 5 or len(tempSet2) not in (2,3):
                    continue
                common = (tempSet & tempSet1) | (tempSet & tempSet2) | (tempSet1 & tempSet2)
                if len(common) < 2:
                    continue
                for col in range(9):
                    if col == j:
                        continue
                    tempSet3 = set(self.layout[i][col].note) - {0}
                    tempSet4 = set(self.layout[row1][col].note) - {0}
                    tempSet5 = set(self.layout[row2][col].note) - {0}
                    if len(tempSet3) != 2 or len(tempSet4) != 2 or len(tempSet5) != 2 or len(tempSet3 | tempSet4 | tempSet5) < 1:
                        continue
                    common = (tempSet3 & tempSet4) | (tempSet3 & tempSet5) | (tempSet4 & tempSet5)
                    if len(tempSet | tempSet1 | tempSet2 | tempSet3 | tempSet4 | tempSet5) != 6 or len(common) != 1:
                        continue
                    finalList = [currentCoords, (i, col), (row1, j), (row1, col), (row2, j), (row2, col)]
                    note_sets = [frozenset(set(self.layout[r][c].note) - {0}) for r, c in finalList]
                    if len(note_sets) == len(set(note_sets)):
                        return finalList
        return [currentCoords]
    # ********************************************************************************************************************
    def SKLoops(self):
        tempCopy = copy.deepcopy(self)
        for tl, tr, bl, br in self.getDiagonalSymSquares():
            coordSet = {tl, tr, bl, br}
            if any(self.layout[r][c].val == 0 for (r,c) in coordSet):
                continue
            hozVals = {(x, y): set() for (x,y) in coordSet}
            verVals = {(x, y): set() for (x,y) in coordSet}
            sHozCellVals = {(x,y): set() for (x,y) in coordSet}
            sVerCellVals = {(x,y): set() for (x,y) in coordSet}
            for x, y in coordSet:
                rowOffset = (x//3) * 3
                colOffset = (y//3) * 3
                checkCol = set()
                checkRow = set()
                filledCount = 0
                for col in range(colOffset, colOffset + 3):
                    if col == y: 
                        continue
                    tempSet = set(self.layout[x][col].note) - {0}
                    hozVals[(x, y)] |= tempSet
                    checkCol.add((x, col))
                    if len(tempSet) == 0:
                        filledCount += 1
                for row in range(rowOffset, rowOffset + 3):
                    if row == x:
                        continue
                    tempSet = set(self.layout[row][y].note) - {0}
                    verVals[(x, y)] |= tempSet
                    checkRow.add((row, y))
                    if len(tempSet) == 0:
                        filledCount += 1
                if filledCount < 2:
                    for val in hozVals[(x, y)]:
                        if all(val in (set(self.layout[a][b].note) - {0}) for a, b in checkCol) or not all(self.layout[a][b].val == 0 for a, b in coordSet):
                            sHozCellVals[(x, y)].add(val)
                    for val in verVals[(x, y)]:
                        if all(val in (set(self.layout[a][b].note) - {0}) for a, b in checkRow) or not all(self.layout[a][b].val == 0 for a, b in coordSet):
                            sVerCellVals[(x, y)].add(val)
                else:
                    break
            if filledCount > 1:
                continue
            # for node in coordSet:
            #     print(f"{node}:\n HozVals {hozVals[node]}. SHozVals {sHozCellVals[node]}.\nVerVals {verVals[node]} \n")
            linkCount = 0
            totalCount1 = 0 # blue
            totalCount2 = 0 # green
            boxStrongVals = {(a, b): set() for a, b in coordSet}
            sHozPairVals = {((a, b), (x, y)): set(sHozCellVals[(a, b)] & sHozCellVals[(x, y)]) for (a, b), (x, y) in itertools.combinations(coordSet, 2) if a == x}
            sVerPairVals = {((a, b), (x, y)): set(sVerCellVals[(a, b)] & sVerCellVals[(x, y)]) for (a, b), (x, y) in itertools.combinations(coordSet, 2) if b == y}
            flip = True
            for ((a, b), (x, y)), vals in sHozPairVals.items():
                if len(vals) > 0:
                    linkCount += 1
                if flip:
                    flip = False
                    totalCount1 += len(hozVals[x, y])
                    totalCount2 += len(hozVals[a, b])
                else:
                    flip = True
                    totalCount1 += len(hozVals[a, b])
                    totalCount2 += len(hozVals[x, y])
            for ((a, b), (x, y)), vals in sVerPairVals.items():
                if len(vals) > 0:
                    linkCount += 1
                if flip:
                    flip = False
                    totalCount1 += len(verVals[a, b])
                    totalCount2 += len(verVals[x, y])
                else:
                    flip = True
                    totalCount1 += len(verVals[x, y])
                    totalCount2 += len(verVals[a, b])
            for x in coordSet:
                if len(hozVals[x] & verVals[x]) > 1:
                    linkCount += 1
            # print(f"LinkCount: {linkCount}")
            # print(f"totalCount1: {totalCount1}")
            # print(f"totalCount2: {totalCount2}")
            if linkCount != 8 or totalCount1 > 16 or totalCount2 > 16:
                # print("Bad counts")
                continue
            # print(f"good cycle {coordSet}")
            # erasing time!
            for (a, b) in coordSet:
                eVals = hozVals[(a, b)] | verVals[(a, b)]
                for (x, y) in coordSet:
                    if ((a, b), (x, y)) in sHozPairVals:
                        eVals -= sHozPairVals[((a, b), (x, y))]
                    if ((x, y), (a, b)) in sHozPairVals:
                        eVals -= sHozPairVals[((x, y), (a, b))]
                    if ((a, b), (x, y)) in sVerPairVals:
                        eVals -= sVerPairVals[((a, b), (x, y))]
                    if ((x, y), (a, b)) in sVerPairVals:
                        eVals -= sVerPairVals[((x, y), (a, b))]
                rowOffset = (a//3) * 3
                colOffset = (b//3) * 3
                ignore = set()
                for row in range(rowOffset, rowOffset + 3):
                    ignore.add((row, b))
                for col in range(colOffset, colOffset + 3):
                    ignore.add((a, col))
                self.subUpdateNotes('box', list(ignore), eVals)
                # print(f"Node: {(a, b)}\nIgnore Nodes: {ignore}\nErasing {eVals}\n")
            for (a, b), (x, y) in sHozPairVals:
                if a != x:
                    continue
                ignore = set()
                colOffset1 = (b//3) * 3
                colOffset2 = (y//3) * 3
                for col in range(9):
                    if colOffset1 <= col < colOffset1 + 3 or colOffset2 <= col < colOffset2 + 3:
                        ignore.add((a, col))
                eVals = set(hozVals[(a, b)] & hozVals[(x, y)])
                self.subUpdateNotes('row', list(ignore), sHozPairVals[((a, b), (x, y))])
                # print(f"Nodes: {(a, b), (x, y)}\nIgnore Nodes: {ignore}\nErasing {eVals}\n")
            for (a, b), (x, y) in sVerPairVals:
                if b != y:
                    continue
                ignore = set()
                rowOffset1 = (a//3) * 3
                rowOffset2 = (x//3) * 3
                for row in range(9):
                    if rowOffset1 <= row < rowOffset1 + 3 or rowOffset2 <= row < rowOffset2 + 3:
                        ignore.add((row, b))
                self.subUpdateNotes('col', list(ignore), sVerPairVals[((a, b), (x, y))])
                # print(f"Nodes: {(a, b), (x, y)}\nIgnore Nodes: {ignore}\nErasing {eVals}\n")
            if not self.stuck(tempCopy):
                print(f"Found SK loop {coordSet}")
                return
                
    def getDiagonalSymSquares(self):
        squares = []
        fourCorners = {(0, 0), (0, 2), (2, 0), (2, 2)}
        for r1 in range(9):
            for r2 in range(r1 + 1, 9):
                for c1 in range(9):
                    for c2 in range(c1 + 1, 9):
                        TL = (r1, c1)
                        TR = (r1, c2)
                        BL = (r2, c1)
                        BR = (r2, c2)
                        if (self.layout[r1][c1].val == 0 or
                            self.layout[r1][c2].val == 0 or
                            self.layout[r2][c1].val == 0 or
                            self.layout[r2][c2].val == 0):
                            continue
                        boxes = {
                            (r1 // 3, c1 // 3),
                            (r1 // 3, c2 // 3),
                            (r2 // 3, c1 // 3),
                            (r2 // 3, c2 // 3)
                        }
                        if len(boxes) != 4:
                            continue
                        rel_pos = [
                            (r1 % 3) * 3 + (c1 % 3),
                            (r1 % 3) * 3 + (c2 % 3),
                            (r2 % 3) * 3 + (c1 % 3),
                            (r2 % 3) * 3 + (c2 % 3)
                        ]
                        if len(set(rel_pos)) == 1:
                            squares.append([TL, TR, BL, BR])
                            continue
                        normalized = {(r - ((r//3) * 3), c - ((c//3) * 3)) for r, c in [TL, TR, BL, BR]}
                        if len(normalized & fourCorners) == 4:
                            squares.append([TL, TR, BL, BR])
                            continue
        return squares
    # ********************************************************************************************************************
    def extUniqueRectanglesUtil(self):
        tempCopy = copy.deepcopy(self)
        remaining = self.getRemaining()
        for combo in itertools.combinations(self.getRemaining(), 3):
            self.extUniqueRectangles(set(combo), tempCopy)
            if not self.stuck(tempCopy):
                return
    def extUniqueRectangles(self, combo, tempCopy):
        rowSets = set()
        colSets = set()
        for row in range(9):
            matchingCols = [c for c in range(9) if set(self.layout[row][c].note) - {0} == combo or len((set(self.layout[row][c].note) - {0}) & combo) == 2]
            for c1, c2 in itertools.combinations(matchingCols, 2):
                tempSet1 = set(self.layout[row][c1].note) - {0}
                tempSet2 = set(self.layout[row][c2].note) - {0}
                if len(tempSet1 | tempSet2) > 0 and tempSet1 == tempSet2 and self.inBox([(row, c1), (row, c2)]):
                    pair = frozenset(((row, c1), (row, c2)))
                    rowSets.add(pair)
        for col in range(9):
            matchingRows = [r for r in range(9) if set(self.layout[r][col].note) - {0} == combo or len((set(self.layout[r][col].note) - {0}) & combo) == 2]
            for r1, r2 in itertools.combinations(matchingRows, 2):
                tempSet1 = set(self.layout[r1][col].note) - {0}
                tempSet2 = set(self.layout[r2][col].note) - {0}
                if len(tempSet1 | tempSet2) > 0 and tempSet1 == tempSet2 and self.inBox([(r1, col), (r2, col)]):
                    pair = frozenset(((r1, col), (r2, col)))
                    colSets.add(pair)
                    
        for ((a, b), (x, y)) in rowSets:
            # print(f"{combo}: {((a, b), (x, y))}")
            tempSet1 = set(self.layout[a][b].note) - {0}
            tempSet2 = set(self.layout[x][y].note) - {0}
            rowOffset1 = (a//3) * 3 
            for row2 in range(9):
                if rowOffset1 <= row2 < rowOffset1 + 3:
                    continue
                tempSet3 = set(self.layout[row2][b].note) - {0}
                tempSet4 = set(self.layout[row2][y].note) - {0}
                if len(tempSet3 & tempSet4 & combo) < 2:
                    continue
                rowOffset2 = (row2//3) * 3 
                for row3 in range(9):
                    if rowOffset1 <= row3 < rowOffset1 + 3 or rowOffset2 <= row3 < rowOffset2 + 3:
                        continue
                    tempSet5 = set(self.layout[row3][b].note) - {0}
                    tempSet6 = set(self.layout[row3][y].note) - {0}
                    if len(tempSet5 & tempSet6 & combo) < 2:
                        continue
                    if combo <= (tempSet1 & tempSet2) | (tempSet3 & tempSet4) | (tempSet5 & tempSet6):
                        goodGroup = [(a, b), (x, y), (row2, b), (row2, y), (row3, b), (row3, y)]
                        getAlters = {(c, d): set(self.layout[c][d].note) - {0} - combo for c, d in goodGroup}
                        eCells = []
                        for (c, d), vals in getAlters.items():
                            if len(vals) > 0:
                                eCells.append((c, d))
                        if len(eCells) == 1:
                            ex1, ey1 = eCells[0]
                            for val in combo:
                                self.layout[ex1][ey1].note[val-1] = 0
                            if not self.stuck(tempCopy):
                                print(goodGroup)
                                print(f"Extended Rectangles Row Type 1 removed {combo} from {(ex1, ey1)}")
                                return
                            
        for ((a, b), (x, y)) in colSets:
            # print(f"{combo}: {((a, b), (x, y))}")
            tempSet1 = set(self.layout[a][b].note) - {0}
            tempSet2 = set(self.layout[x][y].note) - {0}
            colOffset1 = (b//3) * 3
            for col2 in range(9):
                if colOffset1 <= col2 < colOffset1 + 3:
                    continue
                tempSet3 = set(self.layout[a][col2].note) - {0}
                tempSet4 = set(self.layout[x][col2].note) - {0}
                if len(tempSet3 & tempSet4 & combo) < 2:
                    continue
                colOffset2 = (col2//3) * 3 
                for col3 in range(9):
                    if colOffset1 <= col3 < colOffset1 + 3 or colOffset2 <= col3 < colOffset2 + 3:
                        continue
                    tempSet5 = set(self.layout[a][col3].note) - {0}
                    tempSet6 = set(self.layout[x][col3].note) - {0}
                    if len(tempSet5 & tempSet6 & combo) < 2:
                        continue
                    if combo <= (tempSet1 & tempSet2) | (tempSet3 & tempSet4) | (tempSet5 & tempSet6):
                        goodGroup = [(a, b), (x, y), (a, col2), (x, col2), (a, col3), (x, col3)]
                        getAlters = {(c, d): set(self.layout[c][d].note) - {0} - combo for c, d in goodGroup}
                        eCells = []
                        for (c, d), vals in getAlters.items():
                            if len(vals) > 0:
                                eCells.append((c, d))
                        if len(eCells) == 1:
                            ex1, ey1 = eCells[0]
                            for val in combo:
                                self.layout[ex1][ey1].note[val-1] = 0
                            if not self.stuck(tempCopy):
                                print(goodGroup)
                                print(f"Extended Rectangles Row Type 1 removed {combo} from {(ex1, ey1)}")
                                return

        for ((a, b), (x, y)) in rowSets:
            # print(f"{combo}: {((a, b), (x, y))}")
            tempSet1 = set(self.layout[a][b].note) - {0}
            tempSet2 = set(self.layout[x][y].note) - {0}
            if len(tempSet1 & tempSet2 & combo) != 3 or tempSet1 != tempSet2 or len(tempSet1) != 3:
                continue
            rowOffset1 = (a//3) * 3 
            for row2 in range(9):
                if rowOffset1 <= row2 < rowOffset1 + 3:
                    continue
                tempSet3 = set(self.layout[row2][b].note) - {0}
                tempSet4 = set(self.layout[row2][y].note) - {0}
                if len(tempSet3 & tempSet4 & combo) < 2 or not (combo <= tempSet1 | tempSet2 | tempSet3 | tempSet4):
                    continue
                rowOffset2 = (row2//3) * 3
                for row3 in range(9):
                    if rowOffset1 <= row3 < rowOffset1 + 3 or rowOffset2 <= row3 < rowOffset2 + 3:
                        continue
                    tempSet5 = set(self.layout[row3][b].note) - {0}
                    tempSet6 = set(self.layout[row3][y].note) - {0}
                    if tempSet5 != tempSet6 or len(tempSet5 & tempSet6) != 4 or not (combo <= tempSet5 | tempSet6):
                        continue
                    eVal = (tempSet5 - combo).pop()
                    ignoreCells = [(row3, b), (row3, y)]
                    self.subUpdateNotes('box', ignoreCells, {eVal})
                    self.subUpdateNotes('row', ignoreCells, {eVal})
                    if not self.stuck(tempCopy):
                        goodGroup = [(a, b), (x, y), (row2, b), (row2, y), (row3, b), (row3, y)]
                        print(goodGroup)
                        print(f"Extended Rectangles Row Type 2 removed {eVal} from box and row with {ignoreCells}")
                        return
                        
        for ((a, b), (x, y)) in colSets:
            # print(f"{combo}: {((a, b), (x, y))}")
            tempSet1 = set(self.layout[a][b].note) - {0}
            tempSet2 = set(self.layout[x][y].note) - {0}
            if len(tempSet1 & tempSet2 & combo) != 3 or tempSet1 != tempSet2 or len(tempSet1) != 3:
                continue
            colOffset1 = (b//3) * 3 
            for col2 in range(9):
                if colOffset1 <= col2 < colOffset1 + 3:
                    continue
                tempSet3 = set(self.layout[a][col2].note) - {0}
                tempSet4 = set(self.layout[x][col2].note) - {0}
                if len(tempSet3 & tempSet4 & combo) < 2 or not (combo <= tempSet1 | tempSet2 | tempSet3 | tempSet4):
                    continue
                colOffset2 = (col2//3) * 3
                for col3 in range(9):
                    if colOffset1 <= col3 < colOffset1 + 3 or colOffset2 <= col3 < colOffset2 + 3:
                        continue
                    tempSet5 = set(self.layout[a][col3].note) - {0}
                    tempSet6 = set(self.layout[x][col3].note) - {0}
                    if tempSet5 != tempSet6 or len(tempSet5 & tempSet6) != 4 or not (combo <= tempSet5 | tempSet6):
                        continue
                    eVal = (tempSet5 - combo).pop()
                    ignoreCells = [(a, col3), (x, col3)]
                    self.subUpdateNotes('box', ignoreCells, {eVal})
                    self.subUpdateNotes('row', ignoreCells, {eVal})
                    if not self.stuck(tempCopy):
                        goodGroup = [(a, b), (x, y), (a, col2), (x, col2), (a, col3), (x, col3)]
                        print(goodGroup)
                        print(f"Extended Rectangles Col Type 2 removed {eVal} from box and col with {ignoreCells}")
                        return

        for ((a, b), (x, y)) in rowSets:
            # print(f"{combo}: {((a, b), (x, y))}")
            tempSet1 = set(self.layout[a][b].note) - {0}
            tempSet2 = set(self.layout[x][y].note) - {0}
            if len(tempSet1 & tempSet2 & combo) != 2 or tempSet1 != tempSet2 or len(tempSet1) != 2:
                continue
            rowOffset1 = (a//3) * 3 
            for row2 in range(9):
                if rowOffset1 <= row2 < rowOffset1 + 3:
                    continue
                tempSet3 = set(self.layout[row2][b].note) - {0}
                tempSet4 = set(self.layout[row2][y].note) - {0}
                if len(tempSet3 & tempSet4 & combo) != 2 or tempSet3 != tempSet4 or len(tempSet3) != 2 or not (combo <= tempSet1 | tempSet2 | tempSet3 | tempSet4):
                    continue
                goalSet = combo - (tempSet1 & tempSet3)
                rowOffset2 = (row2//3) * 3
                for row3 in range(9):
                    if rowOffset1 <= row3 < rowOffset1 + 3 or rowOffset2 <= row3 < rowOffset2 + 3:
                        continue
                    tempSet5 = set(self.layout[row3][b].note) - {0}
                    tempSet6 = set(self.layout[row3][y].note) - {0}
                    if not (goalSet <= tempSet5) or not (goalSet <= tempSet6):
                        continue
                    eVal = 0
                    for val in goalSet:
                        if self.singleColCheck([(a, b), (row2, b), (row3, b)], {val}) and self.singleColCheck([(x, y), (row2, y), (row3, y)], {val}):
                            continue
                        eVal = val
                    if eVal == 0:
                        continue
                    self.layout[row3][b].note[eVal-1] = 0
                    self.layout[row3][x].note[eVal-1] = 0
                    if not self.stuck(tempCopy):
                        goodGroup = [(a, b), (x, y), (row2, b), (row2, y), (row3, b), (row3, y)]
                        print(goodGroup)
                        print(f"Extended Rectangles Row Type 4 removed {eVal} from box and row with {(row3, b), (row3, y)}")
                        return
                        
        for ((a, b), (x, y)) in colSets:
            # print(f"{combo}: {((a, b), (x, y))}")
            tempSet1 = set(self.layout[a][b].note) - {0}
            tempSet2 = set(self.layout[x][y].note) - {0}
            if len(tempSet1 & tempSet2 & combo) != 2 or tempSet1 != tempSet2 or len(tempSet1) != 2:
                continue
            colOffset1 = (b//3) * 3 
            for col2 in range(9):
                if colOffset1 <= col2 < colOffset1 + 3:
                    continue
                tempSet3 = set(self.layout[a][col2].note) - {0}
                tempSet4 = set(self.layout[x][col2].note) - {0}
                if len(tempSet3 & tempSet4 & combo) != 2 or tempSet3 != tempSet4 or len(tempSet3) != 2 or not (combo <= tempSet1 | tempSet2 | tempSet3 | tempSet4):
                    continue
                goalSet = combo - (tempSet1 & tempSet3)
                colOffset2 = (col2//3) * 3
                for col3 in range(9):
                    if colOffset1 <= col3 < colOffset1 + 3 or colOffset2 <= col3 < colOffset2 + 3:
                        continue
                    tempSet5 = set(self.layout[a][col3].note) - {0}
                    tempSet6 = set(self.layout[x][col3].note) - {0}
                    if not (goalSet <= tempSet5) or not (goalSet <= tempSet6):
                        continue
                    eVal = 0
                    for val in goalSet:
                        if self.singleRowCheck([(a, b), (a, col2), (a, col3)], {val}) and self.singleRowCheck([(x, y), (x, col2), (x, col3)], {val}):
                            continue
                        eVal = val
                    if eVal == 0:
                        continue
                    self.layout[a][col3].note[eVal-1] = 0
                    self.layout[x][col3].note[eVal-1] = 0
                    if not self.stuck(tempCopy):
                        goodGroup = [(a, b), (x, y), (a, col2), (x, col2), (a, col3), (x, col3)]
                        print(goodGroup)
                        print(f"Extended Rectangles Col Type 4 removed {eVal} from box and row with {(a, col3), (x, col3)}")
                        return
    # ********************************************************************************************************************
    def hiddenUniqueRectanglesUtil(self):
        tempCopy = copy.deepcopy(self)
        remaining = self.getRemaining()
        for combo in itertools.combinations(remaining, 2):
            self.hiddenUniqueRectangles(set(combo), tempCopy)
            if not self.stuck(tempCopy):
                return
    def hiddenUniqueRectangles(self, combo, tempCopy):
        rowSets = set()
        colSets = set()
        for row in range(9):
            matchingCols = [c for c in range(9) if combo <= set(self.layout[row][c].note) - {0}]
            for c1, c2 in itertools.combinations(matchingCols, 2):
                pair = frozenset(((row, c1), (row, c2)))
                rowSets.add(pair)
        for col in range(9):
            matchingRows = [r for r in range(9) if combo <= set(self.layout[r][col].note) - {0}]
            for r1, r2 in itertools.combinations(matchingRows, 2):
                pair = frozenset(((r1, col), (r2, col)))
                colSets.add(pair)
        # type 1 Row
        for ((a, b), (c, d)) in rowSets:
            tempSet1 = set(self.layout[a][b].note) - {0}
            tempSet2 = set(self.layout[c][d].note) - {0}
            if not(len(tempSet1) != 2 ^ len(tempSet2) != 2) or not self.inBox([(a, b), (c, d)]) or len(tempSet1) == 0 or len(tempSet2) == 0:
                continue
            rowOffset = (a//3) * 3
            for row in range(9):
                if rowOffset <= row < rowOffset + 3 or frozenset(((row, b), (row, d))) not in rowSets:
                    continue
                vals = []
                if len(tempSet1) == 2:
                    for val in tempSet1:
                        if self.singleRowCheck([(row, d), (row, b)], {val}) and self.singleColCheck([(row, d), (c, d)], {val}):
                            vals.append(val)
                    if len(vals) == 1:
                        eVal = (combo - set(vals)).pop()
                        self.layout[row][d].note[eVal-1] = 0
                elif len(tempSet2) == 2:
                    for val in tempSet2:
                        if self.singleRowCheck([(row, b), (row, d)], {val}) and self.singleColCheck([(row, b), (a, b)], {val}):
                            vals.append(val)
                    if len(vals) == 1:
                        eVal = (combo - set(vals)).pop()
                        self.layout[row][b].note[eVal-1] = 0
                if not self.stuck(tempCopy):
                    print(f"Hidden Unique Rectangles Row Type 1 removed {eVal} at either {(row, b)} or {(row, d)}")
                    return
        # type 1 Col
        for ((a, b), (c, d)) in colSets:
            tempSet1 = set(self.layout[a][b].note) - {0}
            tempSet2 = set(self.layout[c][d].note) - {0}
            if not(len(tempSet1) != 2 ^ len(tempSet2) != 2) or not self.inBox([(a, b), (c, d)]) or len(tempSet1) == 0 or len(tempSet2) == 0:
                continue
            colOffset = (b//3) * 3
            for col in range(9):
                if colOffset <= col < colOffset + 3 or frozenset(((a, col), (c, col))) not in rowSets:
                    continue
                vals = []
                if len(tempSet1) == 2:
                    for val in tempSet1:
                        if self.singleColCheck([(c, col), (a, col)], {val}) and self.singleRowCheck([(c, col), (c, d)], {val}):
                            vals.append(val)
                    if len(vals) == 1:
                        eVal = (combo - set(vals)).pop()
                        self.layout[c][col].note[eVal-1] = 0
                elif len(tempSet2) == 2:
                    for val in tempSet2:
                        if self.singleColCheck([(a, col), (c, col)], {val}) and self.singleRowCheck([(a, col), (a, b)], {val}):
                            vals.append(val)
                    if len(vals) == 1:
                        eVal = (combo - set(vals)).pop()
                        self.layout[a][col].note[eVal-1] = 0
                if not self.stuck(tempCopy):
                    print(f"Hidden Unique Rectangles Col Type 1 removed {eVal} at either {(a, col)} or {(c, col)}")
                    return
        # Type 2a Row
        for ((a, b), (c, d)) in rowSets:
            tempSet1 = set(self.layout[a][b].note) - {0}
            tempSet2 = set(self.layout[c][d].note) - {0}
            if not (len(tempSet1) == 2 and len(tempSet2) == 2) or tempSet1 != tempSet2 or not self.inBox([(a, b), (c, d)]):
                continue
            rowOffset = (a//3) * 3
            for row in range(9):
                if rowOffset <= row < rowOffset + 3 or frozenset(((row, b), (row, d))) not in rowSets:
                    continue
                for val in tempSet1:
                    eVal = (combo - {val}).pop()
                    if self.singleColCheck([(a, b), (row, b)], {val}):
                        self.layout[row][d].note[eVal-1] = 0
                    if self.singleColCheck([(c, d), (row, d)], {val}):
                        self.layout[row][b].note[eVal-1] = 0
                if not self.stuck(tempCopy):
                    print(f"Hidden Unique Rectangles Row Type 2a removed some of {combo} from either {(row, b)} or {(row, d)}")
                    return
        # Type 2a Col
        for ((a, b), (c, d)) in colSets:
            tempSet1 = set(self.layout[a][b].note) - {0}
            tempSet2 = set(self.layout[c][d].note) - {0}
            if not (len(tempSet1) == 2 and len(tempSet2) == 2) or tempSet1 != tempSet2  or not self.inBox([(a, b), (c, d)]):
                continue
            colOffset = (b//3) * 3
            for col in range(9):
                if colOffset <= col < colOffset + 3 or frozenset(((a, col), (c, col))) not in colSets:
                    continue
                for val in tempSet1:
                    eVal = (combo - {val}).pop()
                    if self.singleRowCheck([(a, b), (a, col)], {val}):
                        self.layout[c][col].note[eVal-1] = 0
                    if self.singleRowCheck([(c, d), (c, col)], {val}):
                        self.layout[a][col].note[eVal-1] = 0
                if not self.stuck(tempCopy):
                    print(f"Hidden Unique Rectangles Col Type 2a removed some of {combo} from either {(a, col)} or {(c, col)}")
                    return
        # Type 2b Row
        for ((a, b), (c, d)) in rowSets:
            tempSet1 = set(self.layout[a][b].note) - {0}
            tempSet2 = set(self.layout[c][d].note) - {0}
            if not (len(tempSet1) == 2 and len(tempSet2) == 2) or tempSet1 != tempSet2 or self.inBox([(a, b), (c, d)]):
                continue
            rowOffset = (a//3) * 3
            for row in range(rowOffset, rowOffset + 3):
                if row == a or frozenset(((row, b), (row, d))) not in rowSets:
                    continue
                print(f"BasePair: {(a, b), (c, d)}. Comparing to: {(row, b), (row, d)}")
                for val in tempSet1:
                    eVal = (combo - {val}).pop()
                    if self.singleColCheck([(a, b), (row, b)], {val}) and self.singleBoxCheck([(a, b), (row, b)], {val}):
                        self.layout[row][d].note[eVal-1] = 0
                    if self.singleColCheck([(c, d), (row, d)], {val}) and self.singleBoxCheck([(c, d), (row, d)], {val}):
                        self.layout[row][b].note[eVal-1] = 0
                if not self.stuck(tempCopy):
                    print(f"Hidden Unique Rectangles Row Type 2b removed some of {combo} from either {(row, b)} or {(row, d)}")
                    return
        # Type 2b Col
        for ((a, b), (c, d)) in colSets:
            tempSet1 = set(self.layout[a][b].note) - {0}
            tempSet2 = set(self.layout[c][d].note) - {0}
            if not (len(tempSet1) == 2 and len(tempSet2) == 2) or tempSet1 != tempSet2  or self.inBox([(a, b), (c, d)]):
                continue
            colOffset = (b//3) * 3
            for col in range(colOffset, colOffset + 3):
                if b == col or frozenset(((a, col), (c, col))) not in colSets:
                    continue
                for val in tempSet1:
                    eVal = (combo - {val}).pop()
                    if self.singleRowCheck([(a, b), (a, col)], {val}) and self.singleBoxCheck([(a, b), (a, col)], {val}):
                        self.layout[c][col].note[eVal-1] = 0
                    if self.singleRowCheck([(c, d), (c, col)], {val}) and self.singleBoxCheck([(c, d), (c, col)], {val}):
                        self.layout[a][col].note[eVal-1] = 0
                if not self.stuck(tempCopy):
                    print(f"Hidden Unique Rectangles Col Type 2b removed some of {combo} from either {(a, col)} or {(c, col)}")
                    return
    # ********************************************************************************************************************
    # def wxyzWing(self):
    #     for i in range(9):
    #         for j in range(9):
    #             if self.layout[i][j].val != 0:
    #                 continue
    #             tempSet = set(self.layout[i][j].note) - {0}
    #             if len(tempSet) not in (3, 4):
    #                 continue
                    
    #             rowOffset = (i//3) * 3
    #             colOffset = (j//3) * 3

    #             # these declarations and the following loops are meant for finding potential rowWings, boxWings, and colWings for (i, j)
    #             pBoxWing = {val: set() for val in tempSet}
    #             pRowWing = {val: set() for val in tempSet}
    #             pColWing = {val: set() for val in tempSet}
    #             for val in tempSet:
    #                 for row in range(rowOffset, rowOffset + 3):
    #                     for col in range(colOffset, colOffset + 3):
    #                         if (row, col) == (i, j):
    #                             continue
    #                         babySet = set(self.layout[row][col].note) - {0}
    #                         if val in babySet and len(babySet) < 4:
    #                             pBoxWing[val].add((row, col))
    #             for val in tempSet:
    #                 for col in range(9):
    #                     if colOffset <= col < colOffset + 3:
    #                         continue
    #                     babySet = set(self.layout[i][col].note) - {0}
    #                     if val in babySet and len(babySet) < 4:
    #                         pRowWing[val].add((i, col))
    #             for val in tempSet:
    #                 for row in range(9):
    #                     if rowOffset <= row < rowOffset + 3:
    #                         continue
    #                     babySet = set(self.layout[row][j].note) - {0}
    #                     if val in babySet and len(babySet) < 4:
    #                         pRowWing[val].add((row, j))
    #             # for rowWings
    #             for eVal, potential in pBoxWing.items():
                    
                
                
                

    # ********************************************************************************************************************

























