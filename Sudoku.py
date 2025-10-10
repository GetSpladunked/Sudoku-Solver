from itertools import combinations
import copy

def solve(Puzzle):
    iterations = 0
    Puzzle.displayAll()
    while not Puzzle.solved():
        print(f"Iteration: {iterations}")
        temp = copy.deepcopy(Puzzle)
        Puzzle.cleanup()
        Puzzle.checkBoxLock()
        Puzzle.checkRowLock()
        Puzzle.checkColLock()
        Puzzle.finalizeLocks()
        Puzzle.resetLocks(temp)
        iterations += 1
        if Puzzle.stuck(temp):
            print("Using some strategies")
            Puzzle = strategies(Puzzle)
            if Puzzle.stuck(temp):
                break
                # temp = Puzzle.puzzleRegeneration()
                # if not Puzzle.stuck(temp):
                #     Puzzle = temp
                # else:
                #     break
            else:
                Puzzle.displayAll()
        # else:
        #     Puzzle.displayAll()
    if Puzzle.solved():
        print("Puzzle solved!")
        Puzzle.displayAll()
    else:
        print("Puzzle got stuck :(")
        Puzzle.displayAll()

# MIGHT BE BEST TO PUT HARDER STRATEGIES FIRST BECUASE THE SIMPLE ONES CAN RUIN THE BIG ONES
def strategies(Puzzle):
    temp = copy.deepcopy(Puzzle)
    Puzzle.xWing()
    if not Puzzle.stuck(temp):
        print("X-Wing Worked")
        return Puzzle
    Puzzle.chuteRemotePairs()
    if not Puzzle.stuck(temp):
        print("Chute Remote Pairs Worked")
        return Puzzle
    Puzzle.simpleColoringUtil()
    if not Puzzle.stuck(temp):
        print("Simple Coloring Worked")
        return Puzzle
    Puzzle.yWing()
    if not Puzzle.stuck(temp):
        print("Y-Wing Worked")
        return Puzzle
    Puzzle.rectangleElimination()
    if not Puzzle.stuck(temp):
        print("Rectangle Elimination Worked")
        return Puzzle
    Puzzle.swordfishUtil()
    if not Puzzle.stuck(temp):
        print("Swordfish Worked")
        return Puzzle
    Puzzle.xyzWing()
    if not Puzzle.stuck(temp):
        print("xyz-Wing Worked")
        return Puzzle
    Puzzle.xCyclesUtil()
    if not Puzzle.stuck(temp):
        print("X-Cycles Worked")
        return Puzzle
    Puzzle.medusa3DUtil()
    if not Puzzle.stuck(temp):
        print("3D-Medusa Worked")
        return Puzzle
    Puzzle.jellyFishUtil()
    if not Puzzle.stuck(temp):
        print("JellyFish Worked")
        return Puzzle
    # Puzzle.skyscraperUtil()
    # if not Puzzle.stuck(temp):
    #     print("Skyscraper Worked")
    #     return Puzzle
    # Puzzle.twoStringKiteUtil()
    # if not Puzzle.stuck(temp):
    #     print("2-String Kite Worked")
    #     return Puzzle
    print("Nothing Worked")
    return Puzzle
# working Strategies:
# Puzzle.xWing()
# Puzzle.chuteRemotePairsRows()
# Puzzle.chuteRemotePairsCols()
# Puzzle.simpleColoringUtil()
# Puzzle.yWing()
# Puzzle.rectangleElimination()
# Puzzle.swordfish()**



# diabolical strategies
# xCycles
# 3D Medusa
# jellyfish
# unique rectangles
# fireworks
# twinned xy chains
# SK loops
# extended rectangles 
# hidden URs
# WXYZ wing
# XY Chains
# aligned pair exclusion

# Extreme Strategies
# Exocet
# grouped x cycles
# finned xwing
# finned swordfish
# inference chians
# aic groups, ALSs, URs
# Sue-De-Coq
# digit forcing chains
# nishio forcing chains
# cell forcing chains
# unit forcing chains
# almost locked sets
# double exocet
# death blossom
# pattern overlay

# deprecated strategies
# remote pairs
# y wing chain
# multivalue xwing
# guardians

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
        def setVal(self,hardVal):
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
        self.layout = [[0 for _ in range(9)] for _ in range(9)]
        self.locked = [[False for _ in range(9)] for _ in range(9)]
        self.softboxlocked = [[False for _ in range(9)] for _ in range(9)]
        self.softlinelockedx = [[False for _ in range(9)] for _ in range(9)]
        self.softlinelockedy = [[False for _ in range(9)] for _ in range(9)]
        for i in range(9):
            for j in range(9):
                self.layout[i][j] = self.Node(initLayout[i][j], self)
                if self.layout[i][j].val != 0:
                    self.locked[i][j] = self.softboxlocked[i][j] = self.softlinelockedx[i][j] = self.softlinelockedy[i][j] = True
        self.updateNotes()

    def puzzleRegeneration(self):
        x = [[0 for _ in range(9)] for _ in range(9)]
        for i in range(9):
            for j in range(9):
                x[i][j] = self.layout[i][j].val
        return Puzzle(x)
    
    # simple display function for the problem
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
    # display function for boxlock
    def displayBoxLock(self):
        print("Boxlock: ")
        for i in range(9):
            if i % 3 == 0 and i != 0:
                print("---------------------")
            for j in range(9):
                if j % 3 == 0 and j != 0:
                    print("|", end = " ")
                print("1", end = " ") if self.softboxlocked[i][j] else print("0", end = " ")
                if j == 8:
                    print()
        print()
    def displayLineLockedx(self):
        print("LineLockedx: ")
        for i in range(9):
            if i % 3 == 0 and i != 0:
                print("---------------------")
            for j in range(9):
                if j % 3 == 0 and j != 0:
                    print("|", end = " ")
                print("1", end = " ") if self.softlinelockedx[i][j] else print("0", end = " ")
                if j == 8:
                    print()
        print()
    def displayLineLockedy(self):
        print("LineLockedy: ")
        for i in range(9):
            if i % 3 == 0 and i != 0:
                print("---------------------")
            for j in range(9):
                if j % 3 == 0 and j != 0:
                    print("|", end = " ")
                print("1", end = " ") if self.softlinelockedy[i][j] else print("0", end = " ")
                if j == 8:
                    print()
        print()
    
    def resetLocks(self, tempCopy):
        self.softboxlocked = tempCopy.softboxlocked
        self.softlinelockedx = tempCopy.softlinelockedx
        self.softlinelockedy = tempCopy.softlinelockedy
    # complex display function to show the current possibilities for all the nodes 
    def notesDisplay(self):
        for i in range(9):
            if i % 3 == 0 and i != 0:
                print("-------------------------------------------------------------------------")
            for j in range(9):
                if j % 3 == 0 and j != 0:
                    print("|", end = " ")
                for k in range(3):
                    if self.layout[i][j].val != 0:
                        print(self.layout[i][j].note[k], end = " ")
                    else:
                        if self.layout[i][j].note[k] == 0:
                            print(" ", end = " ")
                        else:
                            print(self.layout[i][j].note[k], end = " ")
                if j != 8:
                    print("|", end = " ")
            print()
            for j in range(9):
                if j % 3 == 0 and j != 0:
                    print("|", end = " ")
                for k in range(3,6):
                    if self.layout[i][j].val != 0:
                        print(self.layout[i][j].note[k], end = " ")
                    else:
                        if self.layout[i][j].note[k] == 0:
                            print(" ", end = " ")
                        else:
                            print(self.layout[i][j].note[k], end = " ")
                if j != 8:
                    print("|", end = " ")
            print() 
            for j in range(9):
                if j % 3 == 0 and j != 0:
                    print("|", end = " ")
                for k in range(6,9):
                    if self.layout[i][j].val != 0:
                        print(self.layout[i][j].note[k], end = " ")
                    else:
                        if self.layout[i][j].note[k] == 0:
                            print(" ", end = " ")
                        else:
                            print(self.layout[i][j].note[k], end = " ")
                if j != 8:
                    print("|", end = " ")
            print()
            if i != 8:
                print("-------------------------------------------------------------------------")

    def displayAll(self):
        print()
        self.display()
        print()
        self.notesDisplay()
        print()
    # the updateNotes function combs through all current values in the problem and removes the redundant notes from their rows, columns, and boxes 
    def updateNotes(self):
        for i in range(9):
            for j in range(9):
                if self.layout[i][j].val != 0:
                    x = self.layout[i][j].val
                    for a in range(9):
                        if a != j:
                            self.layout[i][a].note[x-1] = 0
                        if a != i:
                            self.layout[a][j].note[x-1] = 0
                    rowOffset = (i//3) * 3
                    colOffset = (j//3) * 3
                    for a in range(rowOffset, rowOffset + 3):
                        for b in range(colOffset, colOffset + 3):                           
                            self.layout[a][b].note[x-1] = 0

    
    def subUpdateNotes(self, x, coords, vals):
        match x:
            case 'box':
                rowOffset = (coords[0][0]//3) * 3
                colOffset = (coords[0][1]//3) * 3
                for i in range(rowOffset, rowOffset + 3):
                    for j in range(colOffset, colOffset + 3):
                        if (i,j) in coords or self.layout[i][j].val != 0:
                            continue
                        for k in vals:
                            self.layout[i][j].note[k-1] = 0
            case 'row':
                rowVal = coords[0][0]
                for j in range(9):
                    if (rowVal, j) in coords or self.layout[rowVal][j].val != 0:
                        continue
                    for k in vals:
                        self.layout[rowVal][j].note[k-1] = 0
            case 'col':
                colVal = coords[0][1]
                for i in range(9):
                    if (i, colVal) in coords or self.layout[i][colVal].val != 0:
                        continue
                    for k in vals:
                        self.layout[i][colVal].note[k-1] = 0

    # def miniUpdateNotes(self, x, coords, vals):
    #     match x:
    #         case 'row':
    #             rowVal = coords[0][0]
    #             for i in range(rowVal
    
    # basic termination function
    def solved(self):
        for i in range(9):
            for j in range(9):
                if self.layout[i][j].val == 0:
                    return False
        return True

    def stuck(self, temp):
        stuckFlag = True
        for i in range(9):
            for j in range(9):
                if not self.layout[i][j].equals(temp.layout[i][j]) or not self.softboxlocked[i][j] == temp.softboxlocked[i][j] or not self.softlinelockedx[i][j] == temp.softlinelockedx[i][j] or not self.softlinelockedy[i][j] == temp.softlinelockedy[i][j]:
                    stuckFlag = False
        return stuckFlag

    # cleanup function "cleans up" the board after a value gets changed based on notes
    # function calls itself if a change gets made, which restarts the function
    def cleanup(self):
        # loop that goes through all nodes
        for i in range(9):
            for j in range(9):
                # skips iteration if value exists in current Node
                if self.layout[i][j].val == 0:
                    tempNode = self.layout[i][j]
                else:
                    continue
                # creates a temporary set of all nonzero notes in the current node
                tempSet = set(self.layout[i][j].note)
                tempSet.discard(0)
                if len(tempSet) == 1:
                    a = tempSet.pop()
                    print(f"Single value found {a} at index ({i}, {j})")
                    self.locked[i][j] = self.softboxlocked[i][j] = self.softlinelockedx[i][j] = self.softlinelockedy[i][j] = True
                    self.layout[i][j].setVal(a)
                    self.cleanup()
                    continue
                for a in tempSet:
                    temp = {a}
                    if self.singleBoxCheck([(i,j)], temp):
                        print(f"SingleBoxCheck found {a} at index ({i}, {j})")
                        self.softboxlocked[i][j] = self.softlinelockedx[i][j] = self.softlinelockedy[i][j] = True
                        self.layout[i][j].setVal(a)
                        self.cleanup()
                        break
                    elif self.singleRowCheck([(i,j)], temp):
                        print(f"SingleRowCheck found {a} at index ({i}, {j})")
                        self.softboxlocked[i][j] = self.softlinelockedx[i][j] = self.softlinelockedy[i][j] = True
                        self.layout[i][j].setVal(a)
                        self.cleanup()
                        break
                    elif self.singleColCheck([(i,j)], temp):
                        print(f"SingleColCheck found {a} at index ({i}, {j})")
                        self.locked[i][j] = self.softboxlocked[i][j] = self.softlinelockedx[i][j] = self.softlinelockedy[i][j] = True
                        self.layout[i][j].setVal(a)
                        self.cleanup()
                        break
                           

    # this function checks for boxlocks, these are a set of nodes that effectively cancel out the values the hold for the rest of the box
    def checkBoxLock(self):
        # iterates through entire puzzle
        for size in range(2,5):
            for i in range(9):
                for j in range(9):
                    if self.locked[i][j] or self.softboxlocked[i][j]:
                        continue
                    tempSet = set(self.layout[i][j].note)
                    tempSet.discard(0)
                    rowOffset = (i//3) * 3
                    colOffset = (j//3) * 3
                    lockList = [(i,j)]
                    if size == len(tempSet) == 2:
                        boxLock = False
                        for a in range(rowOffset,rowOffset + 3):
                            if boxLock:
                                break
                            for b in range(colOffset, colOffset + 3):
                                if self.layout[a][b].val != 0 or (i, j) == (a, b):
                                    continue
                                tempSet2 = set(self.layout[a][b].note)
                                tempSet2.discard(0)
                                lockList = [(i, j), (a, b)]
                                if tempSet == tempSet2 or self.singleBoxCheck(lockList, tempSet):
                                    boxLock = True
                                    for a, b in lockList:
                                        self.softboxlocked[a][b] = True
                                    self.subUpdateNotes('box', lockList, tempSet)
                                    break
                        if not boxLock:
                            goodcheck, coordList, masterSet = self.loopCheck2(False, lockList, tempSet, 0)
                            if goodcheck:
                                # print(f"box {len(coordList)} 2: {masterSet} at locs {coordList}")
                                self.subUpdateNotes('box', coordList, masterSet)
                                for a, b in coordList:
                                    self.softboxlocked[a][b] = True
                                for val in masterSet:
                                    tempVal = {val}
                                    tempCoords = []
                                    for a, b in coordList:
                                        if val in self.layout[a][b].note:
                                            tempCoords += [(a, b)]
                                    if self.inRow(tempCoords):
                                        self.subUpdateNotes('row', tempCoords, tempVal)
                                    elif self.inCol(tempCoords):
                                        self.subUpdateNotes('col', tempCoords, tempVal)
                    elif size == len(tempSet) == 3:
                        goodcheck, coordList, masterSet = self.loopCheck3(False, [(i,j)], tempSet, 0)
                        if goodcheck:
                            # print(f"box {len(coordList)} 3: {masterSet} at locs {coordList}")
                            self.subUpdateNotes('box', coordList, masterSet)
                            for a, b in coordList:
                                self.softboxlocked[a][b] = True
                            if len(coordList) == 3:
                                if self.inRow(coordList):
                                    self.subUpdateNotes('row', coordList, masterSet)
                                if self.inCol(coordList):
                                    self.subUpdateNotes('col', coordList, masterSet)
                            for val in masterSet:
                                tempVal = {val}
                                tempCoords = []
                                for a, b in coordList:
                                    if val in self.layout[a][b].note:
                                        tempCoords += [(a, b)]
                                if self.inRow(tempCoords):
                                    self.subUpdateNotes('row', tempCoords, tempVal)
                                elif self.inCol(tempCoords):
                                    self.subUpdateNotes('col', tempCoords, tempVal)
                    elif size == len(tempSet) == 4:
                        goodcheck, coordList, masterSet = self.loopCheck3(False, [(i,j)], tempSet, 0)
                        if goodcheck:
                            # print(f"box {len(coordList)} 4: {masterSet} at locs {coordList}")
                            self.subUpdateNotes('box', coordList, masterSet)
                            for a, b in coordList:
                                self.softboxlocked[a][b] = True
                            for val in masterSet:
                                tempVal = {val}
                                tempCoords = []
                                for a, b in coordList:
                                    if val in self.layout[a][b].note:
                                        tempCoords += [(a, b)]
                                if self.inRow(tempCoords):
                                    self.subUpdateNotes('row', tempCoords, tempVal)
                                elif self.inCol(tempCoords):
                                    self.subUpdateNotes('col', tempCoords, tempVal)
        
    def checkRowLock(self):
        # outer loop is to prioritize nodes who have lower sizes to be checked first
        for size in range(2,5):
            for i in range(9):
                for j in range(9):
                    if self.locked[i][j] or self.softlinelockedx[i][j]:
                        continue
                    tempSet = set(self.layout[i][j].note)
                    tempSet.discard(0)
                    lockList = [(i, j)]
                    if size == len(tempSet) == 2:
                        linelock = False
                        for a in range(j + 1, 9):
                            temp = set(self.layout[i][a].note)
                            temp.discard(0)
                            lockList = [(i, j),(i, a)]
                            if tempSet == temp or self.singleRowCheck(lockList, tempSet):
                                # print(f"found naked row pair {tempSet} at {i},{j}, {i},{a}")
                                linelock = True
                                for a, b in lockList:
                                    self.softlinelockedx[a][b] = True
                                self.subUpdateNotes('row', lockList, tempSet)
                                break
                        if not linelock:
                            goodcheck, coordList, masterSet = self.loopCheck2(False, [(i,j)], tempSet, 1)
                            if goodcheck:
                                # print(f"row {len(coordList)} 2: {masterSet} at locs {coordList}")
                                self.subUpdateNotes('row', coordList, masterSet)
                                for a, b in lockList:
                                    self.softlinelockedx[a][b] =True
                                for val in masterSet:
                                    tempVal = {val}
                                    tempCoords = []
                                    for a, b in coordList:
                                        if val in self.layout[a][b].note:
                                            tempCoords += [(a, b)]
                                    if self.inBox(tempCoords):
                                        self.subUpdateNotes('box', tempCoords, tempVal)
                    elif size == len(tempSet) == 3:
                        goodcheck, coordList, masterSet = self.loopCheck3(False, [(i,j)], tempSet, 1)
                        if goodcheck:
                            # print(f"row {len(coordList)} 3: {masterSet} at locs {coordList}")
                            self.subUpdateNotes('row', coordList, masterSet)
                            for a, b in coordList:
                                self.softlinelockedx[a][b] = True
                            for val in masterSet:
                                tempVal = {val}
                                tempCoords = []
                                for a, b in coordList:
                                    if val in self.layout[a][b].note:
                                        tempCoords += [(a, b)]
                                if self.inBox(tempCoords):
                                    self.subUpdateNotes('box', tempCoords, tempVal)
                    elif size == len(tempSet) == 4:
                        goodcheck, coordList, masterSet = self.loopCheck4(False, [(i,j)], tempSet, 1)
                        if goodcheck:
                            self.subUpdateNotes('row', coordList, masterSet)
                            # print(f"row {len(coordList)} 4: {masterSet} at locs {coordList}")
                            for a, b in coordList:
                                self.softlinelockedx[a][b] = True
                            for val in masterSet:
                                tempVal = {val}
                                tempCoords = []
                                for a, b in coordList:
                                    if val in self.layout[a][b].note:
                                        tempCoords += [(a, b)]
                                if self.inBox(tempCoords):
                                    self.subUpdateNotes('box', tempCoords, tempVal)
                    # elif size == len(tempSet) == 5:
                    #     goodcheck, coordList, masterSet = self.loopCheck5(False, [(i,j)], tempSet, 1)
                    #     if goodcheck:
                    #         print(f"row {len(coordList)} 5: {masterSet} at locs {coordList}")
                    #         for a, b in coordList:
                    #             self.softlinelockedx[a][b] = True
                    #         self.subUpdateNotes('row', coordList, masterSet)
       
    def checkColLock(self):
        for size in range(2,5):
            for i in range(9):
                for j in range(9):
                    if self.layout[i][j].val != 0 or self.softlinelockedy[i][j]:
                        continue
                    tempSet = set(self.layout[i][j].note)
                    tempSet.discard(0)
                    linelock = False
                    if size == len(tempSet) == 2:
                        for a in range(i + 1, 9):
                            temp = set(self.layout[a][j].note)
                            temp.discard(0)
                            lockList = [(i, j),(a, j)]
                            if tempSet == temp or self.singleColCheck(lockList, tempSet):
                                # print(f"found naked col pair {tempSet} at {i},{j}, {a},{j}")
                                linelock = True
                                for a, b in lockList:
                                    self.softlinelockedy[a][b] = True
                                self.subUpdateNotes('col', lockList, tempSet)
                                break
                        if not linelock:
                            goodcheck, coordList, masterSet = self.loopCheck2(False, [(i,j)], tempSet, 2)
                            if goodcheck:
                                # print(f"col {len(coordList)} 2: {masterSet} at locs {coordList}")
                                self.subUpdateNotes('col', coordList, masterSet)
                                for a, b in lockList:
                                    self.softlinelockedy[a][b] = True
                                    # print(f"({a}, {b})")
                                for val in masterSet:
                                    tempVal = [val]
                                    tempCoords = []
                                    for a, b in coordList:
                                        if val in self.layout[a][b].note:
                                            tempCoords += [(a, b)]
                                    if self.inBox(tempCoords):
                                        self.subUpdateNotes('box', tempCoords, tempVal)
                    elif size == len(tempSet) == 3:
                        goodcheck, coordList, masterSet = self.loopCheck3(False, [(i,j)], tempSet, 2)
                        if goodcheck:
                            # print(f"col {len(coordList)} 3: {masterSet} at locs {coordList}")
                            self.subUpdateNotes('col', coordList, masterSet)
                            for a, b in coordList:
                                self.softlinelockedy[a][b] = True
                            for val in masterSet:
                                tempVal = [val]
                                tempCoords = []
                                for a, b in coordList:
                                    if val in self.layout[a][b].note:
                                        tempCoords += [(a, b)]
                                if self.inBox(tempCoords):
                                    self.subUpdateNotes('box', tempCoords, tempVal)
                    elif size == len(tempSet) == 4:
                        goodcheck, coordList, masterSet = self.loopCheck4(False, [(i,j)], tempSet, 2)
                        if goodcheck:
                            # print(f"col {len(coordList)} 4: {masterSet} at locs {coordList}")
                            self.subUpdateNotes('col', coordList, masterSet)
                            for a, b in coordList:
                                self.softlinelockedy[a][b] = True
                            for val in masterSet:
                                tempVal = [val]
                                tempCoords = []
                                for a, b in coordList:
                                    if val in self.layout[a][b].note:
                                        tempCoords += [(a, b)]
                                if self.inBox(tempCoords):
                                    self.subUpdateNotes('box', tempCoords, tempVal)
    # parameter is a tuple:
    # the first value represents if a loop is found,
    # the second value is a list of coordinates of already checked,
    # the third value is a masterSet of all noted values of the coordinates list
    def finalizeLocks(self):
        for i in range(3):
            for j in range(3):
                rowOffset = i * 3
                colOffset = j * 3
                tempSet = set()
                coordList = []
                for row in range(rowOffset, rowOffset + 3):
                    for col in range(colOffset, colOffset + 3):
                        if self.locked[row][col] or self.softlinelockedx[row][col]:
                            continue
                        tempSet = set(tempSet.union(set(self.layout[row][col].note)))
                        self.softboxlocked[row][col] = True
                        coordList += [(row,col)]
                tempSet.discard(0)
                for val in tempSet:
                    tempVal = {val}
                    tempCoords = []
                    for a, b in coordList:
                        if val in self.layout[a][b].note:
                            tempCoords += [(a, b)]
                    if len(tempCoords) == 0:
                        continue
                    if self.inRow(tempCoords) and self.singleBoxCheck(tempCoords, {val}):
                        self.subUpdateNotes('row', tempCoords, tempVal)
                    elif self.inCol(tempCoords) and self.singleBoxCheck(tempCoords, {val}):
                        self.subUpdateNotes('col', tempCoords, tempVal)
        for row in range(9):
            coordList = []
            tempSet = set()
            for col in range(9):
                if self.locked[row][col] or self.softlinelockedx[row][col]:
                    continue
                tempSet = set(tempSet.union(set(self.layout[row][col].note)))
                self.softlinelockedx[row][col] = True
                coordList += [(row, col)]
            tempSet.discard(0)
            for val in tempSet:
                tempVal = {val}
                tempCoords = []
                for a, b in coordList:
                    if val in self.layout[a][b].note:
                        tempCoords += [(a, b)]
                if len(tempCoords) == 0:
                    continue
                if self.inBox(tempCoords) and self.singleRowCheck(tempCoords, {val}):
                    self.subUpdateNotes('box', tempCoords, tempVal)
        for col in range(9):
            coordList = []
            tempSet = set()
            for row in range(9):
                if self.locked[row][col] or self.softlinelockedy[row][col]:
                    continue
                tempSet = set(tempSet.union(set(self.layout[row][col].note)))
                self.softlinelockedy[row][col] = True
                coordList += [(row, col)]
            tempSet.discard(0)
            for val in tempSet:
                tempVal = {val}
                tempCoords = []
                for a, b in coordList:
                    if val in self.layout[a][b].note:
                        tempCoords += [(a, b)]
                if len(tempCoords) == 0:
                    continue
                if self.inBox(tempCoords) and self.singleColCheck(tempCoords, {val}):
                    self.subUpdateNotes('box', tempCoords, tempVal)
    def loopCheck2(self, found, coordList, masterSet, x):
        match x:
            case 0:
                rowOffset = (coordList[0][0]//3) * 3
                colOffset = (coordList[0][1]//3) * 3
                # checks all values in a square, skips over penned in values, values that have been checked or have values
                for a in range(rowOffset, rowOffset + 3):
                    for b in range(colOffset, colOffset + 3):
                        if (a, b) in coordList or self.layout[a][b].val != 0 or self.softboxlocked[a][b]:
                            continue    
                        tempSet = set(self.layout[a][b].note)
                        tempSet.discard(0)
                        if len(tempSet) != 2:
                            continue
                        tempSet2 = masterSet.intersection(tempSet)
                        if len(tempSet2) != 1:
                            continue
                        newMasterSet = masterSet.union(tempSet)
                        if not(len(newMasterSet) == len(masterSet) + 1 or newMasterSet == masterSet):
                            continue
                        newCoordList = coordList + [(a, b)]
                        if len(newMasterSet) == len(newCoordList) and len(newCoordList) >= 3 and self.singleBoxCheck(newCoordList, newMasterSet):
                            return (True, newCoordList, newMasterSet)
                        result = self.loopCheck2(False, newCoordList, newMasterSet, 0)
                        if result[0]:
                            return result
            case 1:
                rowSet = coordList[0][0]
                for a in range(9):
                    if self.layout[rowSet][a].val != 0 or (rowSet, a) in coordList or self.softlinelockedx[rowSet][a]:
                        continue
                    tempSet = set(self.layout[rowSet][a].note)
                    tempSet.discard(0)
                    if len(tempSet) != 2:
                        continue
                    tempSet2 = masterSet.intersection(tempSet)
                    if len(tempSet2) != 1:
                        continue
                    newMasterSet = masterSet.union(tempSet)
                    if not(len(newMasterSet) == len(masterSet) + 1 or newMasterSet == masterSet):
                            continue
                    newCoordList = coordList + [(rowSet, a)]
                    if len(newMasterSet) == len(newCoordList) and len(newCoordList) >= 3 and self.singleBoxCheck(newCoordList, newMasterSet):
                        return (True, newCoordList, newMasterSet)
                    result = self.loopCheck2(False, newCoordList, newMasterSet, 1)
                    if result[0]:
                        return result
            case 2:
                colSet = coordList[0][1]
                for a in range(9):
                    if self.layout[a][colSet].val != 0 or (a, colSet) in coordList or self.softlinelockedy[a][colSet]:
                        continue
                    tempSet = set(self.layout[a][colSet].note)
                    tempSet.discard(0)
                    if len(tempSet) != 2:
                        continue
                    tempSet2 = masterSet.intersection(tempSet)
                    if len(tempSet2) != 1:
                        continue
                    newMasterSet = masterSet.union(tempSet)
                    if not(len(newMasterSet) == len(masterSet) + 1 or newMasterSet == masterSet):
                            continue
                    newCoordList = coordList + [(a, colSet)]
                    if len(newMasterSet) == len(newCoordList) and len(newCoordList) >= 3 and self.singleBoxCheck(newCoordList, newMasterSet):
                        return (True, newCoordList, newMasterSet)
                    result = self.loopCheck2(False, newCoordList, newMasterSet, 2)
                    if result[0]:
                        return result
        return (False, coordList, masterSet)
    
    # recursive function that checks for naked triples or higher where each node has a note array of length of 3
    # returns the same tuple as loopCheck2
    def loopCheck3(self, found, coordList, masterSet, x):
        match x: 
            case 0:
                rowOffset = (coordList[0][0]//3) * 3
                colOffset = (coordList[0][1]//3) * 3
                for a in range(rowOffset, rowOffset + 3):
                    for b in range(colOffset, colOffset + 3):
                        if (a, b) in coordList or self.layout[a][b].val != 0 or self.softboxlocked[a][b]:
                            continue
                        tempSet = set(self.layout[a][b].note)
                        tempSet.discard(0)
                        if len(tempSet) > 3 or not tempSet <= masterSet:
                            continue
                        newMasterSet = masterSet.union(tempSet)
                        newCoordList = coordList + [(a, b)]
                        if len(newMasterSet) == len(newCoordList) and len(newCoordList) >= 3 and self.singleBoxCheck(newCoordList, newMasterSet):
                            return (True, newCoordList, newMasterSet)
                        result = self.loopCheck3(False, newCoordList, newMasterSet, 0)
                        if result[0]:
                            return result
                return (False, coordList, masterSet)
            case 1:
                rowSet = coordList[0][0]
                for a in range(9):
                    if self.layout[rowSet][a].val != 0 or (rowSet, a) in coordList or self.softlinelockedx[rowSet][a]:
                        continue
                    tempSet = set(self.layout[rowSet][a].note)
                    tempSet.discard(0)
                    if len(tempSet) > 3 or not tempSet <= masterSet:
                        continue
                    newMasterSet = masterSet.union(tempSet)
                    newCoordList = coordList + [(rowSet, a)]
                    if len(newMasterSet) == len(newCoordList) and len(newCoordList) >= 3 and self.singleRowCheck(newCoordList, newMasterSet):
                        return(True, newCoordList, newMasterSet)
                    result = self.loopCheck3(False, newCoordList, newMasterSet, 1)
                    if result[0]:
                        return result
            case 2:
                colSet = coordList[0][1]
                for a in range(9):
                    if self.layout[a][colSet].val != 0 or (a, colSet) in coordList or self.softlinelockedy[a][colSet]:
                        continue
                    tempSet = set(self.layout[a][colSet].note)
                    tempSet.discard(0)
                    if len(tempSet) > 3 or not tempSet <= masterSet:
                        continue
                    newMasterSet = masterSet.union(tempSet)
                    newCoordList = coordList + [(a, colSet)]
                    if len(newMasterSet) == len(newCoordList) and len(newCoordList) >= 3 and self.singleColCheck(newCoordList, newMasterSet):
                        return(True, newCoordList, newMasterSet)
                    result = self.loopCheck3(False, newCoordList, newMasterSet, 2)
                    if result[0]:
                        return result
        return (False, coordList, masterSet)

    def loopCheck4(self, found, coordList, masterSet, x):
        match x: 
            case 0:
                rowOffset = (coordList[0][0]//3) * 3
                colOffset = (coordList[0][1]//3) * 3
                for a in range(rowOffset, rowOffset + 3):
                    for b in range(colOffset, colOffset + 3):
                        if (a, b) in coordList or self.layout[a][b].val != 0 or self.softboxlocked[a][b]:
                            continue
                        tempSet = set(self.layout[a][b].note)
                        tempSet.discard(0)
                        if len(tempSet) > 4 or not tempSet <= masterSet:
                            continue
                        newMasterSet = masterSet.union(tempSet)
                        newCoordList = coordList + [(a, b)]
                        if len(newMasterSet) == len(newCoordList) and len(newCoordList) >= 4 and self.singleBoxCheck(newCoordList, newMasterSet):
                            return (True, newCoordList, newMasterSet)
                        result = self.loopCheck4(False, newCoordList, newMasterSet, 0)
                        if result[0]:
                            return result
                return (False, coordList, masterSet)
            case 1:
                rowSet = coordList[0][0]
                for a in range(9):
                    if self.layout[rowSet][a].val != 0 or (rowSet, a) in coordList or self.softlinelockedx[rowSet][a]:
                        continue
                    tempSet = set(self.layout[rowSet][a].note)
                    tempSet.discard(0)
                    if len(tempSet) > 4 or not tempSet <= masterSet:
                        continue
                    newMasterSet = masterSet.union(tempSet)
                    newCoordList = coordList + [(rowSet, a)]
                    if len(newMasterSet) == len(newCoordList) and len(newCoordList) >= 4 and self.singleRowCheck(newCoordList, newMasterSet):
                        return(True, newCoordList, newMasterSet)
                    result = self.loopCheck4(False, newCoordList, newMasterSet, 1)
                    if result[0]:
                        return result
            case 2:
                colSet = coordList[0][1]
                for a in range(9):
                    if self.layout[a][colSet].val != 0 or (a, colSet) in coordList or self.softlinelockedy[a][colSet]:
                        continue
                    tempSet = set(self.layout[a][colSet].note)
                    tempSet.discard(0)
                    if len(tempSet) > 4 or not tempSet <= masterSet:
                        continue
                    newMasterSet = masterSet.union(tempSet)
                    newCoordList = coordList + [(a, colSet)]
                    if len(newMasterSet) == len(newCoordList) and len(newCoordList) >= 4 and self.singleColCheck(newCoordList, newMasterSet):
                        return(True, newCoordList, newMasterSet)
                    result = self.loopCheck4(False, newCoordList, newMasterSet, 2)
                    if result[0]:
                        return result
        return (False, coordList, masterSet)
                         
    # boolean functions, returns true if the coordsList forms a straight line
    def inBox(self, coordsList):
        tempRow = coordsList[0][0]//3
        tempCol = coordsList[0][1]//3
        for i, j in coordsList:
            if i//3 != tempRow or j//3 != tempCol:
                return False
        return True
    def inRow(self, coordsList):
        tempRow = coordsList[0][0]
        for i, j in coordsList:
            if i != tempRow:
                return False
        return True
    def inCol(self, coordsList):
        tempCol = coordsList[0][1]
        for i, j in coordsList:
            if j != tempCol:
                return False
        return True

    # boolean functions only called in a boxlock scenario, returns true if the value provided forms a sub row or column within a boxLock
    def subSameRow(self, coordsList, val):
        # sets row to be checked, once found it breaks the loops and begins real check
        for a, b in coordsList:
            if val in self.layout[a][b].note:
                setRow = a
                break
        # real check, skips coordinates that don't contain the value, returns false if the value is found in the notes of a node with a different row
        for a, b in coordsList:
            if val not in self.layout[a][b].note:
                continue
            if a != setRow:
                return False
        return True
    def subSameCol(self, coordsList, val):
        for a, b in coordsList:
            if val in self.layout[a][b].note:
                setCol = b
                break
        for a, b in coordsList:
            if val not in self.layout[a][b].note:
                continue
            if b != setCol:
                return False
        return True
    # the single check functions check individual boxes, rows, and columns
    # the single box check function checks the current box for the first item in coords
    def singleBoxCheck(self, coords, vals):
        rowOffset, colOffset = coords[0]
        rowOffset = (rowOffset//3) * 3
        colOffset = (colOffset//3) * 3
        for i in range(rowOffset, rowOffset + 3):
            for j in range(colOffset, colOffset + 3):
                if (i, j) in coords:
                    continue
                for k in vals:
                    if k in self.layout[i][j].note:
                        return False
        return True
    # the single row check function checks if a given value exists in the notes for a row outside the confines of the coordinate list
    def singleRowCheck(self, coords, vals):
        rowSet, colSet = coords[0]
        for j in range(9):
            if (rowSet, j) in coords:
                continue
            for k in vals:
                if k in self.layout[rowSet][j].note:
                    return False
        return True
    
    def singleColCheck(self, coords, vals):
        rowSet, colSet = coords[0]
        for i in range(9):
            if (i, colSet) in coords:
                continue
            for k in vals:
                if k in self.layout[i][colSet].note:
                    return False
        return True

    # ********************************************************************************************************************
    # ***********************************************TOUGH STRATEGIES*****************************************************
    # ********************************************************************************************************************
    # utility function for xwing searches
    def xWing(self):
        temp = copy.deepcopy(self)
        for i in range(8):
            for j in range(8):
                if self.layout[i][j].val != 0:
                    continue
                for val in self.layout[i][j].note:
                    self.squareFind((i,j), val)
                    if not temp.stuck(self):
                        # print(i, j, val)
                        return
    # searches for xwings and updates accordingly
    # an x wing is an instance where 2 rows or columns have only 2 notes for the same value
    # if they form a square, the respective column or row's notes can remove the value that forms the square
    def squareFind(self, coords, val):
        row, col = coords
        goodSquare = []
        temp = [val]
        if self.softlinelockedx[row][col]:
            for j in range(col + 1, 9):
                if self.layout[row][j].val != 0:
                    continue
                if val in self.layout[row][j].note:
                    if self.singleRowCheck([(row, col), (row, j)], temp):
                        col2 = j
                        goodSquare = [(row,col), (row,j)]
                        break
            if len(goodSquare) == 2:
                for i in range(9):
                    if i == row:
                        continue
                    if val in self.layout[i][col].note and val in self.layout[i][col2].note:
                        if self.singleRowCheck([(i, col), (i, col2)], temp):
                            goodSquare += [(i,col), (i, col2)]
                            break
                if len(goodSquare) == 4:
                    # print(f"Erasing {val} from cols {goodSquare[0][1]} & {goodSquare[1][1]}")
                    self.subUpdateNotes('col', [goodSquare[0], goodSquare[2]], temp)
                    self.subUpdateNotes('col', [goodSquare[1], goodSquare[3]], temp)
        elif self.softlinelockedy[row][col]:
            for i in range(row + 1, 9):
                if val in self.layout[i][col].note:
                    if self.singleColCheck([(row, col), (i, col)], temp):
                        row2 = i
                        goodSquare = [(row, col), (i, col)]
                        break
            if len(goodSquare) == 2:
                for j in range(9):
                    if j == col:
                        continue
                    if val in self.layout[row][j].note and val in self.layout[row2][j].note:
                        if self.singleColCheck([(row, j), (row2, j)], temp):
                            goodSquare += [(row,j), (row2, j)]
                            break
                if len(goodSquare) == 4:
                    # print(f"Erasing {val} from rows {goodSquare[0][0]} & {goodSquare[1][0]}")
                    self.subUpdateNotes('row', [goodSquare[0], goodSquare[2]], temp)
                    self.subUpdateNotes('row', [goodSquare[1], goodSquare[3]], temp)
    # ********************************************************************************************************************
    # Performs chute remote pairs strategy & updates accordingly, "naked" pairs which exist in different rows and columns (within square sight of a node)
    def chuteRemotePairs(self):
        tempCopy = copy.deepcopy(self)
        for i in range(9):
            for j in range(9):
                # if change is made, teminate function
                if not tempCopy.stuck(self):
                    # print("col change made")
                    return
                # only check (i,j) if it fulfills potential remote pair parameters
                if self.layout[i][j].val != 0:
                    continue
                tempSet = set(self.layout[i][j].note)
                tempSet.discard(0)
                remotePair = []
                if len(tempSet) != 2:
                    continue
                rowOffset = (i//3) * 3
                colOffset = (j//3) * 3
                # checks horizontal chute for remote pair (avoiding current box and row)
                for a in range(rowOffset, rowOffset + 3):
                    if a == i:
                        continue
                    # avoids checking the columns of the current column's box
                    for b in range(9):
                        if colOffset <= b < colOffset + 3 or self.layout[a][b].val != 0:
                            continue
                        temp = set(self.layout[a][b].note)
                        temp.discard(0)
                        if tempSet == temp:
                            remotePair = [(i,j),(a,b)]
                # found remote pair in vertical chute
                if len(remotePair) == 2:
                    # print(f"Row Remote Pair: {remotePair}")
                    x,y = remotePair[1]
                    colOffset2 = (y//3) * 3
                    pencilSet = set()
                    pennedSet = set()
                    # creates list of all noted values (0 excluded) in the appropriate nodes as well as all of the penned in values
                    for a in range(rowOffset, rowOffset + 3):
                        if a == x or a == i:
                            continue
                        for b in range(9):
                            if colOffset <= b < colOffset + 3 or colOffset2 <= b < colOffset2 + 3:
                                continue
                            # print(f"({a}, {b})")
                            if self.layout[a][b].val == 0:
                                temp = set(self.layout[a][b].note)
                                temp.discard(0)
                                pencilSet = pencilSet.union(temp)
                            else:
                                pennedSet.add(self.layout[a][b].val)   
                    # if all values are penned in (pencilSet is empty), then it checks if only one or neither of the values exist in the 
                    if len(pencilSet) == 0:
                        # if neither value in the remote pair is penned in, then performs double elimination
                        if len(tempSet.intersection(pennedSet)) == 0:
                            # print(f"Row Remote Pair 1: {remotePair}")
                            for val in tempSet:
                                for a in range(colOffset, colOffset + 3):
                                    self.layout[x][a].note[val-1] = 0
                                for a in range(colOffset2, colOffset2 + 3):
                                    self.layout[i][a].note[val-1] = 0
                        # if only one remote pair is penned in, erases that value from the appropraite nodes
                        elif len(tempSet.intersection(pennedSet)) == 1:
                            # print(f"Row Remote Pair 2: {remotePair}")
                            val = set(tempSet.intersection(pennedSet)).pop()
                            for a in range(colOffset, colOffset + 3):
                                self.layout[x][a].note[val-1] = 0
                            for a in range(colOffset2, colOffset2 + 3):
                                self.layout[i][a].note[val-1] = 0
                    # otherwise it checks for what values are pencilled in
                    elif len(tempSet.intersection(pencilSet.union(pennedSet))) == 1:
                        val = set(tempSet.intersection(pencilSet.union(pennedSet))).pop
                        if len(pencilSet.intersection(tempSet)) == 1:
                            # print(f"Row Remote Pair 3: {remotePair}")
                            val = set(pencilSet.intersection(tempSet)).pop()
                            for a in range(colOffset, colOffset + 3):
                                self.layout[x][a].note[val-1] = 0
                            for a in range(colOffset2, colOffset2 + 3):
                                self.layout[i][a].note[val-1] = 0
                # if change is made, teminate function
                if not tempCopy.stuck(self):
                    # print("row change made")
                    return
                # resets key variables and performs search on vertical chute
                remotePair = []
                for a in range(9):
                    if rowOffset <= a < rowOffset + 3:
                            continue
                    for b in range(colOffset, colOffset + 3):
                        if b == j or self.layout[a][b].val != 0:
                            continue
                        temp = set(self.layout[a][b].note)
                        temp.discard(0)
                        if tempSet == temp:
                            remotePair = [(i,j),(a,b)]
                if len(remotePair) == 2:
                    # print(f"Col Remote Pair: {remotePair}")
                    x,y = remotePair[1]
                    rowOffset2 = (x//3) * 3
                    pencilSet = set()
                    pennedSet = set()
                    for a in range(9):
                        if rowOffset <= a < rowOffset + 3 or rowOffset2 <= a < rowOffset2 + 3:
                            continue
                        for b in range(colOffset, colOffset + 3):
                            if b == y or b == j:
                                continue
                            # print(f"({a}, {b})")
                            if self.layout[a][b].val == 0:
                                temp = set(self.layout[a][b].note)
                                temp.discard(0)
                                pencilSet = pencilSet.union(temp)
                            else:
                                pennedSet.add(self.layout[a][b].val)
                    if len(pencilSet) == 0:
                        if len(tempSet.intersection(pennedSet)) == 0:
                            # print(f"Col Remote Pair 1: {remotePair}")
                            for val in tempSet:
                                for a in range(rowOffset, rowOffset + 3):
                                    self.layout[a][y].note[val-1] = 0
                                for a in range(rowOffset2, rowOffset2 + 3):
                                    self.layout[a][j].note[val-1] = 0
                        elif len(tempSet.intersection(pennedSet)) == 1:
                            # print(f"Col Remote Pair 2: {remotePair}")
                            val = set(tempSet.intersection(pennedSet)).pop()
                            for a in range(rowOffset, rowOffset + 3):
                                self.layout[a][y].note[val-1] = 0
                            for a in range(rowOffset2, rowOffset2 + 3):
                                self.layout[a][j].note[val-1] = 0
                    elif len(tempSet.intersection(pencilSet.union(pennedSet))) == 1:
                        # print(f"Col Remote Pair 3: {remotePair}")
                        val = set(tempSet.intersection(pencilSet.union(pennedSet))).pop()
                        for a in range(rowOffset, rowOffset + 3):
                            self.layout[a][y].note[val-1] = 0
                        for a in range(rowOffset2, rowOffset2 + 3):
                            self.layout[a][j].note[val-1] = 0

    # ********************************************************************************************************************
    def simpleColoringUtil(self):
        for val in range(1,10):
            self.simpleColoring(val)
    def simpleColoring(self, val):
        tempCopy = copy.deepcopy(self)
        nodesDone = []
        completedGroups = []
        for i in range(9):
            for j in range(9):
                if not tempCopy.stuck(self):
                    return
                if val not in self.layout[i][j].note or (i, j) in nodesDone:
                    continue
                fullLoop = [[(i, j)]]
                newNodes = [(i, j)]
                nodesDone += [(i, j)]
                ends = []
                
                while True:
                    tempLoop = []
                    for a in newNodes:
                        temp = self.getConnectedNodes(val, a, nodesDone)
                        tempLoop += temp
                        nodesDone += temp
                    if len(tempLoop) == 0:
                        break
                    newNodes = tempLoop
                    fullLoop += [tempLoop]
                if len(fullLoop) > 1:
                    completedGroups += [fullLoop]
                # rule 2
                for group in completedGroups:
                    color = 'yellow'
                    badColor = ''
                    colorNodes = []
                    for a in group:
                        if color == 'green':
                            color = 'yellow'
                        else:
                            color = 'green'
                        if len(a) == 1:
                            colorNodes += [(a[0], color)]
                            continue
                        for b in a:
                            colorNodes += [(b, color)]
                    if len(colorNodes) == 2:
                        continue
                    for a in colorNodes:
                        if badColor != '':
                            break
                        for b in colorNodes:
                            if b[1] != a[1] or a == b:
                                continue
                            # print(f"Comparing: {a[0]} and {b[0]}")
                            if self.inBox([a[0], b[0]]) or self.inRow([a[0], b[0]]) or self.inCol([a[0], b[0]]):
                                badColor = b[1]
                                break
                    if badColor == '':
                        continue
                    for a in colorNodes:
                        if a[1] != badColor:
                            x, y = a[0]
                            # print(f"SimpleColoring found {val} at index ({x}, {y})")
                            self.layout[i][j].setVal(val)
                if not tempCopy.stuck(self):
                    return
                # rule 4
                for group in completedGroups:
                    color = 'yellow'
                    badColor = ''
                    colorNodes = {}
                    rawNodes = []
                    endNodes = []
                    for a in group:
                        if color == 'green':
                            color = 'yellow'
                        else:
                            color = 'green'
                        if len(a) == 1:
                            temp = a[0]
                            rawNodes += [temp]
                            colorNodes[temp] = color
                            continue
                        for b in a:
                            rawNodes += [b]
                            colorNodes[b] = color
                    if len(rawNodes) == 2:
                        continue
                    for a in rawNodes:
                        if len(self.getConnectedNodes(val, a, [])) == 1:
                            endNodes += [a]
                    if len(endNodes) != 2:
                        break
                    if colorNodes[endNodes[0]] == colorNodes[endNodes[1]]:
                        break
                    node1x, node1y = endNodes[0]
                    node1Check = True
                    node2x, node2y = endNodes[1]
                    node2Check = True
                    # rule 4 sit 1
                    if not self.sameRowChute(endNodes[0], endNodes[1]) and not self.sameColChute(endNodes[0], endNodes[1]):
                        # print(f"sit1 {val}: {endNodes}")
                        for a in rawNodes:
                            if self.inBox([(node1x, node2y), a]):
                                node1Check = False
                            if self.inBox([(node2x, node1y), a]):
                                node2Check = False
                        if node1Check:
                            self.layout[node1x][node2y].note[val-1] = 0
                        if node2Check:
                            self.layout[node2x][node1y].note[val-1] = 0
                    # rule 4 sit 2 (rows)
                    elif self.sameRowChute(endNodes[0], endNodes[1]) and not self.sameColChute(endNodes[0], endNodes[1]):
                        # print(f"sit2 {val}: {endNodes}")
                        for a in range((node1y//3) * 3, ((node1y//3) * 3) + 3):
                            self.layout[node2x][a].note[val-1] = 0
                        for a in range((node2y//3) * 3, ((node2y//3) * 3) + 3):
                            self.layout[node1x][a].note[val-1] = 0
                    # rule 4 sit 3 (cols)
                    elif not self.sameRowChute(endNodes[0], endNodes[1]) and self.sameColChute(endNodes[0], endNodes[1]):
                        # print(f"sit3 {val}: {endNodes}")
                        for a in range((node1x//3) * 3, ((node1x//3) * 3) + 3):
                            self.layout[a][node2y].note[val-1] = 0
                        for a in range((node2x//3) * 3, ((node2x//3) * 3) + 3):
                            self.layout[a][node1y].note[val-1] = 0
                    if not self.stuck(tempCopy):
                        return
    def getConnectedNodes(self, val, coord, visited):
        i, j = coord
        rowOffset = (i//3) * 3
        colOffset = (j//3) * 3
        connectedNodes = []
        tempDone = []
        badBox = False
        badRow = False
        badCol = False
        for a in range(rowOffset, rowOffset + 3):
            if badBox:
                break
            for b in range(colOffset, colOffset + 3):
                if badBox:
                    break
                if (a, b) == (i, j) or (a, b) in visited:
                    continue
                if val in self.layout[a][b].note:
                    if self.singleBoxCheck([(i, j), (a, b)], {val}):
                        connectedNodes += [(a, b)]
                        tempDone += [(a,b)]
                    else:
                        badBox = True
        for b in range(9):
            if badRow:
                break
            if b == j or (i, b) in visited or (i, b) in tempDone:
                continue
            if val in self.layout[i][b].note:
                if self.singleRowCheck([(i, j), (i, b)], {val}):
                    connectedNodes += [(i, b)]
                    tempDone += [(a,b)]
                else:
                    badRow = True
        for a in range(9):
            if badCol:
                break
            if a == i or (a, j) in visited or (a, j) in tempDone:
                continue
            if val in self.layout[a][j].note:
                if self.singleColCheck([(i, j), (a, j)], {val}):
                    connectedNodes += [(a, j)]
                else:
                    badCol = True
        return connectedNodes

    def sameRowChute(self, node1, node2):
        return node1[0]//3 == node2[0]//3

    def sameColChute(self, node1, node2):
        return node1[1]//3 == node2[1]//3
    # ********************************************************************************************************************
    # y wing
    def yWing(self):
        tempCopy = copy.deepcopy(self)
        for i in range(9):
            for j in range(9):
                if self.layout[i][j].val != 0:
                    continue
                tempSet = set(self.layout[i][j].note)
                tempSet.discard(0)
                if len(tempSet) != 2:
                    continue
                colWing = set()
                rowWing = set()
                rowOffset = (i//3) * 3
                colOffset = (j//3) * 3
                # looks for candidate in column
                for row in range(9):
                    if rowOffset <= row < rowOffset + 3 or self.layout[row][j].val != 0:
                        continue
                    temp = set(self.layout[row][j].note)
                    temp.discard(0)
                    if len(temp) == 2 and len(temp.intersection(tempSet)) == 1:
                        colWing.add((row,j))
                # looks for candidate in row
                for col in range(9):
                    if colOffset <= col < (colOffset + 3) or self.layout[i][col].val != 0:
                        continue
                    temp = set(self.layout[i][col].note)
                    temp.discard(0)
                    if len(temp) == 2 and len(temp.intersection(tempSet)) == 1:
                        rowWing.add((i,col))
                if len(rowWing) > 0 and len(colWing) > 0:
                    for tempRNode in rowWing:
                        tempRowSet = set(self.layout[tempRNode[0]][tempRNode[1]].note)
                        tempRowSet.discard(0)
                        for tempCNode in colWing:
                            tempColSet = set(self.layout[tempCNode[0]][tempCNode[1]].note)
                            tempColSet.discard(0)
                            if len(tempRowSet.union(tempColSet).union(tempSet)) != 3:
                                continue
                            if self.layout[tempRNode[0]][tempRNode[1]].note != self.layout[tempCNode[0]][tempCNode[1]].note:
                                tempRowSet = set(self.layout[tempRNode[0]][tempRNode[1]].note)
                                tempRowSet.discard(0)
                                tempColSet = set(self.layout[tempCNode[0]][tempCNode[1]].note)
                                tempColSet.discard(0)
                                valToErase = tempRowSet.intersection(tempColSet)
                                if len(valToErase) != 1:
                                    continue
                                val = valToErase.pop()
                                self.layout[tempCNode[0]][tempRNode[1]].note[val-1] = 0
                                if not self.stuck(tempCopy):
                                    print(f"Y-Wing Sit 1, Root: ({i}, {j}), rowWing {tempRNode}, colWing{tempCNode}\nErasing {val} at ({tempCNode[0]}, {tempRNode[1]})")
                                    return
                if not self.stuck(tempCopy):
                    # print(f"YWing sit1 {val}:")
                    return
                if len(rowWing) > 0 and len(colWing) == 0:
                    for tempRowNode in rowWing:
                        tempRowSet = set(self.layout[tempRowNode[0]][tempRowNode[1]].note)
                        tempRowSet.discard(0)
                        targetSet = set(tempSet.union(tempRowSet)) - set(tempSet.intersection(tempRowSet))
                        for a in range(rowOffset, rowOffset + 3):
                            if a == i:
                                continue
                            for b in range(colOffset, colOffset + 3):
                                if b == j:
                                    continue
                                tempBoxSet = set(self.layout[a][b].note)
                                tempBoxSet.discard(0)
                                if tempBoxSet == targetSet:
                                    eVal = set(tempRowSet.intersection(tempBoxSet)).pop()
                                    # for eCol in range(colOffset, colOffset + 3):
                                    #     if eCol == j:
                                    #         continue
                                    self.layout[i][b].note[eVal-1] = 0
                                    for eCol in range((tempRowNode[1]//3) * 3, ((tempRowNode[1]//3) * 3) + 3):
                                        self.layout[a][eCol].note[eVal-1] = 0
                                    if not self.stuck(tempCopy):
                                        print(f"Y-Wing Sit 2.Row, Root: ({i}, {j}), rowWing: {tempRowNode}, boxNode: ({a}, {b})\nRow Erasing {eVal} at ({i}, [{colOffset} {colOffset + 1} {colOffset + 2}]) and ({a}, [{((tempRowNode[1]//3) * 3)} {((tempRowNode[1]//3) * 3) + 1} {((tempRowNode[1]//3) * 3) + 2}])")
                                        return
                                    
                elif len(colWing) > 0 and len(rowWing) == 0:
                    for tempColNode in colWing:
                        tempColSet = set(self.layout[tempColNode[0]][tempColNode[1]].note)
                        tempColSet.discard(0)
                        targetSet = set(tempSet.union(tempColSet)) - set(tempSet.intersection(tempColSet))
                        for a in range(rowOffset, rowOffset + 3):
                            if a == i:
                                continue
                            for b in range(colOffset, colOffset + 3):
                                if b == j:
                                    continue
                                tempBoxSet = set(self.layout[a][b].note)
                                tempBoxSet.discard(0)
                                if tempBoxSet == targetSet:
                                    eVal = set(tempColSet.intersection(tempBoxSet)).pop()
                                    # for eRow in range(rowOffset, rowOffset + 3):
                                    #     if eRow == i:
                                    #         continue
                                    self.layout[a][j].note[eVal-1] = 0
                                    for eRow in range((tempColNode[1]//3) * 3,((tempColNode[1]//3) * 3) + 3):
                                        self.layout[eRow][b].note[eVal-1] = 0
                                    if not self.stuck(tempCopy):
                                        print(f"Y-Wing Sit 2.Col, Root: ({i}, {j}), colWing: {tempColNode}, boxNode: ({a}, {b})\nCol Erasing {eVal} at ([{rowOffset} {rowOffset + 1} {rowOffset + 2}], {j}) and ([{((tempColNode[1]//3) * 3)} {((tempColNode[1]//3) * 3) + 1} {((tempColNode[1]//3) * 3) + 2}, {b})")
                                        return
    # ********************************************************************************************************************
    # rectangle elimination
    def rectangleElimination(self):
        tempCopy = copy.deepcopy(self)
        for i in range(9):
            for j in range(9):
                if self.layout[i][j].val != 0:
                    continue
                rowOffset = (i//3) * 3
                colOffset = (j//3) * 3
                strongNode = (i, j)
                tempSet = set(self.layout[i][j].note)
                tempSet.discard(0)
                # parses through every value in current square
                for val in tempSet:
                    # checks for strong links rows and columns at the beginning
                    rowCheck = False
                    colCheck = False
                    for row in range(9):
                        if rowOffset <= row < rowOffset + 3:
                            continue
                        if val in self.layout[row][j].note and self.singleColCheck([(i, j), (row, j)], {val}):
                            strongNode = (row, j)
                            colCheck = True
                            break
                    for col in range(9):
                        if colOffset <= col < colOffset + 3:
                            continue
                        if val in self.layout[i][col].note and self.singleRowCheck([(i, j), (i, col)], {val}):
                            strongNode = (i, col)
                            rowCheck = True
                            break
                    # continues if no strong link is found
                    if not rowCheck and not colCheck:
                        continue
                    # performs next steps only if one strong link exists
                    if rowCheck and not colCheck:
                        weakNodes = set()
                        for row in range(9):
                            if rowOffset <= row < rowOffset + 3:
                                continue
                            if val in self.layout[row][j].note:
                                weakNodes.add((row, j))
                        if len(weakNodes) == 0:
                            continue
                        for tempNode in weakNodes:
                            if self.recCheck(tempNode, strongNode, val):
                                # print(f"{val} Strong link: ({i}, {j}) & {strongNode}, WeakNode: {tempNode}")
                                # print(f"{val} at ({tempNode[0]}, {tempNode[1]}) removed")
                                self.layout[tempNode[0]][tempNode[1]].note[val-1] = 0
                                if not self.stuck(tempCopy):
                                    print(f"{val} Strong link: ({i}, {j}) & {strongNode}, WeakNode: {tempNode}")
                                    print(f"{val} at ({tempNode[0]}, {tempNode[1]}) removed")
                                    return
                    elif colCheck and not rowCheck:
                        weakNodes = set()
                        for col in range(9):
                            if colOffset <= col < colOffset + 3:
                                continue
                            if val in self.layout[i][col].note:
                                weakNodes.add((i, col))
                        if len(weakNodes) == 0:
                            continue
                        for tempNode in weakNodes:
                            if self.recCheck(strongNode, tempNode, val):
                                # print(f"{val} Strong link: ({i}, {j}) & {strongNode}, WeakNode: {tempNode}")
                                # print(f"{val} at ({tempNode[0]}, {tempNode[1]}) removed")
                                self.layout[tempNode[0]][tempNode[1]].note[val-1] = 0
                                if not self.stuck(tempCopy):
                                    print(f"{val} Strong link: ({i}, {j}) & {strongNode}, WeakNode: {tempNode}")
                                    print(f"{val} at ({tempNode[0]}, {tempNode[1]}) removed")
                                    return
                                
    def recCheck(self, rowNode, colNode, val):
        rowOffset = (rowNode[0]//3) * 3
        colOffset = (colNode[1]//3) * 3
        valCheck = False
        for row in range(rowOffset, rowOffset + 3):
            for col in range(colOffset, colOffset + 3):
                if val in self.layout[row][col].note:
                    valCheck = True
        if not valCheck:
            return False
        for row in range(rowOffset, rowOffset + 3):
            if row == rowNode[0]:
                continue
            for col in range(colOffset, colOffset + 3):
                if col == colNode[1]:
                    continue
                if val in self.layout[row][col].note:
                    return False
        return True
        
                    
    # ********************************************************************************************************************
    # sword fish works the same way as an xwing, except its for triples includes triples
    def swordfishUtil(self):
        tempCopy = copy.deepcopy(self)
        masterSet = set()
        for i in range(9):
            for j in range(9):
                masterSet = masterSet.union(set(self.layout[i][j].note))
        masterSet.discard(0)
        for val in masterSet:
            self.swordfish(val)
            if not self.stuck(tempCopy):
                return
    def swordfish(self, val):
        tempCopy = copy.deepcopy(self)
        for i in range(9):
            for j in range(9):
                if val not in self.layout[i][j].note:
                    continue
                # print(f"{val}: ({i},{j})")
                tempSet = set(self.layout[i][j].note)
                tempSet.remove(0)
                goodFlag = False
                stellarFlag = False
                t1 = [(i,j)]
                t2 = []
                t3 = []
                rows = [i]
                cols = [j]
                # first searches for doubles or triples in a row
                for col in range(9):
                    if col in cols or self.layout[i][col].val != 0:
                        continue
                    t1 = [(i,j)]
                    if len(t1) == 1 and val in self.layout[i][col].note:
                        t1 += [(i, col)]
                        cols += [col]
                        if self.singleRowCheck(t1, {val}):
                            stellarFlag = True
                            break
                    elif val in self.layout[i][col].note:
                        if self.singleRowCheck(t1 + [(i, col)], {val}):
                            t1 += [(i, col)]
                            cols += [col]
                            goodFlag = True
                            break
                if stellarFlag:
                    for row in range(9):
                        if len(t2) == 3:
                            break
                        t2 = []
                        if row in rows:
                            continue
                        if val in self.layout[row][cols[0]].note or val in self.layout[row][cols[1]].note:
                            t2 = [(row, cols[0]), (row, cols[1])]
                            for col in range(9):
                                if col in cols:
                                    continue
                                if val in self.layout[row][col].note and self.singleRowCheck(t2 + [(row, col)], {val}):
                                    cols += [col]
                                    rows += [row]
                                    t1 += [(rows[0], col)]
                                    t2 += [(row, col)]
                                    goodFlag = True
                                    break                                        
                elif goodFlag:
                    goodFlag = False
                    for row in range(9):
                        t2 = []
                        if row in rows:
                            continue
                        if val in self.layout[row][cols[0]].note or val in self.layout[row][cols[1]].note or val in self.layout[row][cols[2]].note:
                            t2 = [(row, cols[0]), (row, cols[1]), (row, cols[2])]
                            if self.singleRowCheck(t2, {val}):
                                rows += [row]
                                goodFlag = True
                                break
                if goodFlag:
                    goodFlag = False
                    for row in range(9):
                        t3 = []
                        if row in rows:
                            continue
                        if val in self.layout[row][cols[0]].note or val in self.layout[row][cols[1]].note or val in self.layout[row][cols[2]].note:
                            t3 = [(row, cols[0]), (row, cols[1]), (row, cols[2])]
                            if self.singleRowCheck(t3, {val}):
                                rows += [row]
                                goodFlag = True
                                break
                if goodFlag:
                    t1 = sorted(t1, key=lambda item: item[0])
                    t2 = sorted(t2, key=lambda item: item[0])
                    t3 = sorted(t3, key=lambda item: item[0])
                    for a in range(3):
                        self.subUpdateNotes('col', [t1[a], t2[a], t3[a]], {val}) 
                    if not tempCopy.stuck(self):
                        # print(f"T1: {t1}")
                        # print(f"T2: {t2}")
                        # print(f"T3: {t3}")
                        # print(f"Updating {val} in cols {cols[0]}, {cols[1]}, {cols[2]}")
                        return
                # *************************************************
                # searches for swordfish in columns
                t1 = [(i, j)]
                t2 = []
                t3 = []
                rows = [i]
                cols = [j]
                goodFlag = False
                stellarFlag = False
                for row in range(9):
                    if row in rows or self.layout[row][j].val != 0:
                        continue
                    if len(t1) == 1 and val in self.layout[row][j].note:
                        t1 += [(row, j)]
                        rows += [row]
                        if self.singleColCheck(t1, {val}):
                            stellarFlag = True
                            break
                    elif val in self.layout[i][col].note:
                        if self.singleColCheck(t1 + [(row, j)], {val}):
                            t1 += [(row, j)]
                            rows += [row]
                            goodFlag = True
                            break
                if stellarFlag:
                    for col in range(9):
                        if goodFlag:
                            break
                        t2 = []
                        if col in cols:
                            continue
                        if val in self.layout[rows[0]][col].note or val in self.layout[rows[1]][col].note:
                            t2 = [(rows[0], col), (rows[1], col)]
                            for row in range(9):
                                if row in rows:
                                    continue
                                if val in self.layout[row][col].note and self.singleColCheck(t2 + [(row, col)], {val}):
                                    cols += [col]
                                    rows += [row]
                                    t1 += [(row, cols[0])]
                                    t2 += [(row, col)]
                                    goodFlag = True
                                    break       
                elif goodFlag:
                    goodFlag = False
                    for col in range(9):
                        t2 = []
                        if col in cols:
                            continue
                        if val in self.layout[rows[0]][col].note or val in self.layout[rows[1]][col].note or val in self.layout[rows[2]][col].note:
                            t2 = [(rows[0], col), (rows[1], col), (rows[2], col)]
                            if self.singleColCheck(t2, {val}):
                                cols += [col]
                                goodFlag = True
                                break
                if goodFlag:
                    goodFlag = False
                    for col in range(9):
                        t3 = []
                        if col in cols:
                            continue
                        if val in self.layout[rows[0]][col].note or val in self.layout[rows[1]][col].note or val in self.layout[rows[2]][col].note:
                            t3 = [(rows[0], col), (rows[1], col), (rows[2], col)]
                            if self.singleColCheck(t3, {val}):
                                cols += [col]
                                goodFlag = True
                                break
                if goodFlag:
                    t1 = sorted(t1, key=lambda item: item[1])
                    t2 = sorted(t2, key=lambda item: item[1])
                    t3 = sorted(t3, key=lambda item: item[1])
                    for a in range(3):
                        self.subUpdateNotes('row', [t1[a], t2[a], t3[a]], {val})
                    if not tempCopy.stuck(self):
                        # print(f"T1: {t1}")
                        # print(f"T2: {t2}")
                        # print(f"T3: {t3}")
                        # print(f"Updating {val} in rows {rows[0]}, {rows[1]}, {rows[2]}")
                        return

    # ********************************************************************************************************************
    # xyz-wing
    def xyzWing(self):
        tempCopy = copy.deepcopy(self)
        for i in range(9):
            for j in range(9):
                if self.layout[i][j].val != 0:
                    continue
                tempSet = set(self.layout[i][j].note)
                tempSet.discard(0)
                if len(tempSet) != 3:
                    continue
                colWing = set()
                rowWing = set()
                rowOffset = (i//3) * 3
                colOffset = (j//3) * 3
                # looks for candidate in column
                for row in range(9):
                    if row == i or self.layout[row][j].val != 0:
                        continue
                    temp = set(self.layout[row][j].note)
                    temp.discard(0)
                    if len(temp) == 2 and len(temp.intersection(tempSet)) == 2:
                        colWing.add((row,j))
                # looks for candidate in row
                for col in range(9):
                    if col == j or self.layout[i][col].val != 0:
                        continue
                    temp = set(self.layout[i][col].note)
                    temp.discard(0)
                    if len(temp) == 2 and len(temp.intersection(tempSet)) == 2:
                        rowWing.add((i,col))
                if len(rowWing) > 0 and len(colWing) > 0:
                    for tempRNode in rowWing:
                        tempRowSet = set(self.layout[tempRNode[0]][tempRNode[1]].note)
                        tempRowSet.discard(0)
                        for tempCNode in colWing:
                            tempColSet = set(self.layout[tempCNode[0]][tempCNode[1]].note)
                            tempColSet.discard(0)
                            if len(tempRowSet.union(tempColSet).union(tempSet)) == 3 and self.layout[tempRNode[0]][tempRNode[1]].note != self.layout[tempCNode[0]][tempCNode[1]].note:
                                tempRowSet = set(self.layout[tempRNode[0]][tempRNode[1]].note)
                                tempRowSet.discard(0)
                                tempColSet = set(self.layout[tempCNode[0]][tempCNode[1]].note)
                                tempColSet.discard(0)
                                valToErase = tempRowSet.intersection(tempColSet).intersection(tempSet)
                                if len(valToErase) != 1:
                                    continue
                                val = valToErase.pop()
                                if self.inBox([(i, j), tempRNode]) and not self.inBox([(i, j), tempCNode]):
                                    
                                    for eRow in range(rowOffset, rowOffset + 3):
                                        if eRow == i:
                                            continue
                                        self.layout[eRow][j].note[val-1] = 0
                                    if not self.stuck(tempCopy):
                                        print(f"XYZ-Wing Sit 1 Col, Root: ({i}, {j}), rowWing {tempRNode}, colWing{tempCNode}\nErasing {val} at ([{rowOffset} {rowOffset+1} {rowOffset+2}], {j})")
                                elif self.inBox([(i, j), tempCNode]) and not self.inBox([(i, j), tempRNode]):
                                    for eCol in range(colOffset, colOffset + 3):
                                        if eCol == j:
                                            continue 
                                        self.layout[i][eCol].note[val-1] = 0
                                    if not self.stuck(tempCopy):
                                        print(f"XYZ-Wing Sit 1 Row, Root: ({i}, {j}), rowWing {tempRNode}, colWing{tempCNode}\nErasing {val} at ( {i}), [{colOffset} {colOffset+1} {colOffset+2}]")
                                if not self.stuck(tempCopy):
                                    return
                if not self.stuck(tempCopy):
                    # print(f"YWing sit1 {val}:")
                    return
                if len(rowWing) > 0 and len(colWing) == 0:
                    for tempRowNode in rowWing:
                        tempRowSet = set(self.layout[tempRowNode[0]][tempRowNode[1]].note)
                        tempRowSet.discard(0)
                        for a in range(rowOffset, rowOffset + 3):
                            if a == i:
                                continue
                            for b in range(colOffset, colOffset + 3):
                                if b == j:
                                    continue
                                tempBoxSet = set(self.layout[a][b].note)
                                tempBoxSet.discard(0)
                                if len(tempBoxSet) == 2 and len(tempBoxSet.union(tempRowSet).union(tempSet)) == 3 and tempBoxSet != tempRowSet:
                                    eVal = set(tempRowSet.intersection(tempBoxSet).intersection(tempSet)).pop()
                                    for eCol in range(colOffset, colOffset + 3):
                                        if eCol == j:
                                            continue
                                        self.layout[i][eCol].note[eVal-1] = 0
                                    if not self.stuck(tempCopy):
                                        print(f"XYZ-Wing Sit 2 Row, Root: ({i}, {j}), rowWing {tempRowNode}, boxWing{(a, b)}")
                                        return
                                    
                elif len(colWing) > 0 and len(rowWing) == 0:
                    for tempColNode in colWing:
                        tempColSet = set(self.layout[tempColNode[0]][tempColNode[1]].note)
                        tempColSet.discard(0)
                        for a in range(rowOffset, rowOffset + 3):
                            if a == i:
                                continue
                            for b in range(colOffset, colOffset + 3):
                                if b == j:
                                    continue
                                tempBoxSet = set(self.layout[a][b].note)
                                tempBoxSet.discard(0)
                                if len(tempBoxSet) == 2 and len(tempBoxSet.union(tempColSet).union(tempSet)) == 3 and tempBoxSet != tempColSet:
                                    eVal = set(tempColSet.intersection(tempBoxSet)).pop()
                                    for eRow in range(rowOffset,rowOffset + 3):
                                        if eRow == i:
                                            continue
                                        self.layout[eRow][j].note[eVal-1] = 0
                                    if not self.stuck(tempCopy):
                                        print(f"XYZ-Wing Sit 2 Row, Root: ({i}, {j}), tempColNode {tempColNode}, boxWing{(a, b)}")
                                        return
    # ********************************************************************************************************************
    # possibly scrap after xyWing?
    def bug(self):
        bugFound = False
        for i in range(9):
            if bugFound:
                break
            for j in range(9):
                if bugFound:
                    break
                if self.layout[i][j].val != 0:
                    continue
                tempSet = set(self.layout[i][j].note)
                tempSet.discard(0)
                if len(tempSet) > 3:
                    return
                if len(tempSet) == 3:
                    bugx = i
                    bugy = j
                    bugFound = True
        if bugFound:
            for i in range(9):
                for j in range(9):
                    if self.layout[i][j].val != 0 or (i, j) == (bugx, bugy):
                        continue
                    temp = set(self.layout[i][j].note)
                    temp.discard(0)
                    if len(temp) != 2:
                        return
            valCount = {}
            for val in tempSet:
                valCount[val] = (val, 0)
                for row in range(9):
                    if valCount[val][0] in self.layout[row][bugy].note:
                        tempVal = valCount[val][1] + 1
                        valCount[val] = (val, tempVal)
                for col in range(9):
                    if valCount[val][0] in self.layout[bugx][col].note:
                        tempVal = valCount[val][1] + 1
                        valCount[val] = (val, tempVal)
                for row in range((bugx//3) * 3,((bugx//3) * 3) + 3):
                    for col in range((bugy//3) * 3,((bugy//3) * 3) + 3):
                        if valCount[val][0] in self.layout[row][col].note:
                            tempVal = valCount[val][1] + 1
                            valCount[val] = (val, tempVal)
            for x in valCount:
                print(valCount[x])
                if valCount[x][1] == 9:
                    print(f"BUG found val {valCount[x][0]} at ({bugx}, {bugy})")
                    self.layout[bugx][bugy].setVal(valCount[x][0])
                    
    # ********************************************************************************************************************
    # bad rectangle, scrapped for diabolical strategy "Unique Rectangles"
    def avoidableRectangles(self):
        tempCopy = copy.deepcopy(self)
        for i in range(9):
            for j in range(9):
                if not tempCopy.stuck(self):
                    return
                if self.layout[i][j].val == 0:
                    continue
                # tempSet = set(self.layout[i][j].note)
                # tempSet.discard(0)
                # first it searches for a row pairs of penned values
                for tempCol in range((j//3) * 3, ((j//3) * 3) + 3):
                    if tempCol == j or self.layout[i][tempCol].val == 0:
                        continue
                    for tempRow in range(9):
                        if (i//3) * 3 <= tempRow == ((i//3) * 3) + 3 or not (self.layout[tempRow][j].val == 0 ^ self.layout[tempRow][tempCol].val == 0):
                            continue
                        if self.layout[i][tempCol].val == self.layout[tempRow][j].val and self.layout[tempRow][tempCol].val == 0:
                            self.layout[tempRow][tempCol].note[self.layout[i][j].val - 1] = 0
                        elif self.layout[i][j].val == self.layout[tempRow][tempCol].val and self.layout[tempRow][j].val == 0:
                            self.layout[tempRow][j].note[self.layout[i][tempCol].val - 1] = 0
                        if not tempCopy.stuck(self):
                            return
                # searches for col pairs of penned values
                for tempRow in range((i//3) * 3,((i//3) * 3) + 3):
                    if tempRow == i or self.layout[tempRow][j].val == 0:
                        continue
                    for tempCol in range(9):
                        if (j//3) * 3 <= tempCol < ((j//3) * 3) + 3 or not (self.layout[i][tempCol].val == 0 ^ self.layout[tempRow][tempCol].val == 0):
                            continue
                        if self.layout[tempRow][j].val == self.layout[i][tempCol].val and self.layout[tempRow][tempCol].val == 0:
                            self.layout[tempRow][tempCol].note[self.layout[i][j].val - 1] = 0
                        elif self.layout[i][j].val == self.layout[tempRow][tempCol].val and self.layout[i][tempCol].val == 0:
                            self.layout[i][tempCol].note[self.layout[tempRow][j].val - 1] = 0
                        if not tempCopy.stuck(self):
                            return
        for i in range(9):
            for j in range(9):
                if j % 3 == 0:
                    continue
                if self.layout[i][j].val == 0 or self.layout[i][j + 1].val == 0 or self.layout[i][j + 2].val == 0:
                    continue
                goodCheck = False
                eCheck = False
                vals = set()
                for tempCol in range(3):
                    vals.add(self.layout[i][j + tempCol].val)
                for tempRow in range(9):
                    if i == tempRow:
                        continue
                    tempVals = set()
                    tempSets = set()
                    for tempCol in range(3):
                        if self.layout[tempRow][j + tempCol].val != 0:
                            tempVals.add(self.layout[tempRow][j + tempCol].val)
                        else:
                            tempSets = tempSets.union(set(self.layout[tempRow][j + tempCol].note))
                            eCoord = (tempRow, j + tempCol)
                    tempSets.discard(0)
                    if not goodCheck and len(tempVals) == 2 and len(tempVals.intersection(tempSets)) == 1:
                        eCoord1 = eCoord
                        goodCheck == True
                    elif goodCheck and len(tempVals) == 2 and len(tempVals.intersection(tempSets)) == 1:
                        eCoord
                    
        # # searches cols for row triples
        # for i in range(9):
        #     for colChute in range(9):
        #         if colChute % 3 != 0:
        #             continue
        #         tempVals = set()
        #         tempSets = set()
        #         for tempCol in range(colChute, colChute + 3):
        #             if self.layout[i][tempCol].val == 0:
        #                 temp = set(self.layout[i][tempCol].note)
        #                 temp.discard(0)
        #                 tempSets = tempSets.union(temp)
        #             else:
        #                 tempVals.add(self.layout[i][tempCol].val)
        #         if len(tempVals) == 3:
                    
        # for rowChute in range(3):
        #     tempVals = set()
        #     tempSets = set()
    # ********************************************************************************************************************
    # *************Possibly redundant*************
    # skyscraper utilization
    def skyscraperUtil(self):
        tempCopy = copy.deepcopy(self)
        for val in range(1,10):
            self.skyscraper(val)
            if not tempCopy.stuck(self):
                break
    
    def skyscraper(self, val):
        pairsDone = []
        currVal = {val}
        tempCopy = copy.deepcopy(self)
        for i in range(9):
            if not tempCopy.stuck(self):
                break
            for j in range(9):
                if not tempCopy.stuck(self):
                    break
                if self.layout[i][j].val != 0:
                    continue
                rowSit = False
                colSit = False
                pair1 = [(i,j)]
                pair2 = []
                # searches rows for set pair of values (only to the right of the current column)
                for col in range(j + 1, 9):
                    if col == j or self.layout[i][col].val != 0:
                        continue
                    if val in self.layout[i][col].note and self.singleRowCheck([(i,j),(i,col)], currVal):
                        pair1 += [(i,col)]
                        j2 = col
                        break
                # pair found
                if len(pair1) == 2:
                    for row in range(9):
                        if (i//3) * 3 <= row < ((i//3) * 3) + 3:
                            continue
                        # finds a common note in the first coordinates column
                        if val in self.layout[row][j].note and val not in self.layout[row][j2].note:
                            pair2 = [(row,j)]
                            eColumn1 = j2
                            # only searches to the right of the second coordinates column value
                            for col in range(j2 + 1,((j2//3) * 3) + 3):
                                if self.layout[row][col].val != 0:
                                    continue
                                if val in self.layout[row][col].note and self.singleRowCheck([(row,j),(row,col)], currVal):
                                    pair2 += [(row,col)]
                                    arry1 = self.getArry((i//3)*3)
                                    arry2 = self.getArry((row//3)*3)
                                    eColumn2 = col
                                    rowSit = True
                                    break
                        elif val in self.layout[row][j2].note and val not in self.layout[row][j].note:
                            pair2 = [(row,j2)]
                            eColumn1 = j
                            for col in range((j//3)*3,j):
                                if self.layout[row][col].val != 0:
                                    continue
                                if val in self.layout[row][col].note and self.singleRowCheck([(row,j2),(row,col)], currVal):
                                    pair2 += [(row,col)]
                                    arry1 = self.getArry((i//3)*3)
                                    arry2 = self.getArry((row//3)*3)
                                    eColumn2 = col
                                    rowSit = True
                                    break
                        if rowSit:
                            break
                    if rowSit and len(pair2) == 2 and (set(pair1) not in pairsDone and set(pair2) not in pairsDone):
                        pairsDone += [set(pair1), set(pair2)]
                        # print(f"Row Pair1 {val}: {pair1}")
                        # print(f"Row Pair2 {val}: {pair2}")
                        # print(f"ColErase1 = ({arry1},{eColumn1})")
                        # print(f"ColErase2 = ({arry2},{eColumn2})")
                        for a in range(3):
                            self.layout[arry1[a]][eColumn2].note[val-1] = 0
                            self.layout[arry2[a]][eColumn1].note[val-1] = 0
                        continue
                pair1 = [(i,j)]
                pair2 = []
                for row in range(i + 1,9):
                    if self.layout[row][j].val != 0:
                        continue
                    if val in self.layout[row][j].note and self.singleColCheck([(i,j),(row,j)], currVal):
                        pair1 += [(row,j)]
                        i2 = row
                        break
                if len(pair1) == 2: 
                    # searches for the note existing in a common row or column
                    for col in range(9):
                        if (j//3) * 3 <= col < ((j//3) * 3) + 3:
                            continue
                        pair2 = []
                        # separates the columns being search, because if both values have the note it is an xwing scenario
                        # if common value with (i,j) is found
                        if val in self.layout[i][col].note and val not in self.layout[i2][col].note:
                            pair2 += [(i,col)]
                            eRow1 = i2
                            for row in range(i2 + 1, ((i2//3) * 3) + 3):
                                if self.layout[row][col].val != 0:
                                    continue
                                if val in self.layout[row][col].note and self.singleColCheck([(i,col),(row,col)], currVal):
                                    pair2 += [(row,col)]
                                    eRow2 = row
                                    arry1 = self.getArry((j//3)*3)
                                    arry2 = self.getArry((col//3)*3)
                                    colSit = True
                                    break
                        if val in self.layout[i2][col].note and val not in self.layout[i][col].note:
                            pair2 += [(i2,col)]
                            eRow1 = i
                            for row in range((i//3) * 3, i):
                                if self.layout[row][col].val != 0:
                                    continue
                                if val in self.layout[row][col].note and self.singleColCheck([(i2,col),(row,col)], currVal):
                                    pair2 += [(row,col)]
                                    eRow2 = row
                                    arry1 = self.getArry((j//3)*3)
                                    arry2 = self.getArry((col//3)*3)
                                    colSit = True
                                    break
                        if colSit:
                            break
                    if colSit and len(pair2) == 2 and (set(pair1) not in pairsDone and set(pair2) not in pairsDone):
                        pairsDone += [set(pair1), set(pair2)]
                        # print(f"Col Pair1 {val}: {pair1}")
                        # print(f"Col Pair2 {val}: {pair2}")
                        # print(f"RowErase1 = ({eRow1},{arry2})")
                        # print(f"RowErase2 = ({eRow2},{arry1})")
                        for a in range(3):
                            self.layout[eRow1][arry2[a]].note[val-1] = 0
                            self.layout[eRow2][arry1[a]].note[val-1] = 0
                        continue
                    
    def getArry(self, lowerBound):
        x = []
        for a in range(lowerBound, lowerBound + 3):
            x += [a]
        return x
    def samechute(self, x, y):
        return (x//3)==(y//3)
        
    # ********************************************************************************************************************
    # *************Possibly redundant*************
    def twoStringKiteUtil(self):
        temp = copy.deepcopy(self)
        for val in range(1,10):
            self.twoStringKite(val)
            if not self.stuck(temp):
                break
    # finds the bad note node first, then it finds the following pairs
    def twoStringKite(self, val):
        currVal = {val}
        pairsDone = []
        tempCopy = copy.deepcopy(self)
        for i in range(8):
            if not self.stuck(tempCopy):
                break
            for j in range(8):
                if not self.stuck(tempCopy):
                    break
                currCol = []
                currRow = []
                goodRow = []
                goodCol = []
                if val not in self.layout[i][j].note:
                    continue
                # finds cooresponding row pairs
                for row in range(9):
                    if ((i//3) * 3) <= row < (((i//3) * 3) + 3) or val not in self.layout[row][j].note:
                        continue
                    for col in range(9):
                        if ((j//3) * 3) <= col < (((j//3) * 3) + 3):
                            continue
                        if val in self.layout[row][col].note and self.singleRowCheck([(row, j), (row, col)], currVal):
                            currRow += [(row, j), (row, col)]
                if len(currRow) == 0:
                    continue
                # finds cooresponding column pairs 
                for col in range(9):
                    if ((j//3) * 3) <= col < (((j//3) * 3) + 3) or val not in self.layout[i][col].note:
                        continue
                    for row in range(9):
                        if ((i//3) * 3) <= col < (((i//3) * 3) + 3):
                            continue
                        if val in self.layout[row][col].note and self.singleColCheck([(i, col),(row, col)], currVal):
                            currCol += [(i, col),(row, col)]
                if len(currCol) == 0:
                    continue
                if len(currRow) == 2 and len(currCol) == 2 and self.sameSquare(currRow[1],currCol[1]):
                    print(currRow)
                    self.layout[i][j].note[val-1] = 0

    def sameSquare(self, idx1, idx2):
        return idx1[0]//3 == idx2[0]//3 and idx1[1]//3 == idx2[1]//3

    # ********************************************************************************************************************
    # ***********************************************DIABOLICAL STRATEGIES************************************************
    # ********************************************************************************************************************
    # seems to be a marriage of swordfish and Simple Coloring 
    def xCyclesUtil(self):
        tempCopy = copy.deepcopy(self)
        valsLeft = set()
        for i in range(9):
            for j in range(9):
                tempSet = self.getSet((i, j))
                valsLeft = valsLeft.union(tempSet)
        for val in valsLeft:
            # print(f"Current val {val}")
            self.xCycles(val)
            if not self.stuck(tempCopy):
                return

    def xCycles(self, val):
        tempCopy = copy.deepcopy(self)
        doneCycles = set()
        for i in range(9):
            for j in range(9):
                if not self.stuck(tempCopy):
                    return
                if val not in self.layout[i][j].note:
                    continue
                currentCycle = [(i, j)]
                cycles = self.getCycle1(currentCycle, val)
                if cycles is not None:
                    for cycle in cycles:
                        if set(cycle) not in doneCycles:
                            doneCycles = doneCycles.union(set(cycle))
                            for x in range(0, len(cycle)-1):
                                miniList = [cycle[x], cycle[x+1]]
                                if self.inRow(miniList):
                                    self.subUpdateNotes('row', miniList, {val})
                                elif self.inCol(miniList):
                                    self.subUpdateNotes('col', miniList, {val})
                                elif self.inBox(miniList):
                                    self.subUpdateNotes('box', miniList, {val})
                            if not self.stuck(tempCopy):
                                print("Nice Loops Rule 1")
                                return
                cycles = self.getCycle2(currentCycle, val)
                if cycles is not None:
                    for cycle in cycles:
                        if set(cycle) not in doneCycles:
                            doneCycles = doneCycles.union(set(cycle))
                            self.layout[i][j].setVal(val)
                            if not self.stuck(tempCopy):
                                print(f"Nice Loops Rule 2 set {val} at {(i, j)}")
                                return
                cycles = self.getCycle3(currentCycle, val)
                if cycles is not None:
                    for cycle in cycles:
                        if set(cycle) not in doneCycles:
                            doneCycles = doneCycles.union(set(cycle))
                            eNode = cycle[len(cycle)-1]
                            self.layout[eNode[0]][eNode[1]].note[val - 1] = 0 
                            if not self.stuck(tempCopy):
                                print(f"Nice Loops Rule 3 removed {val} at {(eNode[0], eNode[1])}")
                                return
                
    def getCycle1(self, coords, val, allCycles=None, visited=None):
        if allCycles is None:
            allCycles = []
        if visited is None:
            visited = set(coords)
        current = coords[-1]
        strongFuncs = [self.getStrongRow, self.getStrongCol, self.getStrongBox]
        for func in strongFuncs:
            weakCandidates = []
            strongNode = func(current, val)
            if strongNode == 0 or strongNode in visited:
                continue
            match func:
                case self.getStrongRow:
                    weakFuncs = [self.getWeakCol, self.getWeakBox]
                case self.getStrongCol:
                    weakFuncs = [self.getWeakRow, self.getWeakBox]
                case self.getStrongBox:
                    weakFuncs = [self.getWeakRow, self.getWeakCol]
                case _:
                    continue
            for weakFunc in weakFuncs:
                weakCandidates += weakFunc(strongNode, val)
            for weakNode in weakCandidates:
                if weakNode == coords[0]:
                    # print(f"yeah baby 1 {coords + [strongNode, weakNode]}")
                    allCycles.append(coords + [strongNode, weakNode])
                    continue
                elif weakNode not in visited:
                    self.getCycle1(coords + [strongNode, weakNode], val, allCycles, visited | {strongNode, weakNode})
        return allCycles

    def getCycle2(self, coords, val, allCycles=None, visited=None):
        if allCycles is None:
            allCycles = []
        if visited is None:
            visited = set(coords)
        current = coords[len(coords) - 1]
        strongFuncs = [self.getStrongRow, self.getStrongCol, self.getStrongBox]
        # print(f"Exploring from {current} with visited={visited}")
        for func in strongFuncs:
            weakCandidates = []
            strongNode = func(current, val)
            if strongNode == coords[0]:
                # print(f"yeah baby 2 {coords + [strongNode]}")
                allCycles.append(coords + [strongNode])
                continue
            if strongNode == 0 or strongNode in visited:
                continue
            match func:
                case self.getStrongRow:
                    weakFuncs = [self.getWeakCol, self.getWeakBox]
                case self.getStrongCol:
                    weakFuncs = [self.getWeakRow, self.getWeakBox]
                case self.getStrongBox:
                    weakFuncs = [self.getWeakRow, self.getWeakCol]
                case _:
                    continue
            for weakFunc in weakFuncs:
                weakCandidates += weakFunc(strongNode, val)
            for weakNode in weakCandidates:
                if weakNode not in visited:
                    self.getCycle2(coords + [strongNode, weakNode], val, allCycles, visited | {strongNode, weakNode})
        return allCycles
        
    def getCycle3(self, coords, val, allCycles=None, visited=None):
        if allCycles is None:
            allCycles = []
        if visited is None:
            visited = set(coords)
        current = coords[len(coords) - 1]
        strongFuncs = [self.getStrongRow, self.getStrongCol, self.getStrongBox]
        firstStrongFunc = 0
        if len(coords) > 1:
            if self.inRow([coords[0], coords[1]]):
                firstStrongFunc = self.getStrongRow
            elif self.inCol([coords[0], coords[1]]):
                firstStrongFunc = self.getStrongCol
            elif self.inBox([coords[0], coords[1]]):
                firstStrongFunc = self.getStrongBox
            match firstStrongFunc:
                case self.getStrongRow:
                    strongNode = self.getStrongRow(coords[0], val)
                    subWeakFuncs = [self.getWeakCol, self.getWeakBox]
                case self.getStrongCol:
                    strongNode = self.getStrongCol(coords[0], val)
                    subWeakFuncs = [self.getWeakRow, self.getWeakBox]
                case self.getStrongBox:
                    strongNode = self.getStrongBox(coords[0], val)
                    subWeakFuncs = [self.getWeakRow, self.getWeakCol]
                case _:
                    strongNode = 0
                    subWeakFuncs = 0
            firstCandidates = []
            for weakFunc in subWeakFuncs:
                firstCandidates += weakFunc(coords[0], val)
        for func in strongFuncs:
            weakCandidates = []
            strongNode = func(current, val)
            if strongNode == 0 or strongNode in visited:
                continue
            match func:
                case self.getStrongRow:
                    weakFuncs = [self.getWeakCol, self.getWeakBox]
                case self.getStrongCol:
                    weakFuncs = [self.getWeakRow, self.getWeakBox]
                case self.getStrongBox:
                    weakFuncs = [self.getWeakRow, self.getWeakCol]
                case _:
                    continue
            for weakFunc in weakFuncs:
                weakCandidates += weakFunc(strongNode, val)
            for weakNode in weakCandidates:
                if firstStrongFunc != 0 and weakNode in firstCandidates:
                    # print(f"yeah baby 3 {coords + [strongNode, weakNode]}")
                    allCycles.append(coords + [strongNode, weakNode])
                    continue
                elif weakNode not in visited:
                    self.getCycle3(coords + [strongNode, weakNode], val, allCycles, visited | {strongNode, weakNode})
        return allCycles
    
    def getStrongRow(self, coords,val):
        connections = []
        i, j = coords
        colOffset = (j//3) * 3
        for col in range(9):
            if colOffset <= col < colOffset + 3 or val not in self.layout[i][col].note:
                continue
            if self.singleRowCheck([(i, j), (i, col)], {val}):
                return (i, col)
        return 0
    def getStrongCol(self, coords, val):
        connections = []
        i, j = coords
        rowOffset = (i//3) * 3
        for row in range(9):
            if rowOffset <= row < rowOffset + 3 or val not in self.layout[row][j].note:
                continue
            if self.singleColCheck([(i, j), (row, j)], {val}):
                return (row, j)
        return 0
    def getStrongBox(self, coords, val):
        connections = []
        i, j = coords
        rowOffset = (i//3) * 3
        colOffset = (j//3) * 3
        for row in range(rowOffset, rowOffset + 3):
            if row == i:
                continue
            for col in range(colOffset, colOffset + 3):
                if col == j or val not in self.layout[row][col].note:
                    continue
                if self.singleBoxCheck([(i, j), (row, col)], {val}):
                    return(row, col)
        return 0
    def getWeakRow(self, coords, val):
        newNodes = []
        i, j = coords
        rowOffset = (i//3) * 3
        colOffset = (j//3) * 3
        for col in range(9):
            if colOffset <= col < colOffset + 3 or val not in self.layout[i][col].note:
                continue
            newNodes += [(i, col)]
        return newNodes
    def getWeakCol(self, coords, val):
        newNodes = []
        i, j = coords
        rowOffset = (i//3) * 3
        colOffset = (j//3) * 3
        for row in range(9):
            if rowOffset <= row < rowOffset + 3 or val not in self.layout[row][j].note:
                continue
            newNodes += [(row, j)]
        return newNodes
    def getWeakBox(self, coords, val):
        newNodes = []
        i, j = coords
        rowOffset = (i//3) * 3
        colOffset = (j//3) * 3
        for row in range(rowOffset, rowOffset + 3):
            if row == i:
                continue
            for col in range(colOffset, colOffset + 3):
                if col == j or val not in self.layout[row][col].note:
                    continue    
                newNodes += [(row, col)]
        return newNodes
    def getSet(self, coord):
        tempSet = set(self.layout[coord[0]][coord[1]].note)
        tempSet.discard(0)
        return tempSet
    # ********************************************************************************************************************
    # 3D Medusa
    def medusa3DUtil(self):
        tempCopy = copy.deepcopy(self)
        remaining = set()
        for i in range(9):
            for j in range(9):
                tempSet = self.getSet((i, j))
                remaining = remaining.union(tempSet)
        remaining.discard(0)
        remaining = sorted(remaining)
        print(remaining)
        for val in remaining:
            print("currently on: ", val)
            self.medusa3D(val)
            if not self.stuck(tempCopy):
                return

    # 3D medusa expands on simple coloring but it incorporates other values into its net
    def medusa3D(self, val):
        tempCopy = copy.deepcopy(self)
        nodesDone = []
        completedGroups = []
        # iterates through whole puzzle
        for i in range(9):
            for j in range(9):
                tempSet = set(self.layout[i][j].note)
                tempSet.discard(0)
                if self.locked[i][j] or (i, j, val, 'yellow') in nodesDone or (i, j, val, 'green') in nodesDone or val not in self.layout[i][j].note:
                    continue
                currentVals = val
                firstNode = (i, j, val, 'green')
                fullLoop = [[firstNode]]
                newNodes = [firstNode]
                while True:
                    tempLoop = []
                    for currentNode in newNodes:
                        temp = self.getConnectedMedusaNodes(currentNode, nodesDone)
                        nodesDone += [currentNode]
                        tempLoop += temp
                        nodesDone += temp
                    # loop breaks when no more connecitons are found
                    if len(tempLoop) == 0:
                        break
                    newNodes = tempLoop
                    fullLoop += [tempLoop]
                if len(fullLoop) > 1:
                    completedGroups += [fullLoop]
        valsDone = set()
        # iterates through each group found individually
        for group in completedGroups:
            normalized = []
            pairedNodes = []
            # normalizes current group into 1D array
            for subGroup in group:
                for node in subGroup:
                    normalized += [node]
                    valsDone.add(node[2])
                    print(node)
            print()
            # rule 1 states that if two of the same colors are in the same location, then you remove all of that color
            for a in range(len(normalized)):
                row1, col1, val1, color1 = normalized[a]
                for b in range(a + 1, len(normalized)):
                    row2, col2, val2, color2 = normalized[b]
                    if color1 == color2 and row1 == row2 and col1 == col2:
                        for node in normalized:
                            row, col, eVal, color = node
                            if color == color1:
                                self.layout[row][col].note[eVal-1] = 0
                        if not self.stuck(tempCopy):
                            print("3D Medusa Rule 1")
                            return
            # rule 2 states that if two of the same val of the same color are found in the same row, column, or box, then none of that color are true
            for a in range(len(normalized)):
                row1, col1, val1, color1 = normalized[a]
                for b in range(a + 1, len(normalized)):
                    row2, col2, val2, color2 = normalized[b]
                    if color1 == color2 and val1 == val2 and (self.inRow([(row1, col1), (row2, col2)]) or self.inCol([(row1, col1), (row2, col2)]) or self.inBox([(row1, col1), (row2, col2)])):
                        for node in normalized:
                            row, col, eVal, color = node
                            if color == color1:
                                self.layout[row][col].note[eVal-1] = 0
                        if not self.stuck(tempCopy):
                            print("3D Medusa Rule 2")
                            return
            # rule 3 is funky, if two different colors are found in the same node, then all uncolored notes in that node can be removed
            for a in range(len(normalized)):
                row1, col1, val1, color1 = normalized[a]
                for b in range(a + 1, len(normalized)):
                    if normalized[a] == normalized[b]:
                        continue
                    row2, col2, val2, color2 = normalized[b]
                    if row1 == row2 and col1 == col2 and color1 != color2 and len(self.getConnectedMedusaNodes(normalized[a], [])) > 0 and len(self.getConnectedMedusaNodes(normalized[b], [])) > 0:
                        tempSet = set(self.layout[row1][col1].note)
                        tempSet.discard(0)
                        if len(tempSet) == 2:
                            continue
                        for eVal in tempSet:
                            if eVal == val1 or eVal == val2:
                                continue
                            self.layout[row1][col1].note[eVal-1] = 0
                        if not self.stuck(tempCopy):
                            print("3D Medusa Rule 3")
                            return
            # rule 4 is for off-chain note removal
            # if a node shares a row, col, or box with 2 separate nodes that have the same val with different colors colored nodes then that value can be discarded from that node's notes
            for row in range(9):
                for col in range(9):
                    if self.locked[row][col]:
                        continue
                    rowOffset = (row//3) * 3
                    colOffset = (col//3) * 3
                    for tempVal in valsDone:
                        if tempVal not in self.layout[row][col].note or (row, col, tempVal, 'green') in normalized or (row, col, tempVal, 'yellow') in normalized:
                            continue
                        rowColor = ''
                        colColor = ''
                        boxColor = ''
                        for tempCol in range(9):
                            if (row, tempCol, tempVal, 'green') in normalized:
                                rowColor = 'green'
                                break
                            elif (row, tempCol, tempVal, 'yellow') in normalized:
                                rowColor = 'yellow'
                                break
                        for tempRow in range(9):
                            if (tempRow, col, tempVal, 'green') in normalized:
                                colColor = 'green'
                                break
                            elif (tempRow, col, tempVal, 'yellow') in normalized:
                                colColor = 'yellow'
                                break
                        for tempRow in range(rowOffset, rowOffset + 3):
                            if boxColor != '':
                                break
                            for tempCol in range(colOffset, colOffset + 3):
                                if (tempRow, tempCol, tempVal, 'green') in normalized: 
                                    boxColor = 'green'
                                    break
                                elif (tempRow, tempCol, tempVal, 'yellow') in normalized: 
                                    boxColor = 'yellow'
                                    break
                        colorSets = [rowColor, colColor, boxColor]
                        colorsPresent = [c for c in colorSets if c]
                        if len(colorsPresent) >= 2 and len(set(colorsPresent)) > 1:
                            print(f"Removed {tempVal} from {(row, col)}")
                            self.layout[row][col].note[tempVal - 1] = 0
            if not self.stuck(tempCopy):
                print("3D Medusa Rule 4")
                return
            # rule 5 regards the non-colored notes in colored nodes
            # if a non-colored note in a node is in a box & row or box & col with a node that has a that val which has a different color than the colored note in that cell, then the non-colored node can be discarded
            rule5Done = set()
            for a in range(len(normalized)):
                row1, col1, val1, color1 = normalized[a]
                tempSet = set(self.layout[row1][col1].note)
                tempSet.discard(0)
                for (row2, col2, val2, color2) in normalized:
                    if row1 == row2 and col1 == col2 and val2 in tempSet:
                        tempSet.discard(val2)
                if not tempSet:
                    continue
                for b in range(a + 1, len(normalized)):
                    row2, col2, val2, color2 = normalized[b]
                    if row1 == row2 and col1 == col2:
                        continue
                    if color1 == color2:
                        continue
                    if not self.inBox([(row1, col1),(row2, col2)]):
                        continue
                    rowShare = self.inRow([(row1, col1),(row2, col2)])
                    colShare = self.inCol([(row1, col1),(row2, col2)])
                    if not (rowShare or colShare):
                        continue
                    for tempVal in tempSet:
                        key = (row1, col1, tempVal)
                        if key in rule5Done or tempVal != val2:
                            continue
                        print(f"Rule 5 removing {tempVal} from {(row1, col1)}\nUsed {normalized[a]} and {normalized[b]}")
                        self.layout[row1][col1].note[tempVal - 1] = 0
                        rule5Done.add(key)
            if not self.stuck(tempCopy):
                print("3D Medusa Rule 5")
                return
            # rule 6 again referes to off-chain nodes
            # if an uncolored node shares a row, column, or box with nodes with colored notes that share all of the uncolored node's notes and all of the colors are the same, then that color cannot be true.
            for row in range(9):
                for col in range(9):
                    if self.locked[row][col]:
                        continue
                    tempSet = set(self.layout[row][col].note)
                    tempSet.discard(0)
                    rowOffset = (row//3) * 3
                    colOffset = (col//3) * 3
                    if any((row, col, v, c) in normalized for v in tempSet for c in ('green', 'yellow')):
                        continue
                    checksG = {v: False for v in tempSet}
                    checksY = {v: False for v in tempSet}
                    for val in tempSet:
                        for tempRow in range(9):
                            if row == tempRow:
                                continue
                            if (tempRow, col, val, 'green') in normalized:
                                checksG[val] = True
                            if (tempRow, col, val, 'yellow') in normalized:
                                checksY[val] = True
                        for tempCol in range(9):
                            if col == tempCol:
                                continue
                            if (row, tempCol, val, 'green') in normalized:
                                checksG[val] = True
                            if (row, tempCol, val, 'yellow') in normalized:
                                checksY[val] = True
                        for tempRow in range(rowOffset, rowOffset + 3):
                            for tempCol in range(colOffset, colOffset + 3):
                                if tempRow == row and tempCol == col:
                                    continue
                                if (tempRow, tempCol, val, 'green') in normalized:
                                    checksG[val] = True
                                if (tempRow, tempCol, val, 'yellow') in normalized:
                                    checksY[val] = True
                    allGSeen = all(checksG.values())
                    allYSeen = all(checksY.values())
                    if allGSeen:
                        print(f"Rule 6 removing all green nodes due to {row,col})")
                        for eRow, eCol, eVal, eColor in normalized:
                            if eColor == 'green':
                                self.layout[eRow][eCol].note[eVal - 1] = 0
                        return
                    if allYSeen:
                        print(f"Rule 6 removing all yellow nodes due to {row,col})")
                        for eRow, eCol, eVal, eColor in normalized:
                            if eColor == 'yellow':
                                self.layout[eRow][eCol].note[eVal - 1] = 0
                        return
                        
                        

    # Modified version of getConnectedNodes from simpleColoring, returns an array of nodes connected to the node parameter
    def getConnectedMedusaNodes(self, current, visited):
        i, j, currentVal, currentColor = current
        if currentColor == 'yellow':
            newColor = 'green'
        else:
            newColor = 'yellow'
        rowOffset = (i//3) * 3
        colOffset = (j//3) * 3
        connectedNodes = []
        tempDone = []
        tempSet = set(self.layout[i][j].note)
        tempSet.discard(0)
        # if node only has 2 values noted in, automatically connects the non-current value as a new node
        if len(tempSet) == 2:
            for val in tempSet:
                if (i, j, val, 'yellow') in visited or (i, j, val, 'green') in visited or (i, j, val, 'yellow') in tempDone or (i, j, val, 'green') in tempDone:
                    continue
                if val != currentVal:
                    connectedNodes += [(i, j, val, newColor)]
                    tempDone += [(i, j, val, newColor)]
        # checks box for strong connnection with current node's value
        for a in range(rowOffset, rowOffset + 3):
            for b in range(colOffset, colOffset + 3):
                if (a, b) == (i, j) or (a, b, currentVal, 'yellow') in visited or (a, b, currentVal, 'green') in visited or (a, b, currentVal, 'yellow') in tempDone or (a, b, currentVal, 'green') in tempDone:
                    continue
                if currentVal in self.layout[a][b].note:
                    if self.singleBoxCheck([(i, j), (a, b)], {currentVal}):
                        # print(f"{current} found {currentVal} in same box")
                        connectedNodes += [(a, b, currentVal, newColor)]
                        tempDone += [(a, b, currentVal, newColor)]     
        # checks the row for strong conneciton with current node's value
        for b in range(9):
            if b == j or (i, b, currentVal, 'yellow') in visited or (i, b, currentVal, 'green') in visited or (i, b, currentVal, 'yellow') in tempDone or (i, b, currentVal, 'green') in tempDone:
                continue
            if currentVal in self.layout[i][b].note:
                if self.singleRowCheck([(i, j), (i, b)], {currentVal}):
                    # print(f"{current} found {currentVal} in same row")
                    connectedNodes += [(i, b, currentVal, newColor)]
                    tempDone += [(i, b, currentVal, newColor)]
        # checks the column for strong connection with current node's value
        for a in range(9):
            if a == i or (a, j, currentVal, 'yellow') in visited or (a, j, currentVal, 'green') in visited or (a, j, currentVal, 'yellow') in tempDone or (a, j, currentVal, 'green') in tempDone:
                continue
            if currentVal in self.layout[a][j].note:
                if self.singleColCheck([(i, j), (a, j)], {currentVal}):
                    # print(f"{current} found {currentVal} in same col")
                    connectedNodes += [(a, j, currentVal, newColor)]
                    tempDone += [(a, j, currentVal, newColor)]
        return connectedNodes
    def getGroup(self, coordGroups, item):
        for i in range(len(coordGroups)):
            for j in range(len(coordGroups[i])):
                if item in coordGroups[i][j]:
                    return i
        return -1            
    # ********************************************************************************************************************
    def jellyFishUtil(self):
        tempCopy = copy.deepcopy(self)
        remaining = set()
        for i in range(9):
            for j in range(9):
                remaining |= set(self.layout[i][j].note)
        remaining.discard(0):
        print(remaining)
        for val in remaining:
            self.jellyFish(val)
            if not self.stuck(tempCopy):
                return
                
    def jellyFish(self, val):
        tempCopy = copy.deepcopy(self)
        rowSets = {i: set() for i in range(9)}
        colSets = {i: set() for i in range(9)}
        for i in range(9):
            for j in range(9):
                if val in self.layout[i][j].note:
                    rowSets[i].add(j)
                    colSets[j].add(i)
        rowSets = {r: c for r, c in rowSets.items() if 1 <= len(c) <= 4}
        colSets = {c: r for c, r in colSets.items() if 1 <= len(r) <= 4}
        for i in range(9):
            if not rowSets[i] or len(rowSets[i]) > 4:
                del rowSets[i]
        if len(rowSets) >= 4:
            for len in range(4, 1, -1):
                for i in rowSets:
                    currGroup = [rowSets[i]]
                    currGroup = self.formsJellyFish(self, currSet, rowSets)
                    if len(currGroup) == 4:
                        print(f"{val} found row jellyFish in cols {currGroup}")
                    for j in rowSets:
                        if currSet == rowSet[j]:
                            continue
        for j in range(9):
            if not colSets[j] or len(colSets[j]) > 4:
                del colSets[j]
        if len(colSets) >= 4:
            for len in range(4, 1, -1):
                for j in colSets:
                    
        for j in colSets:
            if not colSets[j]:
                del colSets[j]
        
    def formsJellyFish(self, currSet, rowSets):
        for i in rowSets:
            if rowSets[i] in currSet:
                continue
            for x in currSet:
                
        return currSet
    # ********************************************************************************************************************
    # xy wing
    # def xyWing(self):
    #     tempCopy = copy.deepcopy(self)
    #     for i in range(9):
    #         if not tempCopy.stuck(self):
    #             break
    #         for j in range(9):
    #             if not tempCopy.stuck(self):
    #                 break
    #             tempSet = set(self.layout[i][j].note)
    #             tempSet.discard(0)
    #             if self.layout[i][j].val != 0 or len(tempSet) != 2:
    #                 continue
    #             # checks the box
    #             for row in range((i//3) * 3, ((i//3) * 3) + 3):
    #                 for col in range((j//3) * 3, ((j//3) * 3) + 3):
                        
                # for row in range(((i//3) * 3) + 3, 9):
                #     if self.layout[row][j].val != 0:
                #         continue
                #     if val in self.layout[row][j].note and self.singleColCheck([(i, j),(row, j)], currVal):
                #         currCol += [(row, j)]
                #         break
                # if len(currCol != 2):
                #     continue
                # for row in range(9):
                #     if ((i//3) * 3) <= row < (((i//3) * 3) + 3):
                #         continue
                #     for col in range(9):
                #         if val in self.layout[row][col].note:
                            
        #     for i in range(row,9)
        # for j in range(col + 1, 9):
        #     if self.layout[row][j].val != 0:
        #         continue
        #     if val in self.layout[row][j].note and self.singleRowCheck([coords, (row, j)], val):
        #         potCol.append(j)
        # if len(potCol) == 0:
        #     return (False, coords)
        # for i in range(row + 1, 9):
        #     if self.layout[i][col].val != 0:
        #         continue
        #     if val in self.layout[i][col].note:
        #         potRow.append(i)
        # if len(potRow) == 0:
        #     return (False, coords)
        # for i in potRow:
        #     for j in potCol:
        #         if self.layout[i][j].val != 0:
        #             continue
        #         if val in self.layout[i][j].note:
        #             goodSquare.append([coords, (row, j), (i, col), (i,j)])
        # if len(goodSquare) == 0:
        #     return (False, coords)
        # return (True, goodSquare[len(goodSquare) - 1])
                    
                    
    
    # attempts to solve individual value based on isolating the current node to what exists in the related squares rows and columnn
    # it will return a true or a false based on if a certain value can be proved 
    # def babySolve(self, x, i, j):
    #     # if the value is not a possibility (not in the current notes), it will return False 
    #     rowOffset = (i//3) * 3
    #     colOffset = (j//3) * 3
    #     # array of bools, represents the final return value
    #     checkerBox = [False for _ in range(4)]
    #     # inverset lists of the rows and columns that need checking
    #     inverseRow = [x for x in range(rowOffset,rowOffset+3)]
    #     inverseRow.remove(i)
    #     inverseCol = [x for x in range(colOffset,colOffset+3)]
    #     inverseCol.remove(j)

    #     for a in inverseRow:
    #         # Very easily can add a boxlocked[a][b]-or conditional
    #         if self.layout[a][colOffset].val != 0 and self.layout[a][colOffset + 1].val != 0 and self.layout[a][colOffset + 2].val != 0:
    #             checkerBox[inverseRow.index(a)] = True
    #     for a in inverseCol:
    #         # Very easily can add a boxlocked[a][b]-or conditional
    #         if self.layout[rowOffset][a].val != 0 and self.layout[rowOffset + 1][a].val != 0 and self.layout[rowOffset + 2][a].val != 0:
    #             checkerBox[inverseCol.index(a) + 2] = True

    #     for p in range(4):
    #         if checkerBox[p]:
    #             continue
    #         if p < 2:
    #             temp = []
    #             for a in range(9):
    #                 if colOffset <= a < colOffset + 3:
    #                     continue
    #                 temp.append(self.layout[inverseRow[p]][a].val)
    #             if x in temp:
    #                 checkerBox[p] = True
    #         else:
    #             temp = []
    #             for a in range(9):
    #                 if rowOffset <= a < rowOffset + 3:
    #                     continue
    #                 temp.append(self.layout[a][inverseCol[p - 2]].val)
    #             if x in temp:
    #                 checkerBox[p] = True
    #     if False in checkerBox:
    #         return False
    #     print(f"found {x} at {i} {j}")
    #     return True                    

    # def babySolveUser(self):
    #     for i in range(9):
    #         for j in range(9):
    #             if self.layout[i][j].val != 0:
    #                 continue
    #             tempSet = set(self.layout[i][j].note)
    #             tempSet.discard(0)
    #             for k in tempSet:
    #                 if self.babySolve(k, i, j):
    #                     self.layout[i][j].setVal(k+1)
    #                     self.babySolveUser()


        
                # elif len(tempSet) == 3:
                #     boxlock2 = False
                #     while cA < 3 and not boxLock:
                #         while cB < 3 and not boxlock:
                #             temp = set(self.layout[cA + rowOffset][cB + colOffset].note)
                #             temp.remove(0)
                #             if temp <= tempSet and ((i, j) != (cA + rowOffset, cB + colOffset)):
                #                 if not boxLock:
                #                     boxLock = True
                #                     i2 = cA + rowOffset
                #                     j2 = cB + colOffset
                #                 elif not boxLock2:
                #                     boxLock2 = True
                #                     i3 = cA + rowOffset
                #                     j3 = cB + rowOffset
                #             cB += 1
                #         cA += 1
# if i == i2 and j != j2:
#                                     self.locked2[i][j] = self.softlinelockedx2[i][j] = self.softlinelockedx2[i2][j2] = True
#                                 elif j == j2 and i != i2: 
#                                     self.locked2[i][j] = self.softlinelockedy2[i2][j2] = self.softlinelockedy2[i2][j2] = True
#                                 if self.softlinelockedy2[i][j] or self.softlinelockedx2[i][j]:
#                                     self.locked2[i][j] = True
    # can't remember what this does, i think it 
    # def boxCheck2(self, i, j, i2, j2):
    #     rowOffset = (i//3) * 3
    #     colOffset = (j//3) * 3
    #     for a in range(rowOffset, rowOffset + 3):
    #         for b in range(colOffset, colOffset + 3):
    #             # print(f"RowOffset {rowOffset} + {cA} ColOffset {colOffset} + {cB}")
    #             temp = set(self.layout[a][b].note)
    #             if not self.softboxlocked2[a][b] and temp != {0}:
    #                 return True
    #     return False

                
        
    # def checklocks
                            
                    
    # THINK ABOUT IT
#     from itertools import combinations

# candidates = [(i, j) for i in range(3) for j in range(3) if len(note[i][j]) == 2]
# for trio in combinations(candidates, 3):
#     combined = set().union(*(note[i][j] for i, j in trio))
#     if len(combined) == 3:


# garbage broken redundant code
# def doubleCheck(self):
#         tempCopy = copy.deepcopy(self)
#         # checks each value individually
#         for val in range(1, 10):
#             # iterates through row boxes
#             for i in range(3):
#                 rowOffset = i * 3
#                 goodRow1 = set()
#                 goodRow2 = set()
#                 goodRow3 = set()
#                 for row in range(rowOffset, rowOffset + 3):
#                     for col in range(0, 3):
#                         if val in self.layout[row][col].note:
#                             goodRow1.add(row)
#                     for col in range(3, 6):
#                         if val in self.layout[row][col].note:
#                             goodRow2.add(row)
#                     for col in range(6, 9):
#                         if val in self.layout[row][col].note:
#                             goodRow3.add(row)
#                 if not len(goodRow1) > 0 or not len(goodRow2) > 0 or not len(goodRow3) > 0:
#                     continue
#                 if len(goodRow1) == 2 and (goodRow1 == goodRow2 ^ goodRow1 == goodRow3):
#                     if goodRow1 == goodRow2:
#                         safeRow = set(goodRow1.difference(goodRow3)).pop()
#                         for row in range(rowOffset, rowOffset + 3):
#                             if row == safeRow:
#                                 continue
#                             for col in range(6, 9):
#                                 self.layout[row][col].note[val - 1] = 0
#                         if not tempCopy.stuck(self):
#                             print(f"double check elminated {val} in row chute {i} in columns 6 - 9")
#                     elif goodRow1 == goodRow3:
#                         safeRow = set(goodRow1.difference(goodRow2)).pop()
#                         for row in range(rowOffset, rowOffset + 3):
#                             if row == safeRow:
#                                 continue
#                             for col in range(3, 6):
#                                 self.layout[row][col].note[val - 1] = 0
#                         if not tempCopy.stuck(self):
#                             print(f"double check elminated {val} in row chute {i} in columns 3 - 6")
#                 if len(goodRow2) == 2 and (goodRow2 == goodRow3):
#                     safeRow = set(goodRow1.difference(goodRow3)).pop()
#                     for row in range(forOffset, rowOffset + 3):
#                         if row == safeRow:
#                             continue
#                         for col in range(0, 3):
#                             self.layout[row][col].note[val - 1] = 0
#                     if not tempCopy.stuck(self):
#                         print(f"double check elminated {val} in row chute {i} in columns 0 - 3")
#             for j in range(3):
#                 colOffset = j * 3
#                 goodCol1 = set()
#                 goodCol2 = set()
#                 goodCol3 = set()
#                 for col in range(colOffset, colOffset + 3):
#                     for row in range(0, 3):
#                         if val in self.layout[row][col].note:
#                             goodCol1.add(col)
#                     for row in range(3, 6):
#                         if val in self.layout[row][col].note:
#                             goodCol2.add(col)
#                     for row in range(6, 9):
#                         if val in self.layout[row][col].note:
#                             goodCol3.add(col)
#                 if len(goodCol1) == 2 and (goodCol1 == goodCol2 ^ goodCol1 == goodCol3):
#                     if goodCol1 == goodCol2:
#                         safeCol = set(goodCol1.difference(goodCol3)).pop()
#                         for col in range(colOffset, colOffset + 3):
#                             if col == safeCol:
#                                 continue
#                             for row in range(6, 9):
#                                 self.layout[row][col].note[val - 1] = 0
#                         if not tempCopy.stuck(self):
#                             print(f"double check eliminated {val} in col chute {j} in rows 6 - 9)")
#                     elif goodCol1 == goodCol3:
#                         safeCol = set(goodCol1.difference(goodCol2)).pop()
#                         for col in range(colOffset, colOffset + 3):
#                             if col == safeCol:
#                                 continue
#                             for row in range(3, 6):
#                                 self.layout[row][col].note[val - 1] = 0
#                         if not tempCopy.stuck(self):
#                             print(f"double check eliminated {val} in col chute {j} in rows 3 - 6)")
#                 if len(goodCol2) == 2 and goodCol2 == goodCol3:
#                     safeCol = set(goodCol2.difference(goodCol1)).pop()
#                     for col in range(colOffset, colOffset + 3):
#                         if col == safeCol:
#                             continue
#                         for row in range(0, 3):
#                             self.layout[row][col].note[val - 1] = 0
#                     if not tempCopy.stuck(self):
#                         print(f"double check eliminated {val} in col chute {j} in rows 0 - 3)")







            