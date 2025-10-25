import itertools
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
            Puzzle.displayAll()
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
    Puzzle.uniqueRectangleUtil()
    if not Puzzle.stuck(temp):
        print("Unique Rectangles Worked")
        return Puzzle
    Puzzle.tridagonUtil()
    if not Puzzle.stuck(temp):
        print("Tridagon Worked")
        return Puzzle
    Puzzle.fireworkUtil()
    if not Puzzle.stuck(temp):
        print("Firework Worked")
        return Puzzle
    Puzzle.twinXYChains()
    if not Puzzle.stuck(temp):
        print("Twin XY Chains Worked")
        return Puzzle
    Puzzle.SKLoops()
    if not Puzzle.stuck(temp):
        print("SK Loops Worked")
        return Puzzle
    Puzzle.extUniqueRectanglesUtil()
    if not Puzzle.stuck(temp):
        print("Extended Unique Rectangles Worked")
        return Puzzle
    Puzzle.hiddenUniqueRectanglesUtil()
    if not Puzzle.stuck(temp):
        print("Hidden Unique Rectangles Worked")
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
                        lockList = [(i, j)]
                        for a in range(rowOffset, rowOffset + 3):
                            for b in range(colOffset, colOffset + 3):
                                if (a, b) == (i, j) or self.layout[a][b].val != 0:
                                    continue
                                tempSet2 = set(self.layout[a][b].note)
                                tempSet2.discard(0)
                                if tempSet == tempSet2:
                                    lockList.append((a, b))
                        if len(lockList) == 3:
                            masterSet = tempSet
                            self.subUpdateNotes('box', lockList, masterSet)
                            for a, b in lockList:
                                self.softboxlocked[a][b] = True
                            if self.inRow(lockList):
                                self.subUpdateNotes('row', lockList, masterSet)
                            elif self.inCol(lockList):
                                self.subUpdateNotes('col', lockList, masterSet)
                        else:
                            goodcheck, coordList, masterSet = self.loopCheck3(False, [(i, j)], tempSet, 0)
                            if goodcheck:
                                self.subUpdateNotes('box', coordList, masterSet)
                                for a, b in coordList:
                                    self.softboxlocked[a][b] = True
                                if len(coordList) == 3:
                                    if self.inRow(coordList):
                                        self.subUpdateNotes('row', coordList, masterSet)
                                    elif self.inCol(coordList):
                                        self.subUpdateNotes('col', coordList, masterSet)
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
        tempCopy = copy.deepcopy(self)
        valsLeft = set()
        for i in range(9):
            for j in range(9):
                valsLeft = valsLeft.union(set(self.layout[i][j].note))
        valsLeft.discard(0)
        # print(valsLeft)
        for val in valsLeft:
            self.squareFind(val, tempCopy)
            if not self.stuck(tempCopy):
                return

    # searches for xwings and updates accordingly
    # an x wing is an instance where 2 rows or columns have only 2 notes for the same value
    # if they form a square, the respective column or row's notes can remove the value that forms the square
    def squareFind(self, val, tempCopy):
        # creates a dictionary with key row index to a set of columns where val appears
        rowSet = {r: {c for c in range(9) if val in self.layout[r][c].note} for r in range(9) if any(val in self.layout[r][c].note for c in range(9))}
        for i in rowSet:
            # makes sure current rowSet is 2 length
            if len(rowSet[i]) == 2:
                for j in rowSet:
                    if i == j:
                        continue
                    # makes sure rowset[j] is length 2 and is equivalent to rowset[i]
                    if len(rowSet[j]) == 2 and rowSet[i] == rowSet[j]:
                        for c in rowSet[i]:
                            self.subUpdateNotes('col', [(i, c), (j, c)], {val})
                        if not self.stuck(tempCopy):
                            print(f"X-Wing removed {val} in columns {rowSet[i]}")
                            return
        colSet = {c: {r for r in range(9) if val in self.layout[r][c].note} for c in range(9) if any(val in self.layout[r][c].note for r in range(9))}
        for i in colSet:
            if len(colSet[i]) == 2:
                for j in colSet:
                    if i == j:
                        continue
                    if len(colSet[j]) == 2 and colSet[i] == colSet[j]:
                        for r in colSet[i]:
                            self.subUpdateNotes('row', [(r, i), (r, j)], {val})
                        if not self.stuck(tempCopy):
                            print(f"X-Wing removed {val} in rows {colSet[i]}")
                            return
        
    # ********************************************************************************************************************
    # Performs chute remote pairs strategy & updates accordingly, "naked" pairs which exist in different rows and columns (within square sight of a node)
    def chuteRemotePairs(self):
        tempCopy = copy.deepcopy(self)
        remaining = {v for r in range(9) for c in range(9) for v in self.layout[r][c].note if v != 0}
        for combo in itertools.combinations(remaining, 2):
            comboSet = set(combo)
            rowPairs = self.getRowChuteRemotePairs(comboSet)
            if len(rowPairs) != 0:
                for (a, b), (x, y) in rowPairs:
                    rowOffset1 = (a // 3) * 3
                    colOffset1 = (b // 3) * 3
                    colOffset2 = (y // 3) * 3
                    pencilSet = set()
                    pennedSet = set()
                    for row in range(rowOffset1, rowOffset1 + 3):
                        if row == a or row == x:
                            continue
                        for col in range(9):
                            if colOffset1 <= col < colOffset1 + 3 or colOffset2 <= col < colOffset2 + 3:
                                continue
                            if self.layout[row][col].val == 0:
                                temp = set(self.layout[row][col].note) - {0}
                                pencilSet |= temp
                            else:
                                pennedSet.add(self.layout[row][col].val)
                    remoteIntersection = comboSet & (pencilSet | pennedSet)
                    pencilIntersection = comboSet & pencilSet
                    pennedIntersection = comboSet & pennedSet
                    if len(pencilSet) == 0 and len(pennedIntersection) == 0:
                        # if neither value in the remote pair is penned in, then performs double elimination
                        for eVal in comboSet:
                            for eCol in range(colOffset1, colOffset1 + 3):
                                self.layout[x][eCol].note[eVal-1] = 0
                            for eCol in range(colOffset2, colOffset2 + 3):
                                self.layout[a][eCol].note[eVal-1] = 0
                        if not self.stuck(tempCopy):
                            print(f"Row Remote Pair 1: {[(a, b), (x, y)]}")
                            return
                        # if only one remote pair is penned in, erases that value from the appropraite nodes
                    elif len(pennedIntersection) == 1 and len(pencilIntersection) == 0:
                        eVal = (comboSet & pennedSet).pop()
                        for eCol in range(colOffset1, colOffset1 + 3):
                            self.layout[x][eCol].note[eVal-1] = 0
                        for eCol in range(colOffset2, colOffset2 + 3):
                            self.layout[a][eCol].note[eVal-1] = 0
                        if not self.stuck(tempCopy):
                            print(f"Row Remote Pair 2: {[(a, b), (x, y)]}")
                            return
                    # otherwise it checks for what values are pencilled in
                    elif len(remoteIntersection) == 1 and len(pencilIntersection) == 1:
                        eVal = (pencilSet & comboSet).pop()
                        for eCol in range(colOffset1, colOffset1 + 3):
                            self.layout[x][eCol].note[eVal-1] = 0
                        for eCol in range(colOffset2, colOffset2 + 3):
                            self.layout[a][eCol].note[eVal-1] = 0
                        if not self.stuck(tempCopy):
                            print(f"Row Remote Pair 3: {[(a, b), (x, y)]}")
                            return
        for combo in itertools.combinations(remaining, 2):
            comboSet = set(combo)
            colPairs = self.getColChuteRemotePairs(comboSet)
            if len(colPairs) != 0:
                for (a, b), (x, y) in colPairs:
                    colOffset1 = (b // 3) * 3
                    colOffset2 = (y // 3) * 3
                    rowOffset1 = (a // 3) * 3
                    rowOffset2 = (x // 3) * 3
                    pencilSet = set()
                    pennedSet = set()
                    for col in range(colOffset1, colOffset1 + 3):
                        if col == b or col == y:
                            continue
                        for row in range(9):
                            if rowOffset1 <= row < rowOffset1 + 3 or rowOffset2 <= row < rowOffset2 + 3:
                                continue
                            if self.layout[row][col].val == 0:
                                temp = set(self.layout[row][col].note) - {0}
                                pencilSet |= temp
                            else:
                                pennedSet.add(self.layout[row][col].val)
                    remoteIntersection = comboSet & (pencilSet | pennedSet)
                    pencilIntersection = comboSet & pencilSet
                    pennedIntersection = comboSet & pennedSet
                    # if neither value in the remote pair is penned in, then performs double elimination
                    if len(pencilSet) == 0 and len(pennedIntersection) == 0:
                        for eVal in comboSet:
                            for eRow in range(rowOffset1, rowOffset1 + 3):
                                self.layout[eRow][y].note[eVal - 1] = 0
                            for eRow in range(rowOffset2, rowOffset2 + 3):
                                self.layout[eRow][b].note[eVal - 1] = 0
                        if not self.stuck(tempCopy):
                            print(f"Col Remote Pair 1: {[(a, b), (x, y)]}")
                            return
                        # if only one remote pair is penned in, erases that value from the appropraite nodes
                    elif len(pennedIntersection) == 1 and len(pencilIntersection) == 0:
                        eVal = (pennedIntersection).pop()
                        for eRow in range(rowOffset1, rowOffset1 + 3):
                            self.layout[eRow][y].note[eVal - 1] = 0
                        for eRow in range(rowOffset2, rowOffset2 + 3):
                            self.layout[eRow][b].note[eVal - 1] = 0
                        if not self.stuck(tempCopy):
                            print(f"Col Remote Pair 2: {[(a, b), (x, y)]}")
                            return
                    # otherwise it checks for what values are pencilled in
                    elif len(remoteIntersection) == 1 and len(pencilIntersection) == 1:
                        eVal = (pencilSet & comboSet).pop()
                        for eRow in range(rowOffset1, rowOffset1 + 3):
                            self.layout[eRow][y].note[eVal - 1] = 0
                        for eRow in range(rowOffset2, rowOffset2 + 3):
                            self.layout[eRow][b].note[eVal - 1] = 0
                        if not self.stuck(tempCopy):
                            print(f"Col Remote Pair 3: {[(a, b), (x, y)]}")
                            return
    def getRowChuteRemotePairs(self, combo):
        remotePairs = []
        for rowBlock in range(0, 9, 3):
            for i in range(rowBlock, rowBlock + 3):
                for j in range(9):
                    if self.layout[i][j].val != 0:
                        continue
                    tempSet = set(self.layout[i][j].note) - {0}
                    if tempSet != combo:
                        continue
                    for a in range(rowBlock, rowBlock + 3):
                        if a == i:
                            continue
                        for b in range(9):
                            if (j//3) == (b//3) or self.layout[a][b].val != 0:
                                continue
                            temp = set(self.layout[a][b].note) - {0}
                            if temp == combo and [(a, b), (i, j)] not in remotePairs:
                                remotePairs.append([(i, j), (a, b)])
        return remotePairs
        
    def getColChuteRemotePairs(self, combo):
        remotePairs = []
        for colBlock in range(0, 9, 3):
            for j in range(colBlock, colBlock + 3):
                for i in range(9):
                    if self.layout[i][j].val != 0:
                        continue
                    tempSet = set(self.layout[i][j].note)
                    tempSet.discard(0)
                    if tempSet != combo:
                        continue
                    for b in range(colBlock, colBlock + 3):
                        if b == j:
                            continue
                        for a in range(9):
                            if (i // 3) == (a // 3) or self.layout[a][b].val != 0:
                                continue
                            temp = set(self.layout[a][b].note)
                            temp.discard(0)
                            if temp == combo and [(a, b), (i, j)] not in remotePairs:
                                remotePairs.append([(i, j), (a, b)])
        return remotePairs
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
                            print(f"SimpleColoring found {val} at index ({x}, {y})")
                            # print("start")
                            # for nodes in group:
                            #     print(nodes)
                            self.layout[x][y].setVal(val)
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
            self.swordfish(val, tempCopy)
            if not self.stuck(tempCopy):
                return
                
    def swordfish(self, val, tempCopy):
        # works the same way as xwing
        rowSet = {r: {c for c in range(9) if val in self.layout[r][c].note} for r in range(9) if any(val in self.layout[r][c].note for c in range(9))}
        # creates an array of keys if the rowset item fits length parameters 
        rowKeys = [r for r in rowSet if 2 <= len(rowSet[r]) <= 3]
        for i in range(len(rowKeys)):
            for j in range(i + 1, len(rowKeys)):
                for k in range(j + 1, len(rowKeys)):
                    # for erasing purposes, it pulls the sets from rowKeys 
                    r1, r2, r3 = rowKeys[i], rowKeys[j], rowKeys[k]
                    # creates a masterset of the contents of r1, r2, and r3
                    cols = rowSet[r1] | rowSet[r2] | rowSet[r3]
                    # only continues if the masterset is length 3
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
                        if self.inBox([tempRowNode, (i, j)]):
                            continue
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
                        if self.inBox([tempColNode, (i, j)]):
                            continue
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
                        for node in cycles:
                            print(node)
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
            if self.singleRowCheck([coords, (i, col)], {val}):
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
            if self.singleColCheck([coords, (row, j)], {val}):
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
                if self.singleBoxCheck([coords, (row,col)], {val}):
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
        # print(remaining)
        for val in remaining:
            # print("currently on: ", val)
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
                    # print(node)
            # print()
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
                    if self.layout[row][col].val != 0:
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
    # # ********************************************************************************************************************
    def jellyFishUtil(self):
        tempCopy = copy.deepcopy(self)
        remaining = set()
        for i in range(9):
            for j in range(9):
                remaining |= set(self.layout[i][j].note)
        remaining.discard(0)
        # print(remaining)
        for val in remaining:
            self.jellyFish(val, tempCopy)
            if not self.stuck(tempCopy):
                return
                
    def jellyFish(self, val, tempCopy):
        # works the same way as swordfish but there's 4 values to check the parameter and also different loop functionality
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
    def uniqueRectangleUtil(self):
        tempCopy = copy.deepcopy(self)
        remaining = {v for r in range(9) for c in range(9) for v in self.layout[r][c].note if v != 0}
        # print(remaining)
        for combo in itertools.combinations(remaining, 2):
            self.uniqueRectangles(set(combo), tempCopy)
            if not self.stuck(tempCopy):
                return

    def uniqueRectangles(self, combo, tempCopy):
        rowSets = set()
        for row in range(9):
            matchingCols = [c for c in range(9) if set(self.layout[row][c].note) - {0} == combo]
            for c1, c2 in itertools.combinations(matchingCols, 2):
                pair = frozenset(((row, c1), (row, c2)))
                rowSets.add(pair)
        rowRPSets = self.getRowChuteRemotePairs(combo)
        colSets = set()
        for col in range(9):
            matchingRows = [r for r in range(9) if set(self.layout[r][col].note) - {0} == combo]
            for r1, r2 in itertools.combinations(matchingRows, 2):
                pair = frozenset(((r1, col), (r2, col)))
                colSets.add(pair)
        colRPSets = self.getColChuteRemotePairs(combo)
        
        # Type-1 removes combo from cells that will form deadly pattern (this one targets using row pairs) 
        for (a, b), (x, y) in rowSets:
            for row in range(9):
                if row == a:
                    continue
                if set(self.layout[row][b].note) - {0} == combo:
                    for val in combo:
                        self.layout[row][y].note[val-1] = 0
                elif set(self.layout[row][y].note) - {0} == combo:
                    for val in combo:
                        self.layout[row][b].note[val-1] = 0
                if not self.stuck(tempCopy):
                    print(f"Removed {combo} using row type 1\nCells: {(a, b), (x, y)}")
                    return
        for (a, b), (x, y) in colSets:
            # print("ColSet: ", combo, cells[0], cells[1])
            for col in range(9):
                if col == b:
                    continue
                if set(self.layout[a][col].note) - {0} == combo:
                    for val in combo:
                        self.layout[x][col].note[val-1] = 0
                elif set(self.layout[x][col].note) - {0} == combo:
                    for val in combo:
                        self.layout[a][col].note[val-1] = 0
                if not self.stuck(tempCopy):
                    print(f"Removed {combo} using col type 1\nCells: {(a, b), (x, y)}")
                    return
        # Type-2A and Type-2B refer to nodes with equal notes that contain the combo and are in line (columns) with the pair
        # since the non-combo number must be in these cells, we can erase them from its current row and box (but not the whole column)
        for (a, b), (x, y) in rowSets:
            if not self.inBox([(a, b), (x, y)]):
                continue
            for row in range(9):
                if row == a:
                    continue
                if self.layout[row][b].note == self.layout[row][y].note and len(set(self.layout[row][b].note) - {0}) == 3 and combo <= set(self.layout[row][b].note) - {0}:
                    eIgnoreCells = [(row, b), (row, y)]
                    eVal = set(self.layout[row][b].note) - {0} - combo
                    eVal = eVal.pop()
                    self.subUpdateNotes('row', eIgnoreCells, {eVal})
                    if self.inBox([(a, b), (x, y)]):   
                        self.subUpdateNotes('box', eIgnoreCells, {eVal})
                if not self.stuck(tempCopy):
                    print(f"Removed {eVal} using row type 2A/B")
                    return
        for (a, b), (x, y) in colSets:
            if not self.inBox([(a, b), (x, y)]):
                continue
            # print("ColSet: ", combo, cells[0], cells[1])
            for col in range(9):
                if col == b:
                    continue
                if len(set(self.layout[a][col].note) - {0}) == 3 and set(self.layout[a][col].note) == set(self.layout[x][col].note) and combo <= set(self.layout[x][col].note) - {0}:
                    eIgnoreCells = [(a, col), (x, col)]
                    eVal = set(self.layout[a][col].note) - {0} - combo
                    eVal = eVal.pop()
                    self.subUpdateNotes('col', eIgnoreCells, {eVal})
                    if self.inBox([(a, b), (x, y)]):   
                        self.subUpdateNotes('box', eIgnoreCells, {eVal})
                if not self.stuck(tempCopy):
                    print(f"Removed {eVal} using row type 2A/B")
                    return

        # type 2C deals with remote pairs that form rectangles, if the non remote pair values are identical, the non combo value must exist in the non remote pair nodes, so it can be removed from the inbox nodes that the remote pair nodes can see (in respective rows and columns)
        for (a, b), (x, y) in rowRPSets:
            # print(f"{combo} Row Remote Pairs: {(a, b), (x, y)}")
            tempSet1 = set(self.layout[a][y].note) - {0}
            tempSet2 = set(self.layout[x][b].note) - {0}
            if tempSet1 == tempSet2 and self.layout[a][y].val == 0 and combo <= set(self.layout[a][y].note) - {0}:
                eVal = tempSet1 - {0} - combo
                eVal = eVal.pop()
                colOffset1 = (b//3) * 3
                colOffset2 = (y//3) * 3
                for eCol in range(colOffset1, colOffset1 + 3):
                    self.layout[a][eCol].note[eVal - 1] = 0
                for eCol in range(colOffset2, colOffset2 + 3):
                    self.layout[x][eCol].note[eVal - 1] = 0
                if not self.stuck(tempCopy):
                    print(f"Removed {eVal} using row type 2C")
                    return
        for (a, b), (x, y) in colRPSets:
            # print(f"{combo} Col Remote Pairs: {(a, b), (x, y)}")
            tempSet1 = set(self.layout[a][y].note) - {0}
            tempSet2 = set(self.layout[x][b].note) - {0}
            if tempSet1 == tempSet2 and self.layout[a][y].val == 0 and combo <= set(self.layout[a][y].note) - {0}:
                eVal = tempSet1 - combo
                eVal = eVal.pop()
                rowOffset1 = (a//3) * 3
                rowOffset2 = (x//3) * 3
                for eRow in range(rowOffset1, rowOffset1 + 3):
                    self.layout[eRow][b].note[eVal-1] = 0
                for eRow in range(rowOffset2, rowOffset2 + 3):
                    self.layout[eRow][y].note[eVal-1] = 0
                if not self.stuck(tempCopy):
                    print(f"Removed {eVal} using col type 2C")
                    return

        # type 3 deals with non combo values found in the roof nodes, if the roof nodes non-combo values form a loop with notes in it's row or column (or box if they share a box), then the loop values can be removed from their respective row or column (or box)
        for (a, b), (x, y) in rowSets:
            rowOffset = (a//3) * 3
            if not self.inBox([(a, b), (x, y)]):
                for row in range(rowOffset, rowOffset + 3):
                    if row == a:
                        continue
                    tempSet1 = set(self.layout[row][b].note) - {0}
                    tempSet2 = set(self.layout[row][y].note) - {0}
                    if combo <= tempSet1 and combo <= tempSet2 and tempSet1 != tempSet2:
                        goalSet = (tempSet1 | tempSet2) - combo
                        if len(goalSet) not in (2, 3):
                            continue
                        ignoreSet = [(row, b), (row, y)]
                        print(f"Floor: {(a, b), (x, y)}. Roof: {(row, b), (row, y)}")
                        result = self.urLoopCheck('row', combo, ignoreSet, goalSet)
                        if result[0]:
                            ignoreSet = result[1]
                            eVals = result[2]
                            self.subUpdateNotes('row', ignoreSet, eVals)
                            if not self.stuck(tempCopy):
                                print(f"Floor: {(a, b), (x, y)}. Roof: {(row, b), (row, y)}\nRemoved {eVals} using from row {row} using type 3 (Not in box)")
                                return
            else:
                for row in range(9):
                    if rowOffset <= row < rowOffset + 3:
                        continue
                    tempSet1 = set(self.layout[row][b].note) - {0}
                    tempSet2 = set(self.layout[row][y].note) - {0}
                    if combo <= tempSet1 and combo <= tempSet2 and tempSet1 != tempSet2:
                        goalSet = (tempSet1 | tempSet2) - combo
                        if len(goalSet) not in (2, 3):
                            continue
                        ignoreSet = [(row, b), (row, y)]
                        result = self.urLoopCheck('row', combo, ignoreSet, goalSet)
                        if result[0]:
                            ignoreSet = result[1]
                            eVals = result[2]
                            self.subUpdateNotes('row', ignoreSet, eVals)
                            if not self.stuck(tempCopy):
                                print(f"Floor: {(a, b), (x, y)}. Roof: {(row, b), (row, y)}\nRemoved {eVals} using from row {row} using type 3 (In box)")
                        ignoreSet = [(row, b), (row, y)]
                        result = self.urLoopCheck('box', combo, ignoreSet, goalSet)
                        if result[0]:
                            ignoreSet = result[1]
                            eVals = result[2]
                            self.subUpdateNotes('box', ignoreSet, eVals)
                            if not self.stuck(tempCopy):
                                print(f"Floor: {(a, b), (x, y)}. Roof: {(row, b), (row, y)}\nRemoved {eVals} using from box using type 3 (In box)")
                        if not self.stuck(tempCopy):
                            return

        for (a, b), (x, y) in colSets:
            colOffset = (b // 3) * 3
            if not self.inBox([(a, b), (x, y)]):
                for col in range(colOffset, colOffset + 3):
                    if col == b:
                        continue
                    tempSet1 = set(self.layout[a][col].note) - {0}
                    tempSet2 = set(self.layout[x][col].note) - {0}
                    if combo <= tempSet1 and combo <= tempSet2 and tempSet1 != tempSet2:
                        goalSet = (tempSet1 | tempSet2) - combo
                        if len(goalSet) not in (2, 3):
                            continue
                        ignoreSet = [(a, col), (x, col)]            
                        result = self.urLoopCheck('col', combo, ignoreSet, goalSet)
                        if result[0]:
                            print(f"IgnoreSet: {result[1]}")
                            print(f"eVals: {result[2]}")
                            ignoreSet = result[1]
                            eVals = result[2]
                            self.subUpdateNotes('col', ignoreSet, eVals)
                            if not self.stuck(tempCopy):
                                print(f"Floor: {(a, b), (x, y)}. Roof: {(a, col), (x, col)}\nRemoved {eVals} using from col {col} using type 3 (Not in box)")
                                return
            else:
                for col in range(9):
                    if colOffset <= col < colOffset + 3:
                        continue
                    tempSet1 = set(self.layout[a][col].note) - {0}
                    tempSet2 = set(self.layout[x][col].note) - {0}
                    if combo <= tempSet1 and combo <= tempSet2 and tempSet1 != tempSet2:
                        goalSet = (tempSet1 | tempSet2) - combo
                        if len(goalSet) not in (2, 3):
                            continue
                        ignoreSet = [(a, col), (x, col)]
                        result = self.urLoopCheck('col', combo, ignoreSet, goalSet)
                        if result[0]:
                            ignoreSet = result[1]
                            eVals = result[2]
                            self.subUpdateNotes('col', ignoreSet, eVals)
                            if not self.stuck(tempCopy):
                                print(f"Floor: {(a, b), (x, y)}. Roof: {(a, col), (x, col)}\nRemoved {eVals} using from col {col} using type 3 (In box)")
                        ignoreSet = [(a, col), (x, col)]
                        result = self.urLoopCheck('box', combo, ignoreSet, goalSet)
                        if result[0]:
                            ignoreSet = result[1]
                            eVals = result[2]
                            self.subUpdateNotes('box', ignoreSet, eVals)
                            if not self.stuck(tempCopy):
                                print(f"Floor: {(a, b), (x, y)}. Roof: {(a, col), (x, col)}\nRemoved {eVals} using from box using type 3 (In box)")
                        if not self.stuck(tempCopy):
                            return
        # Rule 4 checks roof nodes to see if they are exlusive to their the roof nodes in their given row, column or box (if they share a box), and removes the other combo value if this is true
        for (a, b), (x, y) in rowSets:
            rowOffset = (a//3) * 3
            if self.inBox([(a, b), (x, y)]):
                for row in range(9):
                    if rowOffset <= row < rowOffset + 3:
                        continue
                    tempSet1 = set(self.layout[row][b].note) - {0}
                    tempSet2 = set(self.layout[row][y].note) - {0}
                    if combo <= tempSet1 and combo <= tempSet2 and tempSet1 != tempSet2:
                        goodVal = 0
                        for tempVal in combo:
                            if self.singleRowCheck([(row, b), (row, y)], {tempVal}) or self.singleBoxCheck([(row, b), (row, y)], {tempVal}):
                                goodVal = tempVal
                                break
                        if goodVal != 0:
                            eVal = combo - {goodVal}
                            eVal = eVal.pop()
                            self.layout[row][b].note[eVal-1] = 0
                            self.layout[row][y].note[eVal-1] = 0
                            if not self.stuck(tempCopy):
                                print(f"Removed {eVal} from roof nodes {(row, b), (row, y)} using row type 4a")
                                return
            else:
                for row in range(rowOffset, rowOffset + 3):
                    if row == a:
                        continue
                    tempSet1 = set(self.layout[row][b].note) - {0}
                    tempSet2 = set(self.layout[row][y].note) - {0}
                    if combo <= tempSet1 and combo <= tempSet2 and tempSet1 != tempSet2:
                        goodVal = 0
                        for tempVal in combo:
                            if self.singleRowCheck([(row, b), (row, y)], {tempVal}):
                                goodVal = tempVal
                                break
                        if goodVal != 0:
                            eVal = combo - {goodVal}
                            eVal = eVal.pop()
                            self.layout[row][b].note[eVal-1] = 0
                            self.layout[row][y].note[eVal-1] = 0
                            if not self.stuck(tempCopy):
                                print(f"Removed {eVal} from nodes {(row, b), (row, y)} using row type 4b")
                                return
        for (a, b), (x, y) in colSets:
            colOffset = (b//3) * 3
            if self.inBox([(a, b), (x, y)]):
                for col in range(9):
                    if colOffset <= col < colOffset + 3: 
                        continue
                    tempSet1 = set(self.layout[a][col].note) - {0}
                    tempSet2 = set(self.layout[x][col].note) - {0}
                    if combo <= tempSet1 and combo <= tempSet2 and tempSet1 != tempSet2:
                        goodVal = 0
                        for tempVal in combo:
                            if self.singleColCheck([(a, col), (x, col)], {tempVal}) or self.singleBoxCheck([(a, col), (x, col)], {tempVal}):
                                goodVal = tempVal
                                break
                        if goodVal != 0:
                            eVal = combo - {goodVal}
                            eVal = eVal.pop()
                            self.layout[a][col].note[eVal-1] = 0
                            self.layout[x][col].note[eVal-1] = 0
                            if not self.stuck(tempCopy):
                                print(f"Removed {eVal} from roof nodes {(a, col), (x, col)} using col type 4a")
                                return
            else:
                for col in range(colOffset, colOffset + 3):
                    if col == b:
                        continue
                    tempSet1 = set(self.layout[a][col].note) - {0}
                    tempSet2 = set(self.layout[x][col].note) - {0}
                    if combo <= tempSet1 and combo <= tempSet2 and tempSet1 != tempSet2:
                        goodVal = 0
                        for tempVal in combo:
                            if self.singleColCheck([(a, col), (x, col)], {tempVal}):
                                goodVal = tempVal
                                break
                        if goodVal != 0:
                            eVal = combo - {goodVal}
                            eVal = eVal.pop()
                            self.layout[a][col].note[eVal-1] = 0
                            self.layout[x][col].note[eVal-1] = 0
                            if not self.stuck(tempCopy):
                                print(f"Removed {eVal} from roof nodes {(a, col), (x, col)} using col type 4b")
                                return
        # rule 5
        for (a, b), (x, y) in rowRPSets:
            # print(f"{combo} Row Remote Pairs: {(a, b), (x, y)}")
            tempSet1 = set(self.layout[a][y].note) - {0}
            tempSet2 = set(self.layout[x][b].note) - {0}
            if tempSet1 and tempSet2 and combo <= tempSet1 and combo <= tempSet2:
                for val in combo:
                    if self.singleRowCheck([(a, b), (a, y)], {val}) and self.singleColCheck([(a, b), (x, b)], {val}):
                        eVal = combo - {val}
                        eVal = eVal.pop()
                        self.layout[a][b].note[eVal-1] = 0
                    if self.singleRowCheck([(x, y), (x, b)], {val}) and self.singleColCheck([(x, y), (a, y)], {val}):
                        eVal = combo - {val}
                        eVal = eVal.pop()
                        self.layout[x][y].note[eVal-1] = 0
                    if not self.stuck(tempCopy):
                        print(f"removed {eVal} from row RP nodes {(a, b), (x, y)}")
                        return
        for (a, b), (x, y) in colRPSets:
            # print(f"{combo} Col Remote Pairs: {(a, b), (x, y)}")
            tempSet1 = set(self.layout[a][y].note) - {0}
            tempSet2 = set(self.layout[x][b].note) - {0}
            if tempSet1 and tempSet2 and combo <= tempSet1 and combo <= tempSet2:
                for val in combo:
                    if self.singleRowCheck([(a, b), (a, y)], {val}) and self.singleColCheck([(a, b), (x, b)], {val}):
                        eVal = combo - {val}
                        eVal = eVal.pop()
                        self.layout[a][b].note[eVal-1] = 0
                    if self.singleRowCheck([(x, y), (x, b)], {val}) and self.singleColCheck([(x, y), (a, y)], {val}):
                        eVal = combo - {val}
                        eVal = eVal.pop()
                        self.layout[x][y].note[eVal-1] = 0
                    if not self.stuck(tempCopy):
                        print(f"removed {eVal} from row RP nodes {(a, b), (x, y)}")
                        return

    def urLoopCheck(self, typeof, combo, roof, masterSet = None, coordList=None):
        if coordList is None:
            coordList = list(roof)
        if masterSet is None:
            masterSet = set()
            for r, c in roof:
                masterSet |= set(self.layout[r][c].note) - {0} - combo
            print(f"Starting With:\nCoordList: {coordList}\nMasterSet: {masterSet}\n")
        foundNew = False
        currentRow, currentCol = coordList[-1]
        
        match typeof:
            case 'row':
                for col in range(9):
                    if (currentRow, col) in coordList or self.layout[currentRow][col].val != 0:
                        continue
                    tempSet = set(self.layout[currentRow][col].note) - {0}
                    if not tempSet or len(tempSet & combo) != 0:
                        continue
                    newMaster = masterSet | tempSet
                    newCoords = coordList + [(currentRow, col)]
                    if len(newCoords) >= 3 and len(newMaster) == len(newCoords) - 1:
                        return True, newCoords, newMaster
                    # print(f"Iterating Through:\nCoordList: {coordList}\nMasterSet: {masterSet}\n")
                    result = self.urLoopCheck('row', combo, [(currentRow, col)], newMaster, newCoords)
                    if result[0]:
                        return result
                return False, coordList, masterSet

            case 'col':
                for row in range(9):
                    if (row, currentCol) in coordList or self.layout[row][currentCol].val != 0 or self.softlinelockedy[row][currentCol]:
                        continue
                    tempSet = set(self.layout[row][currentCol].note) - {0}
                    if not tempSet or len(tempSet & combo) != 0:
                        continue
                    newMaster = masterSet | tempSet
                    newCoords = coordList + [(row, currentCol)]
                    if len(newCoords) >= 3 and len(newMaster) == len(newCoords) - 1:
                        return True, newCoords, newMaster
                    result = self.urLoopCheck('col', combo, [(row, currentCol)], newMaster, newCoords)
                    if result[0]:
                        return result
                return False, coordList, masterSet

            case 'box':
                boxRowStart = (currentRow // 3) * 3
                boxColStart = (currentCol // 3) * 3
                for r in range(boxRowStart, boxRowStart + 3):
                    for c in range(boxColStart, boxColStart + 3):
                        if (r, c) in coordList or self.layout[r][c].val != 0:
                            continue
                        tempSet = set(self.layout[r][c].note) - {0}
                        if not tempSet or len(tempSet & combo) != 0:
                            continue
                        newMaster = masterSet | tempSet
                        newCoords = coordList + [(r, c)]
                        if len(newCoords) >= 3 and len(newMaster) == len(newCoords) - 1:
                            return True, newCoords, newMaster
                        result = self.urLoopCheck('box', combo, [(r, c)], newMaster, newCoords)
                        if result[0]:
                            return result
                return False, coordList, masterSet
    # ********************************************************************************************************************
    def tridagonUtil(self):
        tempCopy = copy.deepcopy(self)
        remaining = {v for r in range(9) for c in range(9) for v in self.layout[r][c].note if v != 0}
        # print(remaining)
        for combo in itertools.combinations(remaining, 3):
            self.tridagon(set(combo), tempCopy)
            if not self.stuck(tempCopy):
                return
    def tridagon(self, combo, tempCopy):
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
                    # else:
                    #     print(f"{combo} {(rBox, cBox)}: Bad ascending root\n")
                        
                rootPattern = self.getDscPattern((rBox, cBox), combo)
                if rootPattern is not None and len(rootPattern) >= 3:
                    if not any(len(set(self.layout[r][c].note) - {0} - combo) > 0 for (r, c) in rootPattern):
                        # print(f"Descending {combo} root {(rBox, cBox)}: {rootPattern}")
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
                    # else:
                    #     print(f"{combo} {(rBox, cBox)}: Bad descending root\n")
                
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
        remaining = set()
        for i in range(9):
            for j in range(9):
                remaining = remaining.union(set(self.layout[i][j].note))
        remaining.discard(0)
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
        remaining = {v for r in range(9) for c in range(9) for v in self.layout[r][c].note if v != 0}
        for combo in itertools.combinations(remaining, 3):
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
        remaining = {v for r in range(9) for c in range(9) for v in self.layout[r][c].note if v != 0}
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

























