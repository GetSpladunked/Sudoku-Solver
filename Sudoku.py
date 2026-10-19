import itertools
import traceback
import copy
import time
import json
import re
from IPython.display import clear_output
from collections import deque, Counter, defaultdict

deepCopyCount = 0
goodSolveCount = 0
deadEndsCount = 0
stratCallCount = 0
iterationCount = 0
nodesPruned = 0
timers = {}
pruneType = None
currentStrat = "other"
_someCache = {}

def updateDisplay():
    # clear_output(wait=True)
    # print(f"Good Solutions:      {goodSolveCount}")
    # print(f"Dead Ends:           {deadEndsCount}")
    # print(f"Deep Copies:         {deepCopyCount}")
    # print(f"Iterations:          {iterationCount}")
    # print(f"Nodes Pruned:        {nodesPruned}")
    # print(f"Cleanup Time:        {cleanupTime:.3f}s")
    # print(f"DeepCopy Time:       {deepCopyTime:.3f}s")
    # print(f"Merge Time:          {mergeTime:.3f}s")
    # print(f"Restructure Time:    {restructureTime:.3f}s")
    # header = f"  {'Strategy':<35} {'Copies':>7} {'Calls':>7} {'Time':>10}"
    # print(header)
    # print("  " + "-" * (len(header) - 2))
    # for strat, data in sorted(timers.items()):
    #     copies = data['copies'] if isinstance(data, dict) else data
    #     calls  = data['calls']  if isinstance(data, dict) else "-"
    #     time_  = f"{data['time']:.3f}s" if isinstance(data, dict) else "-"
    #     print(f"  {strat:<35} {copies:>7} {calls:>7} {time_:>10}")
    return

def solve(puzzle, correctSoln, pruneTypeParam):
    global iterationCount, goodSolveCount, deadEndsCount, pruneType, currentStrat, nodesPruned, cleanupTime, deepCopyTime, mergeTime, restructureTime
    pruneType = pruneTypeParam
    cleanupTime = deepCopyTime = mergeTime = restructureTime = 0.0
    badSolvePile, goodSolvePile, deadEnds = [], [], []
    stratNames = ['xWing', 'chuteRemotePairs', 'simpleColoring', 'wWing', 'yWing', 
                 'rectangleElimination', 'swordfish', 'xyzWing', 'xCycles', 
                 'medusa3D', 'jellyfish', 'uniqueRectangles', 'tridagon', 'fireworks',
                 'twinXYChains', 'skLoops', 'extUniqueRectangles', 'hiddenUniqueRectangles']
                 # 'wxyzWing']
    startTime = time.perf_counter()
    puzzle.updateAllNotes()
    # puzzle.addToBothStrategies("Init Update Notes", time.perf_counter() - startTime)
    puzzle.basicCleanup()
    
    root = SudokuNode(puzzle)
    queue = deque([root])
    allNodes = {root.puzzle.stringRepAll(): root}
    puzzle.displayAllToFullReport()
    baseCopy = copy.deepcopy(puzzle)
    while queue:
        current_node = queue.popleft()
        currentPuzzle = current_node.puzzle
        
        if not currentPuzzle.compare(correctSoln):
            badSolvePile.append(currentPuzzle)
            break
        
        iterationCount += 1
        if not baseCopy.stuck(currentPuzzle):
            _t = time.perf_counter()
            baseCopy = copy.deepcopy(currentPuzzle)
            deepCopyTime += time.perf_counter() - _t
        
        # ConcatStrats = [currentPuzzle.xWing, currentPuzzle.chuteRemotePairs, currentPuzzle.simpleColoring, currentPuzzle.wWing, currentPuzzle.yWing, currentPuzzle.rectangleElimination, currentPuzzle.swordfish, currentPuzzle.xyzWing, currentPuzzle.xCycles, currentPuzzle.medusa3D, currentPuzzle.jellyfish, currentPuzzle.uniqueRectangles, currentPuzzle.tridagon, currentPuzzle.fireworks, currentPuzzle.twinXYChains, CurrentPuzzle.SKLoops]
        newPuzzles = []
        
        for stratName in stratNames:
            strat = getattr(currentPuzzle, stratName)
            currentStrat = stratName
            stratStart = time.perf_counter()
            baseCopy, potentialMoves = strat(baseCopy, current_node)
            stratTime = time.perf_counter() - stratStart
            if currentStrat not in timers:
                timers[currentStrat] = {"copies": 0, "calls": 0, "time": 0.0}
            timers[currentStrat]["calls"] += 1
            timers[currentStrat]["time"] += stratTime
            if potentialMoves:
                newPuzzles.extend(potentialMoves)
        currentStrat = "other"

        if not newPuzzles:
            deadEnds.append(currentPuzzle)
            current_node.nodeType = "deadEnd"
            deadEndsCount += 1
            continue

        badPuzzleFound = False
        for newPuzzle in newPuzzles:
            if not newPuzzle.compare(correctSoln):
                badSolvePile.append(newPuzzle)
                badPuzzleFound = True
                break
        if badPuzzleFound:
            break

        currentStrat = "cleanup"
        for newPuzzle in newPuzzles:
            _t = time.perf_counter()
            newPuzzle.basicCleanup()
            delta = time.perf_counter() - _t
            cleanupTime += delta
            if currentStrat not in timers:
                timers[currentStrat] = {"copies": 0, "calls": 0, "time": 0.0}
            timers[currentStrat]["calls"] += 1
            timers[currentStrat]["time"] += delta
            newPuzzle.displayAllToFullReport()

            if newPuzzle.solved():
                goodSolvePile.append(newPuzzle)
                goodSolveCount += 1
                tempNode = addNode(newPuzzle, current_node, None, "solved")
                addSolvableMove(tempNode)
                continue
            
            existingNode = allNodes.get(newPuzzle.stringRepAll())
            if existingNode:
                current_node.add_child(existingNode)
                for move in current_node.solvableMoves:
                    if move not in existingNode.solvableMoves:
                        existingNode.solvableMoves.append(move)
                for child in existingNode.children:
                    for move in current_node.solvableMoves:
                        if move not in child.solvableMoves:
                            child.solvableMoves.append(move)
                for entry in newPuzzle.condReport:
                    if entry not in existingNode.puzzle.condReport:
                        existingNode.puzzle.condReport.append(entry)
                nodesPruned += 1
                _t = time.perf_counter()
                baseCopy = copy.deepcopy(currentPuzzle)
                deepCopyTime += time.perf_counter() - _t
                allNodes[newPuzzle.stringRepAll()] = existingNode
                continue
            
            newNode = addNode(newPuzzle, current_node, queue, "branch")
            allNodes[newPuzzle.stringRepAll()] = newNode
        currentStrat = "other"
        updateDisplay()

    seen = set()
    uniqueSolutions = []
    for soln in goodSolvePile:
        key = soln.stringRep()
        if key not in seen:
            seen.add(key)
            uniqueSolutions.append(soln)

    # ── Post-solve: merge solved nodes ────────────────────────────────────
    _t = time.perf_counter()
    solvedNodes = findAllSolvedNodes(root)
    preCleanupMap = {}
    for node in solvedNodes:
        for parentSnapshot, currentSnapshot in node.puzzle.condReport:
            preKey = "".join(
                str(currentSnapshot["currentValGrid"][r][c]) for r in range(9) for c in range(9)
            ) + "".join(
                str(currentSnapshot["currentNoteGrid"][r][c][x]) for r in range(9) for c in range(9) for x in range(9)
            )
            if preKey not in preCleanupMap:
                preCleanupMap[preKey] = node
            else:
                existingNode = preCleanupMap[preKey]
                for parent in node.parents:
                    parent.add_child(existingNode)
                    if node in parent.children:
                        parent.children.remove(node)
                for entry in node.puzzle.condReport:
                    if entry not in existingNode.puzzle.condReport:
                        existingNode.puzzle.condReport.append(entry)
                if node in goodSolvePile:
                    goodSolvePile.remove(node)
    mergeTime += time.perf_counter() - _t

    # ── Post-solve: reorder solved nodes ──────────────────────────────────
    _t = time.perf_counter()
    for node in findAllSolvedNodes(root):
        if len(node.parents) > 1:
            bestParent = max(node.parents, key=lambda p: (p.layer, p.uid))
            for parent in node.parents:
                if node in parent.children:
                    parent.children.remove(node)
            bestParent.children.insert(0, node)
            for parent in node.parents:
                if parent != bestParent and node not in parent.children:
                    parent.children.append(node)
    restructureTime += time.perf_counter() - _t

    # ── Post-solve: reorder branch nodes ──────────────────────────────────
    _t = time.perf_counter()
    for node in findAllBranchNodes(root):
        if len(node.parents) > 1:
            bestParent = max(node.parents, key=lambda p: (p.layer, p.uid))
            for parent in node.parents:
                if node in parent.children:
                    parent.children.remove(node)
            bestParent.children.insert(0, node)
            for parent in node.parents:
                if parent != bestParent and node not in parent.children:
                    parent.children.append(node)
    restructureTime += time.perf_counter() - _t

    updateDisplay()
    if badSolvePile:
        print("**************************\n**************************\n**************************\n    YOUR BOY FUCKED UP\n**************************\n**************************\n**************************\n")
    return goodSolvePile, badSolvePile, deadEnds, root, uniqueSolutions
    
# def solve(puzzle, correctSoln, pruneTypeParam):
#     global iterationCount, goodSolveCount, deadEndsCount, pruneType, currentStrat, nodesPruned
#     pruneType = pruneTypeParam
#     badSolvePile, goodSolvePile, deadEnds = [], [], []
    
#     startTime = time.perf_counter()
#     puzzle.updateAllNotes()
#     puzzle.addToBothStrategies("Init Update Notes", time.perf_counter() - startTime)
#     puzzle.basicCleanup()
    
#     root = SudokuNode(puzzle)
#     queue = deque([root])
#     allNodes = {root.puzzle.stringRepAll(): root}
#     puzzle.displayAllToFullReport()
#     baseCopy = copy.deepcopy(puzzle)
#     while queue:
#         current_node = queue.popleft()
#         # print(f"Processing uid={current_node.uid}, queue size={len(queue)}")
#         currentPuzzle = current_node.puzzle
        
#         if not currentPuzzle.compare(correctSoln):
#             badSolvePile.append(currentPuzzle)
#             # continue
#             break
        
#         iterationCount += 1
#         if not baseCopy.stuck(currentPuzzle):
#             baseCopy = copy.deepcopy(currentPuzzle)
        
#         ConcatStrats = [currentPuzzle.xWing, currentPuzzle.chuteRemotePairs, currentPuzzle.simpleColoring, currentPuzzle.wWing, currentPuzzle.yWing, currentPuzzle.rectangleElimination, currentPuzzle.swordfish, currentPuzzle.xyzWing, currentPuzzle.xCycles, currentPuzzle.medusa3D, currentPuzzle.jellyfish, currentPuzzle.uniqueRectangles, currentPuzzle.tridagon, currentPuzzle.fireworks]
#         newPuzzles = []
        
#         for strat in ConcatStrats:
#             currentStrat = strat.__name__
#             stratStart = time.perf_counter()
#             baseCopy, potentialMoves = strat(baseCopy, current_node)
#             stratTime = time.perf_counter() - stratStart
#             if currentStrat not in timers:
#                 timers[currentStrat] = {"copies": 0, "calls": 0, "time": 0.0}
#             timers[currentStrat]["calls"] += 1
#             timers[currentStrat]["time"] += stratTime
#             if potentialMoves:
#                 newPuzzles.extend(potentialMoves)
#         currentStrat = "other"
#         # print(f"node uid={current_node.uid} newPuzzles count={len(newPuzzles)}")
#         if not newPuzzles:
#             deadEnds.append(currentPuzzle)
#             current_node.nodeType = "deadEnd"
#             deadEndsCount += 1
#             continue

#         badPuzzleFound = False
#         for newPuzzle in newPuzzles:
#             if not newPuzzle.compare(correctSoln):
#                 badSolvePile.append(newPuzzle)
#                 badPuzzleFound = True
#                 break
#         if badPuzzleFound:
#             break

#         currentStrat = "cleanup"
#         for newPuzzle in newPuzzles:
#             newPuzzle.basicCleanup()
#             if currentStrat not in timers:
#                 timers[currentStrat] = {"copies": 0, "calls": 0, "time": 0.0}
#             timers[currentStrat]["calls"] += 1
#             timers[currentStrat]["time"] += stratTime
#             newPuzzle.displayAllToFullReport()
#             # print(f"After cleanup: {newPuzzle.stringRep()}")
#             if newPuzzle.solved():
#                 goodSolvePile.append(newPuzzle)
#                 goodSolveCount += 1
#                 tempNode = addNode(newPuzzle, current_node, None, "solved")
#                 addSolvableMove(tempNode)
#                 continue
            
#             existingNode = allNodes.get(newPuzzle.stringRepAll())
#             if existingNode:
#                 current_node.add_child(existingNode)
#                 for move in current_node.solvableMoves:
#                     if move not in existingNode.solvableMoves:
#                         existingNode.solvableMoves.append(move)
#                 for child in existingNode.children:
#                     for move in current_node.solvableMoves:
#                         if move not in child.solvableMoves:
#                             child.solvableMoves.append(move)
#                 for entry in newPuzzle.condReport:
#                     if entry not in existingNode.puzzle.condReport:
#                         existingNode.puzzle.condReport.append(entry)
#                 nodesPruned += 1
#                 baseCopy = copy.deepcopy(currentPuzzle)
#                 allNodes[newPuzzle.stringRepAll()] = existingNode
#                 continue
            
#             newNode = addNode(newPuzzle, current_node, queue, "branch")
#             allNodes[newPuzzle.stringRepAll()] = newNode
#             # print(f"Added new node uid={newNode.uid}, stringRep={newPuzzle.stringRep()}")
#         currentStrat = "other"
#     seen = set()
#     uniqueSolutions = []
#     for soln in goodSolvePile:
#         key = soln.stringRep()
#         if key not in seen:
#             seen.add(key)
#             uniqueSolutions.append(soln)

#     # # ── Post-solve: merge branch nodes with identical pre-cleanup states ───
#     # # Comment out this block to disable
#     # branchNodes = findAllBranchNodes(root)
#     # branchPreCleanupMap = {}
#     # for node in branchNodes:
#     #     for parentSnapshot, currentSnapshot in node.puzzle.condReport:
#     #         preKey = "".join(
#     #             str(currentSnapshot["currentValGrid"][r][c]) for r in range(9) for c in range(9)
#     #         ) + "".join(
#     #             str(currentSnapshot["currentNoteGrid"][r][c][x]) for r in range(9) for c in range(9) for x in range(9)
#     #         )
#     #         if preKey not in branchPreCleanupMap:
#     #             branchPreCleanupMap[preKey] = node
#     #         else:
#     #             existingNode = branchPreCleanupMap[preKey]
#     #             for parent in node.parents:
#     #                 parent.add_child(existingNode)
#     #                 if node in parent.children:
#     #                     parent.children.remove(node)
#     #             for child in node.children:
#     #                 existingNode.add_child(child)
#     #             for entry in node.puzzle.condReport:
#     #                 if entry not in existingNode.puzzle.condReport:
#     #                     existingNode.puzzle.condReport.append(entry)

#     # # Reorder: ensure highest-layer parent owns the branch node in the primary hierarchy
#     # for node in findAllBranchNodes(root):
#     #     if len(node.parents) > 1:
#     #         bestParent = max(node.parents, key=lambda p: (p.layer, p.uid))
#     #         for parent in node.parents:
#     #             if node in parent.children:
#     #                 parent.children.remove(node)
#     #         bestParent.children.insert(0, node)
#     #         for parent in node.parents:
#     #             if parent != bestParent and node not in parent.children:
#     #                 parent.children.append(node)
#     # # ── End post-solve branch merge ────────────────────────────────────────

#     # ── Post-solve: reorder branch nodes by highest-layer parent ───────────
#     # Comment out this block to disable
#     for node in findAllBranchNodes(root):
#         if len(node.parents) > 1:
#             bestParent = max(node.parents, key=lambda p: (p.layer, p.uid))
#             for parent in node.parents:
#                 if node in parent.children:
#                     parent.children.remove(node)
#             bestParent.children.insert(0, node)
#             for parent in node.parents:
#                 if parent != bestParent and node not in parent.children:
#                     parent.children.append(node)
#     # ── End post-solve branch reorder ──────────────────────────────────────
    
#     # ── Post-solve: merge solved nodes with identical pre-cleanup states ───
#     # Comment out this block to disable
#     solvedNodes = findAllSolvedNodes(root)
#     preCleanupMap = {}
#     for node in solvedNodes:
#         for parentSnapshot, currentSnapshot in node.puzzle.condReport:
#             preKey = "".join(
#                 str(currentSnapshot["currentValGrid"][r][c]) for r in range(9) for c in range(9)
#             ) + "".join(
#                 str(currentSnapshot["currentNoteGrid"][r][c][x]) for r in range(9) for c in range(9) for x in range(9)
#             )
#             if preKey not in preCleanupMap:
#                 preCleanupMap[preKey] = node
#             else:
#                 existingNode = preCleanupMap[preKey]
#                 for parent in node.parents:
#                     parent.add_child(existingNode)
#                     if node in parent.children:
#                         parent.children.remove(node)
#                 for entry in node.puzzle.condReport:
#                     if entry not in existingNode.puzzle.condReport:
#                         existingNode.puzzle.condReport.append(entry)
#                 if node in goodSolvePile:
#                     goodSolvePile.remove(node)
    
#     # Reorder: ensure highest-layer parent owns the solved node in the primary hierarchy
#     for node in findAllSolvedNodes(root):
#         if len(node.parents) > 1:
#             bestParent = max(node.parents, key=lambda p: (p.layer, p.uid))
#             # remove node from all parents' children lists
#             for parent in node.parents:
#                 if node in parent.children:
#                     parent.children.remove(node)
#             # re-add to best parent first so D3 sees it as primary
#             bestParent.children.insert(0, node)
#             # re-add to remaining parents
#             for parent in node.parents:
#                 if parent != bestParent and node not in parent.children:
#                     parent.children.append(node)
#     # ── End post-solve merge ───────────────────────────────────────────────

def findAllSolvedNodes(root, visited=None):
    if visited is None:
        visited = set()
    if id(root) in visited:
        return []
    visited.add(id(root))
    result = []
    if root.nodeType == "solved":
        result.append(root)
    for child in root.children:
        result.extend(findAllSolvedNodes(child, visited))
    return result
    
def findAllBranchNodes(root, visited=None):
    if visited is None:
        visited = set()
    if id(root) in visited:
        return []
    visited.add(id(root))
    result = []
    if root.nodeType == "branch":
        result.append(root)
    for child in root.children:
        result.extend(findAllBranchNodes(child, visited))
    return result

# "X-Wing Row"
# "Chute Remote Pairs Row"
# "Simple Coloring Rule 2"
# "Simple Coloring Rule 4"
# "W-Wing"
# "Y-Wing Square"
# "Y-Wing Box (Row)"
# "Y-Wing Box (Col)"
# "Rectangle Elimination Row"
# "Rectangle Elimination Col"
# "Swordfish Row"
# "Swordfish Col"
# "XYZ-Wing L"
# "XYZ-Wing Box (Row)"
# "XYZ-Wing Box (Col)"
# "X-Cycles Type 1"
# "X-Cycles Type 2"
# "X-Cycles Type 3"
# "3D Medusa Rule 1"
# "3D Medusa Rule 2"
# "3D Medusa Rule 3"
# "3D Medusa Rule 4"
# "3D Medusa Rule 5"
# "3D Medusa Rule 6"
# "Jellyfish Row"
# "Jellyfish Col"
# "Unique Rectangles Row 1"
# "Unique Rectangles Row 2A"
# "Unique Rectangles Row 3B"
# "Unique Rectangles Row 3/3B"
# "Unique Rectangles Row 4A"
# "Unique Rectangles Row 2B"
# "Unique Rectangles Row 3A"
# "Unique Rectangles Row 4B"
# AND COL ^^^
# val/noteList format: [(idx + 1, (r, c))]
def uberPrune(parentNode, newMove):
    global pruneType
    strat, group, eNodes, valNodes = newMove
    newPuzzle = parentNode.puzzle
    allSolvableMoves = []
    if pruneType == 0:
        return False
    for parent in parentNode.parents:
        allSolvableMoves.extend(parent.solvableMoves)
    # also include parentNode's own solvableMoves
    allSolvableMoves.extend(parentNode.solvableMoves)
    if pruneType == 1:
        for sStrat, sGroup, sValDiff, sNoteDiff, parentNode in allSolvableMoves:
            if sStrat != strat: continue
            if "X-Wing" in strat:
                if group == sGroup and eNodes <= set(sNoteDiff): 
                    return True
            elif "Chute Remote Pairs" in strat:
                if group == sGroup and eNodes <= set(sNoteDiff):
                    return True
            elif "Simple Coloring" in strat:
                sGroupNodes = {(r, c) for sLayer in sGroup for r, c in sLayer}
                newGroupNodes = {(r, c) for layer in group for r, c in layer}
                if not newGroupNodes <= sGroupNodes:
                    continue
                sGroupLayers = [{(r, c) for r, c in sLayer} for sLayer in sGroup]
                newGroupLayers = [{(r, c) for r, c in layer} for layer in group]
                layerMatch = True
                for newLayer in newGroupLayers:
                    goodLayer = False
                    for oldLayer in sGroupLayers:
                        if not newLayer <= oldLayer:
                            continue
                        if newLayer == oldLayer:
                            goodLayer = True
                            break
                        missingFromNew = oldLayer - newLayer
                        if all(newPuzzle.layout[r][c].note[val-1] == 0 for r, c in missingFromNew):
                            goodLayer = True
                            break
                    if not goodLayer:
                        layerMatch = False
                        break
                if not layerMatch:
                    continue
                if eNodes <= set(sNoteDiff):
                    return True
            elif "W-Wing" in strat:
                if group == sGroup and eNodes <= set(sNoteDiff):
                    return True
            elif "Y-Wing" in strat:
                if group == sGroup and eNodes <= set(sNoteDiff):
                    return True
            elif "Rectangle Elimination" in strat:
                if group == sGroup and eNodes <= set(sNoteDiff):
                    return True
            elif "Swordfish" in strat:
                if group == sGroup and eNodes <= set(sNoteDiff):
                    return True
            elif "XYZ-Wing" in strat:
                if group == sGroup and eNodes <= set(sNoteDiff):
                    return True
            elif "X-Cycles" in strat:
                if group == sGroup and eNodes <= set(sNoteDiff):
                    return True
            elif "3D Medusa" in strat:
                # uses the full Simple Coloring / 3D Medusa group comparison logic
                sGroupNodes = {(r, c, v) for sLayer in sGroup for r, c, v in sLayer}
                newGroupNodes = {(r, c, v) for layer in group for r, c, v in layer}
                if not newGroupNodes <= sGroupNodes:
                    continue
                sGroupLayers = [{(r, c, v) for r, c, v in sLayer} for sLayer in sGroup]
                newGroupLayers = [{(r, c, v) for r, c, v in layer} for layer in group]
                layerMatch = True
                for newLayer in newGroupLayers:
                    goodLayer = False
                    for oldLayer in sGroupLayers:
                        if not newLayer <= oldLayer:
                            continue
                        if newLayer == oldLayer:
                            goodLayer = True
                            break
                        missingFromNew = oldLayer - newLayer
                        if all(newPuzzle.layout[r][c].note[v-1] == 0 for r, c, v in missingFromNew):
                            goodLayer = True
                            break
                    if not goodLayer:
                        layerMatch = False
                        break
                if not layerMatch:
                    continue
                if eNodes <= set(sNoteDiff):
                    return True
            elif "Jellyfish" in strat:
                if group == sGroup and eNodes <= set(sNoteDiff):
                    return True
            elif "Unique Rectangles" in strat:
                if group == sGroup and eNodes <= set(sNoteDiff):
                    return True
        return False
            
                

def diffString(valList, noteList):
    parts = []
    if valList:
        valStr = "\n".join(f"{val} at {coords}" for val, coords in valList)
        parts.append(f"Values placed:\n{valStr}")
    if noteList:
        # Group by value
        noteGroups = {}
        for val, coords in noteList:
            if val not in noteGroups:
                noteGroups[val] = []
            noteGroups[val].append(coords)
        noteStr = "\n".join(f"{val} at {', '.join(str(c) for c in coords)}" for val, coords in sorted(noteGroups.items()))
        parts.append(f"Notes removed:\n{noteStr}")
    return "\n".join(parts)

# def addSolvableMove(current_node):
#     currentPuzzle = current_node.puzzle
#     _, currentSnapshot = currentPuzzle.condReport[0]
#     solvableMove = (
#         currentSnapshot["strategy"],
#         currentSnapshot["group"],
#         currentSnapshot["valDiff"],
#         currentSnapshot["noteDiff"],
#         parent_node
#     )
#     parent_node.solvableMoves.append(solvableMove)
#     for child in parent_node.children:
#         child.solvableMoves.append(solvableMove)

def addSolvableMove(current_node):
    if not current_node.parents:
        return
    currentPuzzle = current_node.puzzle
    _, currentSnapshot = currentPuzzle.condReport[0]
    parent_node = current_node.parents[0]
    solvableMove = (
        currentSnapshot["strategy"],
        currentSnapshot["group"],
        currentSnapshot["valDiff"],
        currentSnapshot["noteDiff"],
        parent_node
    )
    parent_node.solvableMoves.append(solvableMove)
    for child in parent_node.children:
        child.solvableMoves.append(solvableMove)

def addNode(puzzle, parent_node, queue, nodeType="branch"):
    newNode = SudokuNode(puzzle)
    newNode.nodeType = nodeType
    newNode.solvableMoves = parent_node.solvableMoves[:]
    parent_node.add_child(newNode)
    if queue is not None:
        queue.append(newNode)
        # print(f"addNode: uid={newNode.uid} added to queue, queue size={len(queue)}")
    return newNode
# def addNode(puzzle, parent_node, queue):
#     newNode = SudokuNode(puzzle)
#     newNode.solvableMoves = parent_node.solvableMoves[:]
#     parent_node.add_child(newNode)
#     if queue is not None:
#         queue.append(newNode)
#     return newNode

class SudokuNode:
    _counter = 0
    def __init__(self, puzzle, nodeType="root"):
        self.puzzle = puzzle
        self.children = []
        self.parents = []
        self.solvableMoves = []
        self.layer = 0
        self.nodeType = nodeType
        SudokuNode._counter += 1
        self.uid = SudokuNode._counter
    def add_child(self, child_node):
        # child_node.parent = self
        if child_node not in self.children:
            self.children.append(child_node)
        if self not in child_node.parents:
            child_node.parents.append(self)
            if len(child_node.parents) == 1:  # only set layer on first parent
                child_node.layer = self.layer + 1
        # child_node.layer = min(p.layer for p in child_node.parents) + 1
    
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
            if self.val != 0: self.note = [0,0,0,0,0,0,0,0,0]
        # setval changes the value of the current Node and changes the notes for the current node to a list of 9 0's
        # then it calls updateNotes on the problem to remove the current value from all nodes in its x & y axis as well as the box it resides in
        def setVal(self, hardVal, idx):
            self.val = hardVal
            self.note = [0,0,0,0,0,0,0,0,0]
            self.problem.singleLockReset(idx)
            self.problem.setLocks(idx[0], idx[1])
            self.problem.updateAllNotes()
        def equals(self, x):
            return self.val == x.val and all(self.note[i] == x.note[i] for i in range(9))
            
    # The problem class has 5 data structures, 
    # layout: a 9x9 grid of the node objects 
    # locked: a 9x9 bool grid that represents if a node has more than 2 locked attributes
    # softboxlocked: a 9x9 bool grid that represents if a box has two or more nodes with ironed out possibilities, used for filtering out unecessary searches
    # softlinelockedx: a 9x9 bool grid that represents if a row has two or more nodes with ironed out possibilities
    # soflinelockedy: a 9x9 bool grid that represents if a column has two or more nodes with ironed out possibilities
    # all of these are initialized with an initial layout, all lockeded data structures will be initialized to False and changed to true if a node has a value
    # after initialization it will call the update notes function to get rid of incorrect guesses for a node
    def __init__(self, initLayout, time = 0):
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
                if val: self.locked[r][c] = self.softboxlocked[r][c] = self.softlinelockedx[r][c] = self.softlinelockedy[r][c] = True
        self.report = ""
        self.fullReport = ""
        self.usedStrategies = []
        self.allStrategies = []
        self.condReport = []
        self.timer = 0
        self.totalTime = 0

    def __deepcopy__(self, memo):
        global deepCopyCount, timers
        if currentStrat not in timers:
            timers[currentStrat] = {"copies": 0, "calls": 0, "time": 0.0}
        timers[currentStrat]["copies"] += 1
        
        new_puzzle = object.__new__(Puzzle)
        memo[id(self)] = new_puzzle
        new_puzzle.locked = [row[:] for row in self.locked]
        new_puzzle.softboxlocked = [row[:] for row in self.softboxlocked]
        new_puzzle.softlinelockedx = [row[:] for row in self.softlinelockedx]
        new_puzzle.softlinelockedy = [row[:] for row in self.softlinelockedy]
        new_puzzle.report = self.report
        new_puzzle.condReport = self.condReport[:]
        new_puzzle.fullReport = self.fullReport
        new_puzzle.usedStrategies = self.usedStrategies[:]
        new_puzzle.allStrategies = self.allStrategies[:]
        new_puzzle.timer = self.timer
        new_puzzle.totalTime = self.totalTime
        new_puzzle.layout = [[None for _ in range(9)] for _ in range(9)]
        for r in range(9):
            for c in range(9):
                node = self.layout[r][c]
                new_node = Puzzle.Node.__new__(Puzzle.Node)
                new_node.val = node.val
                new_node.note = node.note[:]
                new_node.problem = new_puzzle
                new_puzzle.layout[r][c] = new_node
        deepCopyCount += 1
        # updateDisplay()
        return new_puzzle
    def puzzleFlip(self, newPuzzle, note, strat, current_node, group = None):
        newPuzzle.addToBothReports(note + "\n\n")
        # newPuzzle.displayAllToReport()
        # newPuzzle.displayAllToFullReport()
        valDiff, noteDiff = self.puzzleDifferenceWithVals(newPuzzle)
        step = current_node.layer
        
        # snapshot the current state instead of storing the node reference
        parentSnapshot = {
            "valueGrid": [[self.layout[r][c].val for c in range(9)] for r in range(9)],
            "notesGrid": [[list(self.layout[r][c].note) for c in range(9)] for r in range(9)],
            "parentId": current_node.uid
        }
        currentSnapShot = {
            "currentValGrid": [[newPuzzle.layout[r][c].val for c in range(9)] for r in range(9)],
            "currentNoteGrid": [[list(newPuzzle.layout[r][c].note) for c in range(9)] for r in range(9)],
            "note": note,
            "strategy": strat,
            "group": group,
            "valDiff": valDiff,
            "noteDiff": noteDiff
        }
        newPuzzle.condReport = [(parentSnapshot, currentSnapShot)]
        
        # newPuzzle.addToBothStrategiesAndBothReports("Good: " + strat, time.perf_counter() - self.timer)
        newPuzzle.totalTime += time.perf_counter() - self.timer
        return copy.deepcopy(self), newPuzzle

    def singleLockReset(self, coords):
        i, j = coords
        rowOffset, colOffset = self.getOffset(i), self.getOffset(j)
        for row in range(9): self.softlinelockedy[row][j] = False
        for col in range(9): self.softlinelockedx[i][col] = False
        for row in range(rowOffset, rowOffset + 3): 
            for col in range(colOffset, colOffset + 3): self.softboxlocked[row][col] = False
    # sets locks if a value is found
    def setLocks(self, r, c):
        self.locked[r][c] = self.softboxlocked[r][c] = self.softlinelockedx[r][c] = self.softlinelockedy[r][c] = True
 
    # ********************************************************************************************************************
    # PRINT FUNCTIONS
    def display(self):
        print(self.displayPuzStringRep())
    
    def displayPuzStringRep(self):
        stringRep = ""
        for i in range(9):
            if i % 3 == 0 and i != 0: stringRep += "---------------------\n"
            for j in range(9):
                if j % 3 == 0 and j != 0: stringRep += "| "
                if self.layout[i][j].val != 0: stringRep += f"{self.layout[i][j].val} "
                else: stringRep += "  "
                if j == 8: stringRep += "\n"
        return stringRep + "\n"
    
    def notesDisplay(self):
        print(self.displayNotesStringRep())
    
    def displayNotesStringRep(self):
        stringRep = ""
        horizontal_line = "-" * 73
        for i in range(9):
            if i % 3 == 0 and i != 0: stringRep += horizontal_line + "\n"
            for note_row in range(3):
                for j in range(9):
                    if j % 3 == 0 and j != 0: stringRep += "| "
                    start = note_row * 3
                    end = start + 3
                    for k in range(start, end):
                        val = self.layout[i][j].note[k]
                        if self.layout[i][j].val != 0: stringRep += "0 "
                        else:
                            if val != 0: stringRep += f"{val} "
                            else: stringRep += "  "
                    if j != 8: stringRep += "| "
                stringRep += "\n"
            if i != 8: stringRep += "\n"
        return stringRep + "\n"
    
    def displayAll(self):
        print(self.displayPuzStringRep())
        print(self.displayNotesStringRep())
    
    def displayAllStringRep(self):
        return self.displayPuzStringRep() + self.displayNotesStringRep() + "\n"

    # Adds puzzle + notes to report only
    def displayAllToReport(self):
        self.report += self.displayAllStringRep()
    
    # Adds puzzle + notes to fullReport only
    def displayAllToFullReport(self):
        self.fullReport += self.displayAllStringRep()

    def displayAllToBothReports(self):
        self.displayAllToReport()
        self.displayAllToFullReport()
    
    # Adds string to both reports, then redraws puzzle + notes in fullReport only
    def addToBothReports(self, string):
        self.report += string
        self.fullReport += string

    def addToReports(self, string):
        self.report += string
        self.fullReport += string
    
    def addToBothStrategies(self, strat, tempTime):
        self.usedStrategies.append((strat, tempTime))
        self.allStrategies.append((strat, tempTime))

    def addToBothStrategiesAndBothReports(self, strat, tempTime):
        self.usedStrategies.append((strat, tempTime))
        self.allStrategies.append((strat, tempTime))
        entry = f"{strat}: {tempTime:.6f}s\n"
        self.report += entry
        self.fullReport += entry
        if not strat.startswith("Failed:") and not strat.startswith("Ignored:") and not strat.startswith("Not Cleaned Up"):
            self.fullReport += self.displayAllStringRep()
    
    def displayReport(self):
        print(self.report)
    
    def displayFullReport(self):
        print(self.fullReport)
    
    def displayUsedStrategies(self):
        print("Used Strategies")
        print(f"{'Strategy':<30} {'Time':>11}")
        print("-" * 42)
        subtotal = 0
        for strat, time in self.usedStrategies:
            if strat.startswith("Layer:") or strat.startswith("Solved!"):
                print(f"{strat:^41}")
            else:
                print(f"{strat:<30} {time:>10.6f}s")
                if strat.startswith("Cleaned Up") or strat.startswith("Good:"):
                    subtotal += time
        print(f"{'Subtotal':<30} {subtotal:>10.6f}s")
        print(f"{'Total':<30} {self.totalTime:>10.6f}s")
    
    def displayAllStrategies(self):
        print("All Strategies")
        print(f"{'Strategy':<30} {'Time':>11}")
        print("-" * 41)
        subtotal = 0
        for strat, time in self.allStrategies:
            if strat.startswith("Layer:"):
                print(f"{strat:^41}")
            else:
                print(f"{strat:<30} {time:>10.6f}s")
                if strat.startswith("Cleaned Up") or strat.startswith("Good:"):
                    subtotal += time
        print(f"{'Subtotal':<30} {subtotal:>10.6f}s")
        print(f"{'Total':<30} {self.totalTime:>10.6f}s")

    def softLockGridToFullReport(self, lockName, lockGrid):
        self.fullReport += f"\n{lockName}:\n"
        for r in range(9):
            self.fullReport += " ".join("T" if lockGrid[r][c] else "F" for c in range(9)) + "\n"
        self.fullReport += "\n"
    
    def stringRep(self):
        return "".join(str(self.layout[r][c].val or ".") for r in range(9) for c in range(9))
    def stringRepAll(self):
        vals = "".join(str(self.layout[r][c].val) if self.layout[r][c].val != 0 else "." for r in range(9) for c in range(9))
        notes = "".join(str(self.layout[r][c].note[x]) for r in range(9) for c in range(9) for x in range(9))
        return vals + notes
    # ********************************************************************************************************************
    # Update notes functions
    # the updateNotes function combs through all current values in the problem and removes the redundant notes from their rows, columns, and boxes 
    def updateAllNotes(self):
        for i in range(9):
            for j in range(9):
                x = self.layout[i][j].val
                if x == 0: continue
                for a in range(9):
                    if a != j: self.layout[i][a].note[x-1] = 0
                    if a != i: self.layout[a][j].note[x-1] = 0
                rowOffset, colOffset = self.getOffset(i), self.getOffset(j)
                for a in range(rowOffset, rowOffset + 3):
                    for b in range(colOffset, colOffset + 3):                           
                        self.layout[a][b].note[x-1] = 0
    
    def subUpdateNotes(self, x, coords, vals, fromLocks = False):
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
            if (i, j) in coords or self.locked[i][j]: continue
            for k in vals:
                self.layout[i][j].note[k-1] = 0
    # updates specific values (optimization purposes)
    def updateNotesDX(self, coordList, vals):
        for i, j in coordList:
            for eVal in vals: self.layout[i][j].note[eVal-1] = 0

    def updateNotesGX(self, eNodes):
        for eVal, coord in eNodes:
            self.layout[coord[0]][coord[1]].note[eVal-1] = 0
    
    def updateNotesIgnoreDX(self, coordList, vals):
        for i, j in coordList:
            eVals = {1, 2, 3, 4, 5, 6, 7, 8, 9} - set(vals)
            for eVal in eVals: self.layout[i][j].note[eVal-1] = 0

    # resets notes for generator
    def resetNotes(self):
        for i in range(9):
            for j in range(9):
                if self.locked[i][j]: continue
                for note in range(9):
                    self.layout[i][j].note[note] = note + 1
        for i in range(9):
            for j in range(9):
                if not self.locked[i][j]: continue
                val = {self.layout[i][j].val}
                self.subUpdateNotes('box', [(i, j)], val)
                self.subUpdateNotes('row', [(i, j)], val)
                self.subUpdateNotes('col', [(i, j)], val)
    # ********************************************************************************************************************
    # Termination & "stuck" binary functions, also a differenceCount function to determine the effectivity of changes made to a puzzle object
    # basic termination function
    def solved(self):
        for i in range(9):
            for j in range(9):
                if self.layout[i][j].val == 0: return False
        return True
    # conditional to determine if there are any differences between current build and a tempCopy
    def stuck(self, tempCopy):
        if not all(self.layout[i][j].equals(tempCopy.layout[i][j]) for i in range(9) for j in range(9)): return False
        return True
    
    def stuckCleanup(self, tempCopy):
        if not all(self.layout[i][j].equals(tempCopy.layout[i][j]) for i in range(9) for j in range(9)): return False
        if self.softboxlocked != tempCopy.softboxlocked or self.softlinelockedx != tempCopy.softlinelockedx or self.softlinelockedy != tempCopy.softlinelockedy:
            return False
        return True

    def stuckLock(self):
        return all(self.softboxlocked[i][j] and self.softlinelockedx[i][j] and self.softlinelockedy[i][j] for i in range(9) for j in range(9))

    def puzzleDifference(self, origCopy):
        return [(i, j) for i in range(9) for j in range(9) if not self.layout[i][j].equals(origCopy.layout[i][j])]
    
    def puzzleDifferenceWithVals(self, newPuzzle):
        valList = []
        noteList = []
        for r in range(9):
            for c in range(9):
                if self.layout[r][c].val != newPuzzle.layout[r][c].val:
                    valList.append((newPuzzle.layout[r][c].val, (r, c)))
                for idx in range(9):
                    if self.layout[r][c].note[idx] != newPuzzle.layout[r][c].note[idx]:
                        noteList.append((idx + 1, (r, c)))
        valList.sort(key=lambda x: x[0])
        noteList.sort(key=lambda x: x[0])
        return valList, noteList
        
    def differenceCount(self, origCopy):
        hardCount, softCount = 0, 0
        for i in range(9):
            for j in range(9):
                if origCopy.layout[i][j].val == 0 and self.layout[i][j].val == 0:
                    tempSet1 = set(origCopy.layout[i][j].note) - {0}
                    tempSet2 = set(self.layout[i][j].note) - {0}
                    softCount += len(tempSet1) - len(tempSet2)
                elif origCopy.layout[i][j].val == 0 and self.layout[i][j].val != 0: hardCount += 1
        return hardCount, softCount
        
    def compare(self, solvedArry):
        for i in range(9):
            for j in range(9):
                if self.layout[i][j].val == solvedArry[i][j]: continue
                if solvedArry[i][j] not in self.layout[i][j].note: return False
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
    def getBoxCoords(self, coords):
        return (self.getOffset(coords[0]), self.getOffset(coords[1]))
    
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
    def returnConnections(self, coordsList):
        x = []
        if self.inBox(coordsList):
            x.append("box")
        if self.inRow(coordsList):
            x.append("row")
        if self.inCol(coordsList):
            x.append("col")
        return x

    #SET STUFF
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

    # returns indexes of nodes whose notes are a subset of vals
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

    # returns indexes of nodes whose notes contain a subset of vals
    def getAnyBoxIdxs(self, pos, vals):
        r0, c0 = self.getOffset(pos[0]), self.getOffset(pos[1])
        return {(r, c) for r in range(r0, r0 + 3) for c in range(c0, c0 + 3) if vals <= self.getSet((r, c))}
    def getAnyRowIdxs(self, pos, vals):
        x, _ = pos
        return {(x, c) for c in range(9) if not self.locked[x][c] and vals <= self.getSet((x, c))}
    def getAnyColIdxs(self, pos, vals):
        _, y = pos
        return {(r, y) for r in range(9) if not self.locked[r][y] and vals <= self.getSet((r, y))}
    def getAnyConnectedIdxs(self, pos, vals):
        return self.getAnyBoxIdxs(pos, vals) | self.getAnyRowIdxs(pos, vals) | self.getAnyColIdxs(pos, vals)
    def getAnyPuzIdxs(self, vals):
        return {(r, c) for r in range(9) for c in range(9) if not self.locked[r][c] and vals <= self.getSet((r, y))}
    
    def getAnyTwos(self):
        result = {}
        for r in range(9):
            for c in range(9):
                s = self.getSet((r, c))
                if len(s) != 2: continue
                s = frozenset(s)
                if s not in result: result[s] = []
                result[s].append((r, c))
        return result

    def getAllIdxsOfLen(self, n):
        result = []
        for r in range(9):
            for c in range(9):
                if self.locked[r][c]: continue
                count = sum(1 for v in self.layout[r][c].note if v != 0)
                if count == n:
                    result.append((r, c))
        return result
    
    def checkLoopValidity(self, nodes, vals):
        check = {val: 0 for val in vals}
        for node in nodes:
            for val in self.getSet(node):
                if val in vals: check[val] += 1
        if all(check[val] >= len(vals) - 1 for val in vals): return True
        return False

    # returns if 2 nodes are in same row/col chute
    def sameRowChute(self, nodes):
        return all(n1[0]//3 == n2[0]//3 for n1, n2 in itertools.combinations(nodes, 2))
    def sameColChute(self, nodes):
        return all(n1[1]//3 == n2[1]//3 for n1, n2 in itertools.combinations(nodes, 2))

    def getAllBoxNotes(self, coords):
        boxX, boxY = self.getBoxCoords(coords)
        superNotes = []
        for r in range(boxX, boxX + 3):
            for c in range(boxY, boxY + 3):
                superNotes += self.layout[r][c].note
        return set(superNotes) - {0}
    def getAllRowNotes(self, coord):
        superNotes = []
        for c in range(9):
            superNotes += self.layout[coord][c].note
        return set(superNotes) - {0}
    def getAllColNotes(self, coord):
        superNotes = []
        for r in range(9):
            superNotes += self.layout[r][coord].note
        return set(superNotes) - {0}

    def getAllBoxCoords(self, coords):
        x, y = coords
        r0, c0 = self.getOffset(x), self.getOffset(y)
        return {(r, c) for r in range(r0, r0 + 3) for c in range(c0, c0 + 3)}
    def getAllRowCoords(self, coords):
        x, _ = coords
        return {(x, c) for c in range(9)}
    def getAllColCoords(self, coords):
        _, y = coords
        return {(r, y) for r in range(9)}
    def getAnyCoords(self, coords):
        return self.getAllBoxCoords(coords) | self.getAllRowCoords(coords) | self.getAllColCoords(coords)
    # ********************************************************************************************************************
    # ***********************************************BASIC STRATEGIES*****************************************************
    # ********************************************************************************************************************
    # def basicCleanup(self):
    #     startTime = time.perf_counter()
    #     self.cleanup()
    #     self.checkBoxLockIterator()
    #     self.checkRowLockIterator()
    #     self.checkColLockIterator()
    #     bugFired = self.bug()
    #     if (bugFired):
    #         self.cleanup()
    #     return bugFired
    def basicCleanup(self):
        global timers
        subTimers = {}

        
        _t = time.perf_counter()
        self.cleanup()
        subTimers['cleanup'] = time.perf_counter() - _t
        
        _t = time.perf_counter()
        self.checkBoxLockIterator()
        subTimers['checkBoxLock'] = time.perf_counter() - _t
        
        _t = time.perf_counter()
        self.checkRowLockIterator()
        subTimers['checkRowLock'] = time.perf_counter() - _t
        
        _t = time.perf_counter()
        self.checkColLockIterator()
        subTimers['checkColLock'] = time.perf_counter() - _t
        
        _t = time.perf_counter()
        bugFired = self.bug()
        subTimers['bug'] = time.perf_counter() - _t
        
        if bugFired:
            _t = time.perf_counter()
            self.cleanup()
            subTimers['cleanup2'] = time.perf_counter() - _t
        
        # accumulate into global timers
        for key, val in subTimers.items():
            fullKey = f"bc_{key}"
            if fullKey not in timers:
                timers[fullKey] = {"copies": 0, "calls": 0, "time": 0.0}
            timers[fullKey]["calls"] += 1
            timers[fullKey]["time"] += val
            
        return bugFired
    
    # def basicCleanup(self):
    #     global timers
    #     subTimers = {}
    #     bugFired = False
 
    #     def timed(key, fn):
    #         _t = time.perf_counter()
    #         result = fn()
    #         subTimers[key] = subTimers.get(key, 0.0) + (time.perf_counter() - _t)
    #         return result
 
    #     # repeat until a full pass changes nothing, so eliminations from one
    #     # step (e.g. the col lock) get picked up by the others
    #     while True:
    #         before = self.stringRepAll()
 
    #         timed('cleanup', self.cleanup)
    #         timed('checkBoxLock', self.checkBoxLockIterator)
    #         timed('checkRowLock', self.checkRowLockIterator)
    #         timed('checkColLock', self.checkColLockIterator)
 
    #         if timed('bug', self.bug):
    #             bugFired = True
 
    #         if self.stringRepAll() == before: break
 
    #     # accumulate into global timers
    #     for key, val in subTimers.items():
    #         fullKey = f"bc_{key}"
    #         if fullKey not in timers:
    #             timers[fullKey] = {"copies": 0, "calls": 0, "time": 0.0}
    #         timers[fullKey]["calls"] += 1
    #         timers[fullKey]["time"] += val
 
    #     return bugFired
    # Fundamental updating function
    # *************************************
    # OLDER VERSION
    # *************************************
    # def cleanup(self):
    #     # loop that goes through all nodes
    #     for i in range(9):
    #         for j in range(9):
    #             # skips iteration if value exists in current Node
    #             if self.locked[i][j]: continue
    #             # creates a temporary set of all nonzero notes in the current node
    #             tempSet = self.getSet((i, j))
    #             if len(tempSet) == 1:
    #                 a = tempSet.pop()
    #                 self.addToReports(f"Cleanup found {a} at index {(i, j)}\n")
    #                 self.layout[i][j].setVal(a, (i, j))
    #                 self.cleanup()
    #                 continue
    #             for a in tempSet:
    #                 if any([self.singleBoxCheck([(i,j)], {a}),
    #                         self.singleRowCheck([(i,j)], {a}),
    #                         self.singleColCheck([(i,j)], {a})]):
    #                     self.addToReports(f"Cleanup found {a} at index {(i, j)}\n")
    #                     self.layout[i][j].setVal(a, (i, j))
    #                     self.cleanup()
    #                     break
    # *************************************
    # OLD VERSION
    # *************************************
    def cleanup(self):
        changed = True
        while changed:
            changed = False
            for i in range(9):
                for j in range(9):
                    if self.locked[i][j]: continue
                    tempSet = self.getSet((i, j))
                    if not tempSet: continue
                    
                    placed = None
                    if len(tempSet) == 1:
                        placed = next(iter(tempSet))
                    else:
                        for a in tempSet:
                            if any([self.singleBoxCheck([(i,j)], {a}),
                                    self.singleRowCheck([(i,j)], {a}),
                                    self.singleColCheck([(i,j)], {a})]):
                                placed = a
                                break
                    
                    if placed is not None:
                        self.addToReports(f"Cleanup found {placed} at index {(i, j)}\n")
                        self.layout[i][j].setVal(placed, (i, j))
                        changed = True

    def cleanupSimple(self):
        changed = True
        while changed:
            changed = False
            for i in range(9):
                for j in range(9):
                    if self.locked[i][j]: continue
                    tempSet = self.getSet((i, j))
                    if not tempSet: continue
                    
                    placed = None
                    # ?**********************
                    if len(tempSet) == 1:
                        placed = next(iter(tempSet))
                    # ?**********************
                   
                    if placed is not None:
                        self.addToReports(f"Cleanup found {placed} at index {(i, j)}\n")
                        self.layout[i][j].setVal(placed, (i, j))
                        changed = True
    def cleanupSimpler(self, useNaked=False, useHidden=False, updateNotes=False):
        FULL = 0b1111111110   # bits 1..9
        box = [[(r // 3) * 3 + c // 3 for c in range(9)] for r in range(9)]
        units = ([[(r, c) for c in range(9)] for r in range(9)]
                 + [[(r, c) for r in range(9)] for c in range(9)]
                 + [[(r, c) for r in range(br, br + 3) for c in range(bc, bc + 3)]
                    for br in (0, 3, 6) for bc in (0, 3, 6)])
    
        grid = [[self.layout[r][c].val for c in range(9)] for r in range(9)]
        rowSeen, colSeen, boxSeen = [0] * 9, [0] * 9, [0] * 9
        for r in range(9):
            for c in range(9):
                if grid[r][c]:
                    bit = 1 << grid[r][c]
                    rowSeen[r] |= bit; colSeen[c] |= bit; boxSeen[box[r][c]] |= bit
    
        def place(r, c, v):
            grid[r][c] = v
            bit = 1 << v
            rowSeen[r] |= bit; colSeen[c] |= bit; boxSeen[box[r][c]] |= bit
            self.addToReports(f"Cleanup found {v} at index {(r, c)}\n")
            self.layout[r][c].setVal(v, (r, c))
    
        placed = 0
        changed = True
        while changed:
            changed = False
            if useNaked:
                for r in range(9):
                    for c in range(9):
                        if grid[r][c]: continue
                        cand = FULL & ~(rowSeen[r] | colSeen[c] | boxSeen[box[r][c]])
                        if cand and cand & (cand - 1) == 0:
                            place(r, c, cand.bit_length() - 1); placed += 1; changed = True
            if useHidden:
                for unit in units:
                    unitSeen = 0
                    for r, c in unit:
                        if grid[r][c]: unitSeen |= 1 << grid[r][c]
                    for v in range(1, 10):
                        bit = 1 << v
                        if unitSeen & bit: continue
                        spots = [(r, c) for r, c in unit
                                 if not grid[r][c]
                                 and not ((rowSeen[r] | colSeen[c] | boxSeen[box[r][c]]) & bit)]
                        if len(spots) == 1:
                            place(spots[0][0], spots[0][1], v)
                            unitSeen |= bit; placed += 1; changed = True
        if updateNotes:
            self.resetNotes()
        return placed

    def singlesSolve(cells):
        """cells: 81 ints (0 = blank). Fills in naked/hidden singles only; returns the 81-int result."""
        grid = list(cells)
        cand = [_FULL if v == 0 else 0 for v in grid]
                _FULL = 0b1111111110
        _UNITS = ([[r * 9 + c for c in range(9)] for r in range(9)]
                  + [[r * 9 + c for r in range(9)] for c in range(9)]
                  + [[(br + r) * 9 + bc + c for r in range(3) for c in range(3)]
                     for br in (0, 3, 6) for bc in (0, 3, 6)])
        _PEERS = [sorted({j for u in _UNITS if i in u for j in u} - {i}) for i in range(81)]
        
        def place(i, v):
            grid[i] = v
            cand[i] = 0
            keep = ~(1 << v)
            for p in _PEERS[i]:
                cand[p] &= keep
    
        for i, v in enumerate(grid):
            if v:
                keep = ~(1 << v)
                for p in _PEERS[i]:
                    cand[p] &= keep
    
        progress = True
        while progress:
            progress = False
            for i in range(81):                      # naked single: one digit left for the cell
                m = cand[i]
                if m and not m & (m - 1):
                    place(i, m.bit_length() - 1)
                    progress = True
            for unit in _UNITS:                      # hidden single: one cell left for the digit
                once = twice = 0                     # digits seen in >= 1 cell / in >= 2 cells of this unit
                for i in unit:
                    m = cand[i]
                    twice |= once & m
                    once |= m
                only = once & ~twice                 # digits that fit in exactly one cell
                while only:
                    low = only & -only
                    only ^= low
                    for i in unit:
                        if cand[i] & low:
                            place(i, low.bit_length() - 1)
                            progress = True
                            break
        return grid
  

    # *************************************
    # NEW VERSION
    # *************************************
    # def cleanup(self):
    #     dirty = {(i, j) for i in range(9) for j in range(9) if not self.locked[i][j]}
    
    #     while dirty:
    #         i, j = dirty.pop()
    #         if self.locked[i][j]: continue
    #         tempSet = self.getSet((i, j))
    #         if not tempSet: continue
    
    #         placed = None
    #         if len(tempSet) == 1:
    #             placed = next(iter(tempSet))
    #         else:
    #             for a in tempSet:
    #                 if any([self.singleBoxCheck([(i, j)], {a}),
    #                         self.singleRowCheck([(i, j)], {a}),
    #                         self.singleColCheck([(i, j)], {a})]):
    #                     placed = a
    #                     break
    
    #         if placed is not None:
    #             self.addToReports(f"Cleanup found {placed} at index {(i, j)}\n")
    #             self.layout[i][j].setVal(placed, (i, j))
    #             for peer in self._peers(i, j):
    #                 if self.locked[peer[0]][peer[1]]: continue
    #                 dirty.add(peer)
    #                 # a peer's notes just changed, so cells sharing ITS row/col/box
    #                 # may now be forced too, even if they aren't peers of (i, j)
    #                 for p2 in self._peers(*peer):
    #                     if not self.locked[p2[0]][p2[1]]:
    #                         dirty.add(p2)
    
    # def _peers(self, i, j):
    #     peers = set()
    #     for c in range(9):
    #         if c != j: peers.add((i, c))
    #     for r in range(9):
    #         if r != i: peers.add((r, j))
    #     br, bc = 3 * (i // 3), 3 * (j // 3)
    #     for r in range(br, br + 3):
    #         for c in range(bc, bc + 3):
    #             if (r, c) != (i, j): peers.add((r, c))
    #     return peers
    
    
    def checkBoxLockIterator(self):
        boxes = [(r, c) for r in range(0, 9, 3) for c in range(0, 9, 3)]
        lockedVals = set()
        for x, y in boxes:
            lockedVals.clear()
            allBoxNotes = self.getAllBoxNotes((x, y))
            changed = True
            while changed:
                boxCells = [(r, c) for r in range(x, x + 3) for c in range(y, y + 3) if not self.locked[r][c] and not self.softboxlocked[r][c]]
                if not boxCells: break
                cellSets = {cell: self.getSet(cell) for cell in boxCells}
                changed = self.checkBoxLock((x, y), boxCells, cellSets, lockedVals, allBoxNotes)
            
    def checkBoxLock(self, boxCoords, boxCells, cellSets, lockedVals, allBoxNotes):
        x, y = boxCoords
        for size in range(2, len(boxCells) + 1):
            for combo in itertools.combinations(boxCells, size):
                union = set().union(*(cellSets[cell] for cell in combo))
                if len(union) != size: continue
                comboList = list(combo)
                goodList = []
                sit = 0
                exact = [cell for cell in comboList if cellSets[cell] == union]
                extended = [cell for cell in boxCells if cellSets[cell] <= union]
                if len(exact) == size:
                    goodList = exact
                    sit = 1
                elif 2 <= len(extended) == size:
                    goodList = extended
                    sit = 2
                if not goodList: continue
                for cell in goodList: self.softboxlocked[cell[0]][cell[1]] = True
                self.subUpdateNotes('box', goodList, union, True)
                self.fullReport += f"CheckBoxLock Sit {sit} found {union} in {goodList}, recorded box locks.\n"
                lockedVals |= union
                if lockedVals == allBoxNotes: return False
                return True
        #probably redundant, but you can leave it here and tone down size if this fucks you over.
        return False
        
    def checkRowLockIterator(self):
        lockedVals = set()
        for r in range(9):
            lockedVals.clear()
            allRowNotes = self.getAllRowNotes(r)
            changed = True
            while changed:
                rowCells = [(r, c) for c in range(9) if not self.locked[r][c] and not self.softlinelockedx[r][c]]
                if not rowCells: break
                cellSets = {cell: self.getSet(cell) for cell in rowCells}
                changed = self.checkRowLock(r, rowCells, cellSets, lockedVals, allRowNotes)
    
    def checkRowLock(self, row, rowCells, cellSets, lockedVals, allRowNotes):
        for size in range(2, len(rowCells) + 1):
            for combo in itertools.combinations(rowCells, size):
                union = set().union(*(cellSets[cell] for cell in combo))
                if len(union) != size: continue
                comboList = list(combo)
                goodList = []
                sit = 0
                exact = [cell for cell in comboList if cellSets[cell] == union]
                extended = [cell for cell in rowCells if cellSets[cell] <= union]
                if len(exact) == size:
                    goodList = exact
                    sit = 1
                elif 2 <= len(extended) == size:
                    goodList = extended
                    sit = 2
                if not goodList: continue
    
                for cell in goodList: self.softlinelockedx[cell[0]][cell[1]] = True
                self.subUpdateNotes('row', goodList, union, True)
                self.fullReport += f"CheckRowLock Sit {sit} found {union} in {goodList}, recorded row locks.\n"
                lockedVals |= union
                if lockedVals == allRowNotes: return False
                return True
        return False
    
    def checkColLockIterator(self):
        lockedVals = set()
        for c in range(9):
            lockedVals.clear()
            allColNotes = self.getAllColNotes(c)
            changed = True
            while changed:
                colCells = [(r, c) for r in range(9) if not self.locked[r][c] and not self.softlinelockedy[r][c]]
                if not colCells: break
                cellSets = {cell: self.getSet(cell) for cell in colCells}
                changed = self.checkColLock(c, colCells, cellSets, lockedVals, allColNotes)
    
    def checkColLock(self, col, colCells, cellSets, lockedVals, allColNotes):
        for size in range(2, len(colCells) + 1):
            for combo in itertools.combinations(colCells, size):
                union = set().union(*(cellSets[cell] for cell in combo))
                if len(union) != size: continue
                comboList = list(combo)
                goodList = []
                sit = 0
                exact = [cell for cell in comboList if cellSets[cell] == union]
                extended = [cell for cell in colCells if cellSets[cell] <= union]
                if len(exact) == size:
                    goodList = exact
                    sit = 1
                elif 2 <= len(extended) == size:
                    goodList = extended
                    sit = 2
                if not goodList: continue
    
                for cell in goodList: self.softlinelockedy[cell[0]][cell[1]] = True
                self.subUpdateNotes('col', goodList, union, True)
                self.fullReport += f"CheckColLock Sit {sit} found {union} in {goodList}, recorded col locks.\n"
                lockedVals |= union
                if lockedVals == allColNotes: return False
                return True
        return False
    # ********************************************************************************************************************
    # ***********************************************TOUGH STRATEGIES*****************************************************
    # ********************************************************************************************************************
    # Theres definitely room for optimization, try collecting all of the strong links then comparing all of them 
    # def xWing(self, baseCopy, current_node):
    #     newPuzzles = []
    #     for val in self.getRemaining():
    #         for r1 in range(9):
    #             row1Cells = {c for r, c in self.getAnyRowIdxs((r1, 0), {val})}
    #             if len(row1Cells) != 2: continue
    #             for r2 in range(r1 + 1, 9):
    #                 row2Cells = {c for r, c in self.getAnyRowIdxs((r2, 0), {val})}
    #                 if row2Cells != row1Cells: continue
    #                 for c in row1Cells: 
    #                     baseCopy.subUpdateNotes('col', [(r1, c), (r2, c)], {val})
    #                 if self.stuck(baseCopy): continue
    #                 note = f"X-Wing removed {val} in columns {row1Cells}"
    #                 eNodes = self.puzzleDifference(baseCopy)
    #                 baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "X-Wing Row", current_node)
    #                 newPuzzles.append(tempPuzzle)
    #         for c1 in range(9):
    #             col1Cells = {r for r, c in self.getAnyColIdxs((0, c1), {val})}
    #             if len(col1Cells) != 2: continue
    #             for c2 in range(c1 + 1, 9):
    #                 col2Cells = {r for r, c in self.getAnyColIdxs((0, c2), {val})}
    #                 if col1Cells != col2Cells: continue 
    #                 for r in col1Cells: 
    #                     baseCopy.subUpdateNotes('row', [(r, c1), (r, c2)], {val})
    #                 if self.stuck(baseCopy): continue
    #                 note = f"X-Wing removed {val} in rows {col1Cells}"
    #                 eNodes = self.puzzleDifference(baseCopy)
    #                 baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "X-Wing Col", current_node)
    #                 newPuzzles.append(tempPuzzle)
    #     return baseCopy, newPuzzles
    # getAnyRowIdxs(self, pos, vals)
    
    def xWing(self, baseCopy, current_node):
        newPuzzles = []
        for val in self.getRemaining():
            for r1 in range(9):
                row1Cells = {c for r, c in self.getAnyRowIdxs((r1, 0), {val})}
                if len(row1Cells) != 2: continue
                for r2 in range(r1 + 1, 9):
                    row2Cells = {c for r, c in self.getAnyRowIdxs((r2, 0), {val})}
                    if row2Cells != row1Cells: continue
                    eNodes = set()
                    for c in row1Cells: 
                        eNodes |= {(val, (r, c)) for r, c in self.getAnyColIdxs((r1, c), {val}) - {(r1, c), (r2, c)}}
                    if not eNodes or uberPrune(current_node, ("X-Wing Row", [row1Cells, row2Cells], eNodes, None)): continue
                    baseCopy.updateNotesGX(eNodes)
                    if self.stuck(baseCopy): continue
                    note = f"X-Wing removed {val} in columns {row1Cells}"
                    eNodes = self.puzzleDifference(baseCopy)
                    baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "X-Wing Row", current_node, [row1Cells, row2Cells])
                    newPuzzles.append(tempPuzzle)
            for c1 in range(9):
                col1Cells = {r for r, c in self.getAnyColIdxs((0, c1), {val})}
                if len(col1Cells) != 2: continue
                for c2 in range(c1 + 1, 9):
                    col2Cells = {r for r, c in self.getAnyColIdxs((0, c2), {val})}
                    if col1Cells != col2Cells: continue
                    eNodes = set()
                    for r in col1Cells:
                        eNodes |= {(val, (r, c)) for r, c in self.getAnyRowIdxs((r, c1), {val}) - {(r, c1), (r, c2)}}
                    if not eNodes or uberPrune(current_node, ("X-Wing Col", [col1Cells, col2Cells], eNodes, None)): continue
                    baseCopy.updateNotesGX(eNodes)
                    if self.stuck(baseCopy): continue
                    note = f"X-Wing removed {val} in rows {col1Cells}"
                    baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "X-Wing Col", current_node, [col1Cells, col2Cells])
                    newPuzzles.append(tempPuzzle)
        return baseCopy, newPuzzles

    # def xWing(self, baseCopy, current_node):
    #     newPuzzles = []
    #     for val in self.getRemaining():
    #         # ---- Row X-Wing ----
    #         for r1 in range(9):
    #             row1Cells = {c for r, c in self.getAnyRowIdxs((r1, 0), {val})}
    #             if len(row1Cells) != 2: continue
    #             for r2 in range(r1 + 1, 9):
    #                 row2Cells = {c for r, c in self.getAnyRowIdxs((r2, 0), {val})}
    #                 if row2Cells != row1Cells: continue
    #                 corners = [(r, c) for r in (r1, r2) for c in row1Cells]
    #                 if self.threeMatchingPairs(corners): continue
    #                 eNodes = set()
    #                 for c in row1Cells:
    #                     eNodes |= {(val, (r, c)) for r, c in self.getAnyColIdxs((r1, c), {val}) - {(r1, c), (r2, c)}}
    #                 if not eNodes or uberPrune(current_node, ("X-Wing Row", [row1Cells, row2Cells], eNodes, None)): continue
    #                 baseCopy.updateNotesGX(eNodes)
    #                 if self.stuck(baseCopy): continue
    #                 note = f"X-Wing removed {val} in columns {row1Cells}"
    #                 eNodes = self.puzzleDifference(baseCopy)
    #                 baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "X-Wing Row", current_node, [row1Cells, row2Cells])
    #                 newPuzzles.append(tempPuzzle)
 
    #         # ---- Column X-Wing ----
    #         for c1 in range(9):
    #             col1Cells = {r for r, c in self.getAnyColIdxs((0, c1), {val})}
    #             if len(col1Cells) != 2: continue
    #             for c2 in range(c1 + 1, 9):
    #                 col2Cells = {r for r, c in self.getAnyColIdxs((0, c2), {val})}
    #                 if col1Cells != col2Cells: continue
    #                 corners = [(r, c) for r in col1Cells for c in (c1, c2)]
    #                 if self.threeMatchingPairs(corners): continue
    #                 eNodes = set()
    #                 for r in col1Cells:
    #                     eNodes |= {(val, (r, c)) for r, c in self.getAnyRowIdxs((r, c1), {val}) - {(r, c1), (r, c2)}}
    #                 if not eNodes or uberPrune(current_node, ("X-Wing Col", [col1Cells, col2Cells], eNodes, None)): continue
    #                 baseCopy.updateNotesGX(eNodes)
    #                 if self.stuck(baseCopy): continue
    #                 note = f"X-Wing removed {val} in rows {col1Cells}"
    #                 baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "X-Wing Col", current_node, [col1Cells, col2Cells])
    #                 newPuzzles.append(tempPuzzle)
    #     return baseCopy, newPuzzles
        
    # def threeMatchingPairs(self, corners):
    #     sets = Counter(frozenset(self.getSet(pos)) for pos in corners)
    #     return any(n >= 3 and len(s) == 2 for s, n in sets.items())

    # ********************************************************************************************************************
    # Performs chute remote pairs strategy & updates accordingly, "naked" pairs which exist in different rows and columns (within square sight of a node)
    def chuteRemotePairs(self, baseCopy, current_node):
        newPuzzles = []
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
                        if self.locked[r][c]: pennedSet.add(self.layout[r][c].val)
                        else: pencilSet |= self.getSet((r, c))
                    remoteIntersection = comboSet & (pencilSet | pennedSet)
                    pencilIntersection = comboSet & pencilSet
                    pennedIntersection = comboSet & pennedSet
                    eNodes = set()
                    baseENodes = [(x, eCol) for eCol in range(colOffset1, colOffset1 + 3)] + [(a, eCol) for eCol in range(colOffset2, colOffset2 + 3)]
                    group = ((a, b), (x, y))
                    note = ""
                    if len(pencilSet) == 0 and len(pennedIntersection) == 0:
                        baseENodes += [(x, eCol) for eCol in range(colOffset2, colOffset2 + 3) if eCol != y] + [(a, eCol) for eCol in range(colOffset1, colOffset1 + 3) if eCol != b]
                        for val in comboSet:
                            for r, c in baseENodes:
                                if val in self.layout[r][c].note:
                                    eNodes.add((val, (r, c)))
                        note = f"Remote Pair (Row) 1: {[(a, b), (x, y)]} removed {comboSet}"
                    elif len(pennedIntersection) == 1 and len(pencilIntersection) == 0:
                        for val in pennedIntersection:
                            for r, c in baseENodes:
                                if val in self.layout[r][c].note:
                                    eNodes.add((val, (r, c)))
                        note = f"Remote Pair (Row) 2: {[(a, b), (x, y)]} removed {pennedIntersection}"
                    elif len(remoteIntersection) == 1 and len(pencilIntersection) == 1:
                        for val in pencilIntersection:
                            for r, c in baseENodes:
                                if val in self.layout[r][c].note:
                                    eNodes.add((val, (r, c)))
                        note = f"Remote Pair (Row) 3: {[(a, b), (x, y)]} removed {pencilIntersection}"
                    if eNodes and not uberPrune(current_node, ("Chute Remote Pairs Row", group, eNodes, None)):
                        baseCopy.updateNotesGX(eNodes)
                        diffNodes = self.puzzleDifference(baseCopy)
                        note = note + f" from {diffNodes}"
                        baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Chute Remote Pairs Row", current_node, group)
                        newPuzzles.append(tempPuzzle)
                        
            colPairs = self.getColChuteRemotePairs(comboSet)
            if len(colPairs) != 0:
                for (a, b), (x, y) in colPairs:
                    colOffset1, rowOffset1, rowOffset2 = self.getOffset(b), self.getOffset(a), self.getOffset(x)
                    otherCells = {(r, c) for r in range(9) for c in range(colOffset1, colOffset1 + 3) if c not in {b, y} and not (rowOffset1 <= r < rowOffset1 + 3 or rowOffset2 <= r < rowOffset2 + 3)}
                    pencilSet, pennedSet = set(), set()
                    for r, c in otherCells:
                        if self.locked[r][c]: pennedSet.add(self.layout[r][c].val)
                        else: pencilSet |= self.getSet((r, c))
                    remoteIntersection = comboSet & (pencilSet | pennedSet)
                    pencilIntersection = comboSet & pencilSet
                    pennedIntersection = comboSet & pennedSet
                    eNodes = set()
                    baseENodes = [(eRow, y) for eRow in range(rowOffset1, rowOffset1 + 3)] + [(eRow, b) for eRow in range(rowOffset2, rowOffset2 + 3)]
                    group = ((a, b), (x, y))
                    note = ""
                    if len(pencilSet) == 0 and len(pennedIntersection) == 0:
                        baseENodes += [(eRow, y) for eRow in range(rowOffset2, rowOffset2 + 3) if eRow != x] + [(eRow, b) for eRow in range(rowOffset1, rowOffset1 + 3) if eRow != a]
                        for val in comboSet:
                            for r, c in baseENodes:
                                if val in self.layout[r][c].note:
                                    eNodes.add((val, (r, c)))
                        note = f"Remote Pair (Col) 1: {[(a, b), (x, y)]} removed {comboSet}"
                    elif len(pennedIntersection) == 1 and len(pencilIntersection) == 0:
                        for val in pennedIntersection:
                            for r, c in baseENodes:
                                if val in self.layout[r][c].note:
                                    eNodes.add((val, (r, c)))
                        note = f"Remote Pair (Col) 2: {[(a, b), (x, y)]} removed {pennedIntersection}"
                    elif len(remoteIntersection) == 1 and len(pencilIntersection) == 1:
                        for val in pencilIntersection:
                            for r, c in baseENodes:
                                if val in self.layout[r][c].note:
                                    eNodes.add((val, (r, c)))
                        note = f"Remote Pair (Col) 3: {[(a, b), (x, y)]} removed {pencilIntersection}"
                    if eNodes and not uberPrune(current_node, ("Chute Remote Pairs Col", group, eNodes, None)):
                        baseCopy.updateNotesGX(eNodes)
                        diffNodes = self.puzzleDifference(baseCopy)
                        note = note + f" from {diffNodes}"
                        baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Chute Remote Pairs Col", current_node, group)
                        newPuzzles.append(tempPuzzle)
        return baseCopy, newPuzzles
    # def chuteRemotePairs(self, baseCopy, current_node):
    #     newPuzzles = []
    #     remaining = self.getRemaining()
    #     for combo in itertools.combinations(remaining, 2):
    #         comboSet = set(combo)
    #         rowPairs = self.getRowChuteRemotePairs(comboSet)
    #         if len(rowPairs) != 0:
    #             for (a, b), (x, y) in rowPairs:
    #                 rowOffset1, colOffset1, colOffset2 = self.getOffset(a), self.getOffset(b), self.getOffset(y)
    #                 otherCells = {(r, c) for r in range(rowOffset1, rowOffset1 + 3) for c in range(9) if r not in {a, x} and not (colOffset1 <= c < colOffset1 + 3 or colOffset2 <= c < colOffset2 + 3)}
    #                 pencilSet, pennedSet = set(), set()
    #                 for r, c in otherCells:
    #                     if self.locked[r][c]: pennedSet.add(self.layout[r][c].val)
    #                     else: pencilSet |= self.getSet((r, c))
    #                 remoteIntersection = comboSet & (pencilSet | pennedSet)
    #                 pencilIntersection = comboSet & pencilSet
    #                 pennedIntersection = comboSet & pennedSet
    #                 eNodes = [(x,eCol) for eCol in range(colOffset1, colOffset1 + 3)] + [(a,eCol) for eCol in range(colOffset2, colOffset2 + 3)]
    #                 group = ((a, b), (x, y))
    #                 if len(pencilSet) == 0 and len(pennedIntersection) == 0:
    #                     eNodes += [(x, eCol) for eCol in range(colOffset2, colOffset2 + 3) if eCol != y] + [(a, eCol) for eCol in range(colOffset1, colOffset1 + 3) if eCol != b]
    #                     baseCopy.updateNotesDX(eNodes, comboSet)
    #                     eNodes = self.puzzleDifference(baseCopy)
    #                     note = f"Remote Pair (Row) 1: {[(a, b), (x, y)]} removed {comboSet} from {eNodes}"
    #                 elif len(pennedIntersection) == 1 and len(pencilIntersection) == 0:
    #                     baseCopy.updateNotesDX(eNodes, pennedIntersection)
    #                     eNodes = self.puzzleDifference(baseCopy)
    #                     note = f"Remote Pair (Row) 2: {[(a, b), (x, y)]} removed {pennedIntersection} from {eNodes}"
    #                 elif len(remoteIntersection) == 1 and len(pencilIntersection) == 1:
    #                     baseCopy.updateNotesDX(eNodes, pencilIntersection)
    #                     eNodes = self.puzzleDifference(baseCopy)
    #                     note = f"Remote Pair (Row) 3: {[(a, b), (x, y)]} removed {pencilIntersection} from {eNodes}"
    #                 if not self.stuck(baseCopy):
    #                     baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Chute Remote Pairs Row", current_node, group)
    #                     newPuzzles.append(tempPuzzle)
                        
    #         colPairs = self.getColChuteRemotePairs(comboSet)
    #         if len(colPairs) != 0:
    #             for (a, b), (x, y) in colPairs:
    #                 colOffset1, rowOffset1, rowOffset2 = self.getOffset(b), self.getOffset(a), self.getOffset(x)
    #                 otherCells = {(r, c) for r in range(9) for c in range(colOffset1, colOffset1 + 3) if c not in {b, y} and not (rowOffset1 <= r < rowOffset1 + 3 or rowOffset2 <= r < rowOffset2 + 3)}
    #                 pencilSet, pennedSet = set(), set()
    #                 for r, c in otherCells:
    #                     if self.locked[r][c]: pennedSet.add(self.layout[r][c].val)
    #                     else: pencilSet |= self.getSet((r, c))
    #                 remoteIntersection = comboSet & (pencilSet | pennedSet)
    #                 pencilIntersection = comboSet & pencilSet
    #                 pennedIntersection = comboSet & pennedSet
    #                 eNodes = [(eRow, y) for eRow in range(rowOffset1, rowOffset1 + 3)] + [(eRow, b) for eRow in range(rowOffset2, rowOffset2 + 3)]
    #                 group = ((a, b), (x, y))
    #                 if len(pencilSet) == 0 and len(pennedIntersection) == 0:
    #                     eNodes += [(eRow, y) for eRow in range(rowOffset2, rowOffset2 + 3) if eRow != x] + [(eRow, b) for eRow in range(rowOffset1, rowOffset1 + 3) if eRow != a]
    #                     baseCopy.updateNotesDX(eNodes, comboSet)
    #                     eNodes = self.puzzleDifference(baseCopy)
    #                     note = f"Remote Pair (Col) 1: {[(a, b), (x, y)]} removed {comboSet} from {eNodes}"
    #                 elif len(pennedIntersection) == 1 and len(pencilIntersection) == 0:
    #                     baseCopy.updateNotesDX(eNodes, pennedIntersection)
    #                     eNodes = self.puzzleDifference(baseCopy)
    #                     note = f"Remote Pair (Col) 2: {[(a, b), (x, y)]} removed {pennedIntersection} from {eNodes}"
    #                 elif len(remoteIntersection) == 1 and len(pencilIntersection) == 1:
    #                     baseCopy.updateNotesDX(eNodes, pencilIntersection)
    #                     eNodes = self.puzzleDifference(baseCopy)
    #                     note = f"Remote Pair (Col) 3: {[(a, b), (x, y)]} removed {pencilIntersection} from {eNodes}"
    #                 if not self.stuck(baseCopy):
    #                     baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Chute Remote Pairs Col", current_node, group)
    #                     newPuzzles.append(tempPuzzle)
    #     return baseCopy, newPuzzles



        
    def getRowChuteRemotePairs(self, combo):
        remotePairs = []
        goodNodes = {(r, c) for r in range(9) for c in range(9) if self.getSet((r, c)) == combo}
        for n1, n2 in itertools.combinations(goodNodes, 2):
            if self.sameRowChute([n1, n2]): remotePairs.append([n1, n2])
        return remotePairs
    def getColChuteRemotePairs(self, combo):
        remotePairs = []
        goodNodes = {(r, c) for r in range(9) for c in range(9) if self.getSet((r, c)) == combo}
        for n1, n2 in itertools.combinations(goodNodes, 2):
            if self.sameColChute([n1, n2]): remotePairs.append([n1, n2])
        return remotePairs
    # ********************************************************************************************************************
    def simpleColoring(self, baseCopy, current_node):
        newPuzzles = []
        remaining = self.getRemaining()
        allPatterns = dict()
        for val in self.getRemaining():
            allConnections = self.getAllSCConnections(val)
            scPatterns = self.getSCPattern(allConnections)
            if scPatterns:
                allPatterns[val] = scPatterns
        for val, patterns in allPatterns.items():
            for pattern in patterns:
                group = pattern
                continueFlag = False
                coloredList = []
                normalized = set()
                color = 'green'
                for layer in pattern:
                    color = 'green' if color == 'yellow' else 'yellow'
                    for node in layer:
                        coloredList += [(color, node)]
                        normalized.add(node)
                if len(coloredList) <= 3: continue
                badColor = None
                for n1, n2 in itertools.combinations(coloredList, 2):
                    if n1[0] != n2[0]: continue
                    if self.inRow([n1[1], n2[1]]) or self.inCol([n1[1], n2[1]]) or self.inBox([n1[1], n2[1]]):
                        badColor = n1[0]
                        break
                if badColor is not None:
                    eNodes = set()
                    badNodes = []
                    for currentColor, node in coloredList:
                        if currentColor != badColor: continue
                        x, y = node
                        eNodes.add((val, (x, y)))
                        badNodes.append((x, y))
                    note = ""        
                    for layer in pattern:
                        note += f"{layer}\n"
                    note += f"Simple Coloring rule 2 removed {val} from nodes: {badNodes}"
                    if eNodes and not uberPrune(current_node, ("Simple Coloring Rule 2", group, eNodes, None)):
                        baseCopy.updateNotesGX(eNodes)
                        diffNodes = self.puzzleDifference(baseCopy)
                        note += f" from {diffNodes}"
                        baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Simple Coloring Rule 2", current_node, group)
                        newPuzzles.append(tempPuzzle)
                        continueFlag = True
                if continueFlag: continue
                eNodes = set()
                potentialElims = {(r, c) for r in range(9) for c in range(9) if not self.locked[r][c] and val in self.layout[r][c].note}
                potentialElims -= normalized
                for r, c in potentialElims:
                    greenConnected = []
                    yellowConnected = []
                    for currentColor, node in coloredList:
                        a, b = node
                        if self.hasConnection([(r, c), (a, b)]):
                            if currentColor == 'green':
                                greenConnected.append((a, b))
                            else:
                                yellowConnected.append((a, b))
                    if greenConnected and yellowConnected and not self.hasConnection(greenConnected + yellowConnected):
                        eNodes.add((val, (r, c)))
                note = ""
                for layer in pattern:
                    note += f"{layer}\n"
                note += f"Simple Coloring rule 4 removed {val}"
                if eNodes and not uberPrune(current_node, ("Simple Coloring Rule 4", group, eNodes, None)):
                    baseCopy.updateNotesGX(eNodes)
                    diffNodes = self.puzzleDifference(baseCopy)
                    note += f" from {diffNodes}"
                    baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Simple Coloring Rule 4", current_node, group)
                    if not any(tempPuzzle.stuck(newPuzzle) for newPuzzle in newPuzzles):
                        newPuzzles.append(tempPuzzle)
        return baseCopy, newPuzzles
    # def simpleColoring(self, baseCopy, current_node):
    #     newPuzzles = []
    #     remaining = self.getRemaining()
    #     allPatterns = dict()
    #     for val in self.getRemaining():
    #         allConnections = self.getAllSCConnections(val)
    #         scPatterns = self.getSCPattern(allConnections)
    #         if scPatterns:
    #             allPatterns[val] = scPatterns
    #     for val, patterns in allPatterns.items():
    #         if val != 7: continue
    #         for pattern in patterns:
    #             group = pattern
    #             continueFlag = False
    #             coloredList = []
    #             normalized = set()
    #             color = 'green'
    #             for layer in pattern:
    #                 color = 'green' if color == 'yellow' else 'yellow'
    #                 for node in layer:
    #                     coloredList += [(color, node)]
    #                     normalized.add(node)
    #             if len(coloredList) <= 3: continue
    #             badColor = None
    #             for n1, n2 in itertools.combinations(coloredList, 2):
    #                 if n1[0] != n2[0]: continue
    #                 if self.inRow([n1[1], n2[1]]) or self.inCol([n1[1], n2[1]]) or self.inBox([n1[1], n2[1]]):
    #                     badColor = n1[0]
    #                     break
    #             if badColor is not None:
    #                 for currentColor, node in coloredList:
    #                     if currentColor == badColor: continue
    #                     x, y = node
    #                     note = ""
    #                     for layer in pattern:
    #                         note += f"{layer}\n"
    #                     note = f"Simple Coloring rule 2 found {val} at index {(x, y)}"
    #                     baseCopy.layout[x][y].setVal(val, (x, y))
    #                     baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Simple Coloring Rule 2", current_node, group)
    #                     newPuzzles.append(tempPuzzle)
    #                     continueFlag = True
    #             if continueFlag: continue
    #             eNodes = []
    #             potentialElims = {(r, c) for r in range(9) for c in range(9) if not self.locked[r][c] and val in self.layout[r][c].note}
    #             potentialElims = potentialElims - normalized
    #             for nA, nB in itertools.combinations(coloredList, 2):
    #                 if nA[0] == nB[0]: continue
    #                 n1, n2 = nA[1], nB[1]
    #                 for node in potentialElims:
    #                     if self.hasConnection([n1, node]) and self.hasConnection([n2, node]):
    #                         eNodes.append(node)
    #             for er, ec in eNodes:
    #                 baseCopy.layout[er][ec].note[val-1] = 0
    #             if not self.stuck(baseCopy):
    #                 note = ""
    #                 for layer in pattern:
    #                     note += f"{layer}\n"
    #                 eNodes = self.puzzleDifference(baseCopy)
    #                 note += f"Simple Coloring rule 4 removed {val} from {eNodes}"
    #                 baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Simple Coloring Rule 4", current_node, group)
    #                 if not any(tempPuzzle.stuck(newPuzzle) for newPuzzle in newPuzzles):
    #                     newPuzzles.append(tempPuzzle)
    #     return baseCopy, newPuzzles

    def getSCPattern(self, allConnections, currentPattern=None, allPatterns=None):
        if currentPattern is None:
            currentPattern = []
        if allPatterns is None:
            allPatterns = []
        while allConnections:
            if not currentPattern:
                startNode = next(iter(allConnections))
                currentPattern.append([startNode])
            tempLayer = set()
            for node in currentPattern[-1]:
                neighbors = allConnections.get(node, set())
                tempLayer.update(neighbors)
            for node in currentPattern[-1]:
                if node in allConnections:
                    del allConnections[node]
                for other in allConnections:
                    allConnections[other] -= {node}
            if not tempLayer:
                allPatterns.append([list(layer) for layer in currentPattern])
                currentPattern = []
            else:
                currentPattern.append(list(tempLayer))
        return allPatterns

    def getAllSCConnections(self, val):
        connections = {}
        def add_link(a, b):
            connections.setdefault(a, set()).add(b)
            connections.setdefault(b, set()).add(a)
        for row in range(9):
            rowIdxs = list(self.getAnyRowIdxs((row, 0), {val}))
            if len(rowIdxs) == 2:
                add_link(tuple(rowIdxs[0]), tuple(rowIdxs[1]))
        for col in range(9):
            colIdxs = list(self.getAnyColIdxs((0, col), {val}))
            if len(colIdxs) == 2:
                add_link(tuple(colIdxs[0]), tuple(colIdxs[1]))
        for boxR in range(0, 9, 3):
            for boxC in range(0, 9, 3):
                boxIdxs = list(self.getAnyBoxIdxs((boxR, boxC), {val}))
                if len(boxIdxs) == 2:
                    add_link(tuple(boxIdxs[0]), tuple(boxIdxs[1]))
        return connections

    # ********************************************************************************************************************
    def wWing(self, baseCopy, current_node):
        newPuzzles = []
        wIndex = self.getAnyTwos()
        wNodes = [cell for cells in wIndex.values() for cell in cells]
        links = self.getWWingLinks(wNodes)
        paths = self.getWWingPaths(links)
        for path in paths:
            start, end = path[0], path[-1]
            startConnections, endConnections = self.getAnyCoords(start), self.getAnyCoords(end)
            common = set.intersection(*[self.getSet(node) for node in path])
            if len(common) == 2:
                eVals = common
            else:
                eVals = self.getSet(start) - common
            eNodes = {(val, (x, y)) for (x, y) in (startConnections & endConnections) if not self.locked[x][y] for val in eVals if val in self.layout[x][y].note}
            if not eNodes: continue
            note = f"{path}\nW-Wing removed {eVals}"
            if not uberPrune(current_node, ("W-Wing", path, eNodes, None)):
                baseCopy.updateNotesGX(eNodes)
                diffNodes = self.puzzleDifference(baseCopy)
                note += f" from {diffNodes}"
                baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "W-Wing", current_node, path)
                if not any(tempPuzzle.stuck(newPuzzle) for newPuzzle in newPuzzles):
                    newPuzzles.append(tempPuzzle)
        return baseCopy, newPuzzles

    # def wWing(self, baseCopy, current_node):
    #     newPuzzles = []
    #     wIndex = self.getAnyTwos()
    #     wNodes = [cell for cells in wIndex.values() for cell in cells]
    #     links = self.getWWingLinks(wNodes)
    #     paths = self.getWWingPaths(links)
    #     for path in paths:
    #         start, end = path[0], path[-1]
    #         startConnections, endConnections = self.getAnyCoords(start), self.getAnyCoords(end)
    #         #POTENTIAL PROBLEM: not subtracting current path from enodes
    #         eNodes = {(x, y) for (x, y) in (startConnections & endConnections) if not self.locked[x][y]}
    #         common = set.intersection(*[self.getSet(node) for node in path])
    #         if len(common) == 2:
    #             eVals = common
    #         else:
    #             eVals = self.getSet(start) - common
    #         if not eNodes: continue
    #         baseCopy.updateNotesDX(eNodes, eVals)
    #         if self.stuck(baseCopy): continue
    #         eNodes = self.puzzleDifference(baseCopy)
    #         note = f"{path}\nW-Wing removed {eVals} from from {eNodes}"
    #         baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "W-Wing", current_node, path)
    #         if not any(tempPuzzle.stuck(newPuzzle) for newPuzzle in newPuzzles):
    #             newPuzzles.append(tempPuzzle)
    #     return baseCopy, newPuzzles
        
    def getWWingPaths(self, links):
        paths = []
        for start in links:
            for second in links.get(start, []):
                conn1 = self.returnConnections([start, second])
                if not conn1: continue
                for third in links.get(second, []):
                    if third == start or self.getSet(third) != self.getSet(second): continue
                    conn2 = self.returnConnections([second, third])
                    if not conn2 or any(c in conn1 for c in conn2): continue
                    for end in links.get(third, []):
                        if end == start or end == second: continue
                        if self.getSet(start) != self.getSet(end) or self.hasConnection([start, end]): continue
                        conn3 = self.returnConnections([third, end])
                        if not conn3 or any(c in conn2 for c in conn3): continue
                        common = set.intersection(*[self.getSet(node) for node in [start, second, third, end]])
                        if not common: continue
                        paths.append([start, second, third, end])
        return paths
        
    def getWWingLinks(self, nodes):
        links = {}
        for nodeA, nodeB in itertools.combinations(nodes, 2):
            if self.hasConnection([nodeA, nodeB]):
                a, b = tuple(nodeA), tuple(nodeB)
                links.setdefault(a, set()).add(b)
                links.setdefault(b, set()).add(a)
        return links
    # ********************************************************************************************************************
    # y wing
    def yWing(self, baseCopy, current_node):
        newPuzzles = []
        for i in range(9):
            for j in range(9):
                if self.locked[i][j]: continue
                tempSet = self.getSet((i, j))
                if len(tempSet) != 2: continue 
                rowOffset, colOffset = self.getOffset(i), self.getOffset(j)
                colWing, rowWing = set(), set()
                for row in range(9):
                    if rowOffset <= row < rowOffset + 3 or self.locked[row][j]: continue
                    temp = self.getSet((row, j))
                    if len(temp) == 2 and len(temp & tempSet) == 1: colWing.add((row, j))
                for col in range(9):
                    if colOffset <= col < (colOffset + 3) or self.locked[i][col]: continue
                    temp = self.getSet((i, col))
                    if len(temp) == 2 and len(temp & tempSet) == 1: rowWing.add((i, col))
                if len(rowWing) > 0 and len(colWing) > 0:
                    for rx, ry in rowWing:
                        tempRowSet = self.getSet((rx, ry))
                        for cx, cy in colWing:
                            tempColSet = self.getSet((cx, cy))
                            if len(tempRowSet | tempColSet | tempSet) != 3 or self.layout[rx][ry].note == self.layout[cx][cy].note: continue
                            tempRowSet, tempColSet = self.getSet((rx, ry)), self.getSet((cx, cy))
                            eVal = tempRowSet & tempColSet
                            if len(eVal) != 1: continue
                            eNodes = {(val, (cx, ry)) for val in eVal if val in self.layout[cx][ry].note}
                            if not eNodes: continue
                            note = f"Y-Wing Sit 1, Root: {(i, j)}, rowWing {(rx, ry)}, colWing{(cx, cy)}\nErasing {eVal} at {(cx, ry)}"
                            if not uberPrune(current_node, ("Y-Wing Square", ((i,j),(rx,ry),(cx,cy)), eNodes, None)):
                                baseCopy.updateNotesGX(eNodes)
                                diffNodes = self.puzzleDifference(baseCopy)
                                note += f" from {diffNodes}"
                                baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Y-Wing Square", current_node, ((i,j),(rx,ry),(cx,cy)))
                                newPuzzles.append(tempPuzzle)
                elif len(rowWing) > 0 and len(colWing) == 0:
                    for rx, ry in rowWing:
                        tempRowSet = self.getSet((rx, ry))
                        targetSet = (tempSet | tempRowSet) - (tempSet & tempRowSet)
                        for a in range(rowOffset, rowOffset + 3):
                            if a == i: continue
                            for b in range(colOffset, colOffset + 3):
                                if b == j: continue
                                tempBoxSet = self.getSet((a, b))
                                if tempBoxSet == targetSet and len(self.getExRowIdxs((a, b), targetSet)) == 1:
                                    eVal = tempRowSet & tempBoxSet
                                    eCells = set()
                                    for eCol in range(colOffset, colOffset + 3): eCells.add((i, eCol))
                                    for eCol in range((ry//3) * 3, ((ry//3) * 3) + 3): eCells.add((a, eCol))
                                    eCells = eCells - {(i, j)}
                                    eNodes = {(val, (r, c)) for val in eVal for r, c in eCells if val in self.layout[r][c].note}
                                    if not eNodes: continue
                                    note = f"Y-Wing Sit 2.Row, Root: {(i, j)}, rowWing: {(rx, ry)}, boxNode: {(a, b)}\nRow Erasing {eVal}"
                                    if not uberPrune(current_node, ("Y-Wing Box (Row)", ((i,j),(rx,ry),(a,b)), eNodes, None)):
                                        baseCopy.updateNotesGX(eNodes)
                                        diffNodes = self.puzzleDifference(baseCopy)
                                        note += f" at {diffNodes}"
                                        baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Y-Wing Box (Row)", current_node, ((i,j),(rx,ry),(a,b)))
                                        newPuzzles.append(tempPuzzle)
                elif len(colWing) > 0 and len(rowWing) == 0:
                    for cx, cy in colWing:
                        tempColSet = self.getSet((cx, cy))
                        targetSet = (tempSet | tempColSet) - (tempSet & tempColSet)
                        for b in range(colOffset, colOffset + 3):
                            if b == j: continue
                            for a in range(rowOffset, rowOffset + 3):
                                if a == i: continue
                                tempBoxSet = self.getSet((a, b))
                                if tempBoxSet == targetSet and len(self.getExColIdxs((a, b), targetSet)) == 1:
                                    eVal = tempColSet & tempBoxSet
                                    eCells = set()
                                    for eRow in range(rowOffset, rowOffset + 3): eCells.add((eRow, j))
                                    for eRow in range((cx//3) * 3,((cx//3) * 3) + 3): eCells.add((eRow, b))
                                    eCells = eCells - {(i, j)}
                                    eNodes = {(val, (r, c)) for val in eVal for r, c in eCells if val in self.layout[r][c].note}
                                    if not eNodes: continue
                                    note = f"Y-Wing Sit 2.Col, Root: {(i, j)}, colWing: {(cx, cy)}, boxNode: {(a, b)}\nCol Erasing {eVal}"
                                    if not uberPrune(current_node, ("Y-Wing Box (Col)", ((i,j),(cx,cy),(a,b)), eNodes, None)):
                                        baseCopy.updateNotesGX(eNodes)
                                        diffNodes = self.puzzleDifference(baseCopy)
                                        note += f" at {diffNodes}"
                                        baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Y-Wing Box (Col)", current_node, ((i,j),(cx,cy),(a,b)))
                                        newPuzzles.append(tempPuzzle)
        return baseCopy, newPuzzles
    # def yWing(self, baseCopy, current_node):
    #     newPuzzles = []
    #     for i in range(9):
    #         for j in range(9):
    #             if self.locked[i][j]: continue
    #             tempSet = self.getSet((i, j))
    #             if len(tempSet) != 2: continue
    #             rowOffset, colOffset = self.getOffset(i), self.getOffset(j)
    #             colWing, rowWing = set(), set()
    #             # looks for candidate in column
    #             for row in range(9):
    #                 if rowOffset <= row < rowOffset + 3 or self.locked[row][j]: continue
    #                 temp = self.getSet((row, j))
    #                 if len(temp) == 2 and len(temp & tempSet) == 1: colWing.add((row, j))
    #             # looks for candidate in row
    #             for col in range(9):
    #                 if colOffset <= col < (colOffset + 3) or self.locked[i][col]: continue
    #                 temp = self.getSet((i, col))
    #                 if len(temp) == 2 and len(temp & tempSet) == 1: rowWing.add((i, col))
    #             if len(rowWing) > 0 and len(colWing) > 0:
    #                 for rx, ry in rowWing:
    #                     tempRowSet = self.getSet((rx, ry))
    #                     for cx, cy in colWing:
    #                         tempColSet = self.getSet((cx, cy))
    #                         if len(tempRowSet | tempColSet | tempSet) != 3 or self.layout[rx][ry].note == self.layout[cx][cy].note: continue
    #                         tempRowSet, tempColSet = self.getSet((rx, ry)), self.getSet((cx, cy))
    #                         eVal = tempRowSet & tempColSet
    #                         if len(eVal) != 1: continue
    #                         baseCopy.updateNotesDX([(cx, ry)], eVal)
    #                         if self.stuck(baseCopy): continue
    #                         note = f"Y-Wing Sit 1, Root: {(i, j)}, rowWing {(rx, ry)}, colWing{(cx, cy)}\nErasing {eVal} at {(cx, ry)}"
    #                         baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Y-Wing Square", current_node)
    #                         newPuzzles.append(tempPuzzle)
    #             elif len(rowWing) > 0 and len(colWing) == 0:
    #                 for rx, ry in rowWing:
    #                     tempRowSet = self.getSet((rx, ry))
    #                     targetSet = (tempSet | tempRowSet) - (tempSet & tempRowSet)
    #                     for a in range(rowOffset, rowOffset + 3):
    #                         if a == i: continue
    #                         for b in range(colOffset, colOffset + 3):
    #                             if b == j: continue
    #                             tempBoxSet = self.getSet((a, b))
    #                             if tempBoxSet == targetSet and len(self.getExRowIdxs((a, b), targetSet)) == 1:
    #                                 eVal = tempRowSet & tempBoxSet
    #                                 eCells = set()
    #                                 for eCol in range(colOffset, colOffset + 3): eCells.add((i, eCol))
    #                                 for eCol in range((ry//3) * 3, ((ry//3) * 3) + 3): eCells.add((a, eCol))
    #                                 eCells = eCells - {(i, j)}
    #                                 baseCopy.updateNotesDX(eCells, eVal)
    #                                 if self.stuck(baseCopy): continue
    #                                 eNodes = self.puzzleDifference(baseCopy)
    #                                 note = f"Y-Wing Sit 2.Row, Root: {(i, j)}, rowWing: {(rx, ry)}, boxNode: {(a, b)}\nRow Erasing {eVal} at {eNodes}"
    #                                 baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Y-Wing Box (Row)", current_node)
    #                                 newPuzzles.append(tempPuzzle)
    #             elif len(colWing) > 0 and len(rowWing) == 0:
    #                 for cx, cy in colWing:
    #                     tempColSet = self.getSet((cx, cy))
    #                     targetSet = (tempSet | tempColSet) - (tempSet & tempColSet)
    #                     for b in range(colOffset, colOffset + 3):
    #                         if b == j: continue
    #                         for a in range(rowOffset, rowOffset + 3):
    #                             if a == i: continue
    #                             tempBoxSet = self.getSet((a, b))
    #                             if tempBoxSet == targetSet and len(self.getExColIdxs((a, b), targetSet)) == 1:
    #                                 eVal = tempColSet & tempBoxSet
    #                                 eCells = set()
    #                                 for eRow in range(rowOffset, rowOffset + 3): eCells.add((eRow, j))
    #                                 for eRow in range((cx//3) * 3,((cx//3) * 3) + 3): eCells.add((eRow, b))
    #                                 eCells = eCells - {(i, j)}
    #                                 baseCopy.updateNotesDX(eCells, eVal)
    #                                 if self.stuck(baseCopy): continue
    #                                 eNodes = self.puzzleDifference(baseCopy)
    #                                 note = f"Y-Wing Sit 2.Col, Root: {(i, j)}, colWing: {(cx, cy)}, boxNode: {(a, b)}\nCol Erasing {eVal} at {eNodes}"
    #                                 baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Y-Wing Box (Col)", current_node)
    #                                 newPuzzles.append(tempPuzzle)
    #     return baseCopy, newPuzzles
    # ********************************************************************************************************************
    # rectangle elimination
    # *****CONSIDER RUNNING ALL OF THE RECTANGLE ELIMINATIONS FOR A GIVEN PUZZLE AT ONCE
    def rectangleElimination(self, baseCopy, current_node):
        newPuzzles = []
        remaining = self.getRemaining()
        rowDict, colDict = baseCopy.getRectDicts(remaining)
        for val in remaining:
            for row in rowDict.get(val, {}):
                strongRow = rowDict[val][row]
                n1, n2 = strongRow[0], strongRow[1]
                for newRow in range(9):
                    if self.getOffset(newRow) == self.getOffset(n1[0]): continue
                    weakNodes = {(newRow, n1[1]), (newRow, n2[1])} & baseCopy.getAnyRowIdxs((newRow, 0), {val})
                    for weakNode in weakNodes:
                        if not baseCopy.rectCheck(strongRow, weakNode, val, isRow=True): continue
                        root, rowNode = (n1, n2) if self.inCol([weakNode, n2]) else (n2, n1)
                        eNodes = {(val, weakNode)} if val in self.layout[weakNode[0]][weakNode[1]].note else set()
                        if not eNodes: continue
                        group = (root, rowNode, weakNode)
                        note = f"Rectangle Elimination (row) removed {val} from {weakNode}. Root: {root}, rowNode: {rowNode}"
                        if not uberPrune(current_node, ("Rectangle Elimination Row", group, eNodes, None)):
                            baseCopy.updateNotesGX(eNodes)
                            diffNodes = self.puzzleDifference(baseCopy)
                            note += f" from {diffNodes}"
                            baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Rectangle Elimination Row", current_node, group)
                            newPuzzles.append(tempPuzzle)
                            rowDict, colDict = baseCopy.getRectDicts(remaining)
            for col in colDict.get(val, {}):
                strongCol = colDict[val][col]
                n1, n2 = strongCol[0], strongCol[1]
                for newCol in range(9):
                    if self.getOffset(newCol) == self.getOffset(n1[1]): continue
                    weakNodes = {(n1[0], newCol), (n2[0], newCol)} & baseCopy.getAnyColIdxs((0, newCol), {val})
                    for weakNode in weakNodes:
                        if not baseCopy.rectCheck(strongCol, weakNode, val, isRow=False): continue
                        root, colNode = (n1, n2) if self.inRow([weakNode, n2]) else (n2, n1)
                        eNodes = {(val, weakNode)} if val in self.layout[weakNode[0]][weakNode[1]].note else set()
                        if not eNodes: continue
                        group = (root, colNode, weakNode)
                        note = f"Rectangle Elimination (col) removed {val} from {weakNode}. Root: {root}, colNode: {colNode}"
                        if not uberPrune(current_node, ("Rectangle Elimination Col", group, eNodes, None)):
                            baseCopy.updateNotesGX(eNodes)
                            diffNodes = self.puzzleDifference(baseCopy)
                            note += f" from {diffNodes}"
                            baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Rectangle Elimination Col", current_node, group)
                            newPuzzles.append(tempPuzzle)
                            rowDict, colDict = baseCopy.getRectDicts(remaining)
        return baseCopy, newPuzzles
    # def rectangleElimination(self, baseCopy, current_node):
    #     newPuzzles = []
    #     remaining = self.getRemaining()
    #     rowDict, colDict = baseCopy.getRectDicts(remaining)
    #     for val in remaining:
    #         for row in rowDict.get(val, {}):
    #             strongRow = rowDict[val][row]
    #             n1, n2 = strongRow[0], strongRow[1]
    #             for newRow in range(9):
    #                 if self.getOffset(newRow) == self.getOffset(n1[0]): continue
    #                 weakNodes = {(newRow, n1[1]), (newRow, n2[1])} & baseCopy.getAnyRowIdxs((newRow, 0), {val})
    #                 for weakNode in weakNodes:
    #                     if not baseCopy.rectCheck(strongRow, weakNode, val, isRow=True): continue
    #                     root, rowNode = (n1, n2) if self.inCol([weakNode, n2]) else (n2, n1)
    #                     baseCopy.updateNotesDX([weakNode], {val})
    #                     if self.stuck(baseCopy): continue
    #                     note = f"Rectangle Elimination (row) removed {val} from {weakNode}. Root: {root}, rowNode: {rowNode}"
    #                     baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Rectangle Elimination Row", current_node)
    #                     newPuzzles.append(tempPuzzle)
    #                     rowDict, colDict = baseCopy.getRectDicts(remaining)
    #         for col in colDict.get(val, {}):
    #             strongCol = colDict[val][col]
    #             n1, n2 = strongCol[0], strongCol[1]
    #             for newCol in range(9):
    #                 if self.getOffset(newCol) == self.getOffset(n1[1]): continue
    #                 weakNodes = {(n1[0], newCol), (n2[0], newCol)} & baseCopy.getAnyColIdxs((0, newCol), {val})
    #                 for weakNode in weakNodes:
    #                     if not baseCopy.rectCheck(strongCol, weakNode, val, isRow=False): continue
    #                     root, colNode = (n1, n2) if self.inRow([weakNode, n2]) else (n2, n1)
    #                     baseCopy.updateNotesDX([weakNode], {val})
    #                     if self.stuck(baseCopy): continue
    #                     note = f"Rectangle Elimination (col) removed {val} from {weakNode}. Root: {root}, colNode: {colNode}"
    #                     baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Rectangle Elimination Col", current_node)
    #                     newPuzzles.append(tempPuzzle)
    #                     rowDict, colDict = baseCopy.getRectDicts(remaining)
    #     return baseCopy, newPuzzles
    
    def rectCheck(self, strongPair, weakNode, val, isRow=True):
        if self.inCol([weakNode, strongPair[0]]) if isRow else self.inRow([weakNode, strongPair[0]]):
            other = strongPair[1]
        else:
            other = strongPair[0]
        
        if isRow:
            intersect = (weakNode[0], other[1])
            boxIdx = (self.getOffset(weakNode[0]), self.getOffset(other[1]))
        else:
            intersect = (other[0], weakNode[1])
            boxIdx = (self.getOffset(other[0]), self.getOffset(weakNode[1]))
        
        allBoxIdxs = self.getAllBoxCoords(boxIdx)
        if not any(val in self.layout[r][c].note for r, c in allBoxIdxs): return False
        
        checkNodes = {idx for idx in allBoxIdxs 
                      if not self.inRow([intersect, idx]) and not self.inCol([intersect, idx])}
        for tempNode in checkNodes:
            if val in self.layout[tempNode[0]][tempNode[1]].note: return False
        return True
            
    def getRectDicts(self, remaining):
        rowDict, colDict = {}, {}
        for val in remaining:
            rowDict[val] = {}
            colDict[val] = {}
            for i in range(9):
                rowIdxs = self.getAnyRowIdxs((i, 0), {val})
                if len(rowIdxs) == 2 and not self.inBox(list(rowIdxs)):
                    rowDict[val][i] = tuple(rowIdxs)
                colIdxs = self.getAnyColIdxs((0, i), {val})
                if len(colIdxs) == 2 and not self.inBox(list(colIdxs)):
                    colDict[val][i] = tuple(colIdxs)
        return rowDict, colDict
    # ********************************************************************************************************************
    # sword fish works the same way as an xwing, except its for triples includes triples
    def swordfish(self, baseCopy, current_node):
        newPuzzles = []
        for val in self.getRemaining():
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
                            eNodes = set()
                            for c in tempColSet:
                                ignore_nodes = {(r, c) for r in tempRowSet}
                                eNodes |= {(val, (r, c)) for r in range(9) if val in self.layout[r][c].note and (r, c) not in ignore_nodes}
                            if not eNodes: continue
                            group = (frozenset(tempRowSet), frozenset(tempColSet))
                            note = f"Swordfish on value {val}: rows {sorted(tempRowSet)}, columns {sorted(tempColSet)}"
                            if not uberPrune(current_node, ("Swordfish Row", group, eNodes, None)):
                                baseCopy.updateNotesGX(eNodes)
                                if self.stuck(baseCopy): continue
                                diffNodes = self.puzzleDifference(baseCopy)
                                note += f" removed {val} from {diffNodes}"
                                if not any(baseCopy.stuck(newPuzzle) for newPuzzle in newPuzzles):
                                    baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Swordfish Row", current_node, group)
                                    newPuzzles.append(tempPuzzle)
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
                            eNodes = set()
                            for r in tempRowSet:
                                ignore_nodes = {(r, c) for c in tempColSet}
                                eNodes |= {(val, (r, c)) for c in range(9) if val in self.layout[r][c].note and (r, c) not in ignore_nodes}
                            if not eNodes: continue
                            group = (frozenset(tempRowSet), frozenset(tempColSet))
                            note = f"Swordfish on value {val}: columns {sorted(tempColSet)}, rows {sorted(tempRowSet)}"
                            if not uberPrune(current_node, ("Swordfish Col", group, eNodes, None)):
                                baseCopy.updateNotesGX(eNodes)
                                if self.stuck(baseCopy): continue
                                diffNodes = self.puzzleDifference(baseCopy)
                                note += f" removed {val} from {diffNodes}"
                                if not any(baseCopy.stuck(newPuzzle) for newPuzzle in newPuzzles):
                                    baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Swordfish Col", current_node, group)
                                    newPuzzles.append(tempPuzzle)
        return baseCopy, newPuzzles
    # def swordfish(self, baseCopy, current_node):
    #     newPuzzles = []
    #     for val in self.getRemaining():
    #         rowSet = {r: {c for c in range(9) if val in self.layout[r][c].note} for r in range(9) if any(val in self.layout[r][c].note for c in range(9))}
    #         rowKeys = [r for r in rowSet if 2 <= len(rowSet[r]) <= 3]
    #         for i in range(len(rowKeys)):
    #             for j in range(i + 1, len(rowKeys)):
    #                 for k in range(j + 1, len(rowKeys)):
    #                     r1, r2, r3 = rowKeys[i], rowKeys[j], rowKeys[k]
    #                     cols = rowSet[r1] | rowSet[r2] | rowSet[r3]
    #                     if len(cols) == 3:
    #                         tempRowSet = {r1, r2, r3}
    #                         tempColSet = cols
    #                         for c in tempColSet:
    #                             ignore_nodes = [(r, c) for r in tempRowSet]
    #                             baseCopy.subUpdateNotes('col', ignore_nodes, {val})
    #                         if self.stuck(baseCopy): continue
    #                         note = f"Swordfish on value {val}: rows {sorted(tempRowSet)}, columns {sorted(tempColSet)}"
    #                         if not any(baseCopy.stuck(newPuzzle) for newPuzzle in newPuzzles):
    #                             baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Swordfish Row", current_node)
    #                             newPuzzles.append(tempPuzzle)
    #         colSet = {c: {r for r in range(9) if val in self.layout[r][c].note} for c in range(9) if any(val in self.layout[r][c].note for r in range(9))}
    #         colKeys = [c for c in colSet if 2 <= len(colSet[c]) <= 3]
    #         for i in range(len(colKeys)):
    #             for j in range(i + 1, len(colKeys)):
    #                 for k in range(j + 1, len(colKeys)):
    #                     c1, c2, c3 = colKeys[i], colKeys[j], colKeys[k]
    #                     rows = colSet[c1] | colSet[c2] | colSet[c3]
    #                     if len(rows) == 3:
    #                         tempColSet = {c1, c2, c3}
    #                         tempRowSet = rows
    #                         for r in tempRowSet:
    #                             ignore_nodes = [(r, c) for c in tempColSet]
    #                             baseCopy.subUpdateNotes('row', ignore_nodes, {val})
    #                         if self.stuck(baseCopy): continue
    #                         note = f"Swordfish on value {val}: columns {sorted(tempColSet)}, rows {sorted(tempRowSet)}"
    #                         if not any(baseCopy.stuck(newPuzzle) for newPuzzle in newPuzzles):
    #                             baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Swordfish Col", current_node)
    #                             newPuzzles.append(tempPuzzle)
    #     return baseCopy, newPuzzles

    # ********************************************************************************************************************
    # xyz-wing
    def xyzWing(self, baseCopy, current_node):
        newPuzzles = []
        for i in range(9):
            for j in range(9):
                if self.layout[i][j].val != 0: continue
                tempSet = self.getSet((i, j))
                if len(tempSet) != 3: continue
                colWing, rowWing = set(), set()
                rowOffset, colOffset = self.getOffset(i), self.getOffset(j)
                for row in range(9):
                    if row == i or self.locked[row][j]: continue
                    temp = self.getSet((row, j))
                    if len(temp) == 2 and len(temp & tempSet) == 2: colWing.add((row,j))
                for col in range(9):
                    if col == j or self.locked[i][col]: continue
                    temp = self.getSet((i, col))
                    if len(temp) == 2 and len(temp & tempSet) == 2: rowWing.add((i,col))
                if len(rowWing) > 0 and len(colWing) > 0:
                    for a, b in rowWing:
                        tempRowSet = self.getSet((a, b))
                        for c, d in colWing:
                            tempColSet = self.getSet((c, d))
                            if len(tempRowSet | tempColSet | tempSet) == 3 and self.layout[a][b].note != self.layout[c][d].note:
                                valToErase = tempRowSet & tempColSet
                                if len(valToErase) != 1: continue
                                val = valToErase.pop()
                                eCells = set()
                                if self.inBox([(i, j), (a, b)]) and not self.inBox([(i, j), (c, d)]):
                                    eCells = {(eRow, j) for eRow in range(rowOffset, rowOffset + 3) if eRow != i}
                                elif self.inBox([(i, j), (c, d)]) and not self.inBox([(i, j), (a, b)]):
                                    eCells = {(i, eCol) for eCol in range(colOffset, colOffset + 3) if eCol != j}
                                eNodes = {(val, (r, c)) for r, c in eCells if val in self.layout[r][c].note}
                                if not eNodes: continue
                                group = ((i,j),(a,b),(c,d))
                                note = f"XYZ-Wing Sit 1 Root: {(i, j)}, rowWing {(a, b)}, colWing{(c, d)}\nErasing {val}"
                                if not uberPrune(current_node, ("XYZ-Wing L", group, eNodes, None)):
                                    baseCopy.updateNotesGX(eNodes)
                                    diffNodes = self.puzzleDifference(baseCopy)
                                    note += f" at {diffNodes}"
                                    baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "XYZ-Wing L", current_node, group)
                                    newPuzzles.append(tempPuzzle)
                elif len(rowWing) > 0 and len(colWing) == 0:
                    for x, y in rowWing:
                        if self.inBox([(x, y), (i, j)]): continue
                        tempRowSet = self.getSet((x, y))
                        for a in range(rowOffset, rowOffset + 3):
                            if a == i: continue
                            for b in range(colOffset, colOffset + 3):
                                if b == j: continue
                                tempBoxSet = self.getSet((a, b))
                                if len(tempBoxSet) == 2 and len(tempBoxSet | tempRowSet | tempSet) == 3 and tempBoxSet != tempRowSet:
                                    eVal = (tempRowSet & tempBoxSet).pop()
                                    eCells = {(i, eCol) for eCol in range(colOffset, colOffset + 3) if eCol != j}
                                    eNodes = {(eVal, (r, c)) for r, c in eCells if eVal in self.layout[r][c].note}
                                    if not eNodes: continue
                                    group = ((i,j),(x,y),(a,b))
                                    note = f"XYZ-Wing Sit 2 Row, Root: ({i}, {j}), rowWing {(x, y)}, boxWing {(a, b)}"
                                    if not uberPrune(current_node, ("XYZ-Wing Box (Row)", group, eNodes, None)):
                                        baseCopy.updateNotesGX(eNodes)
                                        diffNodes = self.puzzleDifference(baseCopy)
                                        note += f" removed {eVal} from {diffNodes}"
                                        baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "XYZ-Wing Box (Row)", current_node, group)
                                        newPuzzles.append(tempPuzzle)
                elif len(colWing) > 0 and len(rowWing) == 0:
                    for x, y in colWing:
                        if self.inBox([(x, y), (i, j)]): continue
                        tempColSet = self.getSet((x, y))
                        for a in range(rowOffset, rowOffset + 3):
                            if a == i: continue
                            for b in range(colOffset, colOffset + 3):
                                if b == j: continue
                                tempBoxSet = self.getSet((a, b))
                                if len(tempBoxSet) == 2 and len(tempBoxSet | tempColSet | tempSet) == 3 and tempBoxSet != tempColSet:
                                    eVal = (tempColSet & tempBoxSet).pop()
                                    eCells = {(eRow, j) for eRow in range(rowOffset, rowOffset + 3) if eRow != i}
                                    eNodes = {(eVal, (r, c)) for r, c in eCells if eVal in self.layout[r][c].note}
                                    if not eNodes: continue
                                    group = ((i,j),(x,y),(a,b))
                                    note = f"XYZ-Wing Sit 2 Col, Root: ({i}, {j}), colWing {(x, y)}, boxWing {(a, b)}"
                                    if not uberPrune(current_node, ("XYZ-Wing Box (Col)", group, eNodes, None)):
                                        baseCopy.updateNotesGX(eNodes)
                                        diffNodes = self.puzzleDifference(baseCopy)
                                        note += f" removed {eVal} from {diffNodes}"
                                        baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "XYZ-Wing Box (Col)", current_node, group)
                                        newPuzzles.append(tempPuzzle)
        return baseCopy, newPuzzles
    # def xyzWing(self, baseCopy, current_node):
    #     newPuzzles = []
    #     for i in range(9):
    #         for j in range(9):
    #             if self.layout[i][j].val != 0: continue
    #             tempSet = self.getSet((i, j))
    #             if len(tempSet) != 3: continue
    #             colWing, rowWing = set(), set()
    #             rowOffset, colOffset = self.getOffset(i), self.getOffset(j)
    #             # looks for candidate in column
    #             for row in range(9):
    #                 if row == i or self.locked[row][j]: continue
    #                 temp = self.getSet((row, j))
    #                 if len(temp) == 2 and len(temp & tempSet) == 2: colWing.add((row,j))
    #             # looks for candidate in row
    #             for col in range(9):
    #                 if col == j or self.locked[i][col]: continue
    #                 temp = self.getSet((i, col))
    #                 if len(temp) == 2 and len(temp & tempSet) == 2: rowWing.add((i,col))
    #             if len(rowWing) > 0 and len(colWing) > 0:
    #                 for a, b in rowWing:
    #                     tempRowSet = self.getSet((a, b))
    #                     for c, d in colWing:
    #                         tempColSet = self.getSet((c, d))
    #                         if len(tempRowSet | tempColSet | tempSet) == 3 and self.layout[a][b].note != self.layout[c][d].note:
    #                             valToErase, eNodes = tempRowSet & tempColSet, set() 
    #                             if len(valToErase) != 1: continue
    #                             val = valToErase.pop()
    #                             if self.inBox([(i, j), (a, b)]) and not self.inBox([(i, j), (c, d)]):
    #                                 eNodes = set()
    #                                 for eRow in range(rowOffset, rowOffset + 3):
    #                                     if eRow == i: continue
    #                                     eNodes.add((eRow, j))
    #                             elif self.inBox([(i, j), (c, d)]) and not self.inBox([(i, j), (a, b)]):
    #                                 for eCol in range(colOffset, colOffset + 3):
    #                                     if eCol == j: continue 
    #                                     eNodes.add((i, eCol))
    #                             baseCopy.updateNotesDX(list(eNodes), {val})
    #                             if self.stuck(baseCopy): continue
    #                             eNodes = self.puzzleDifference(baseCopy)
    #                             note = f"XYZ-Wing Sit 1 Root: {(i, j)}, rowWing {(a, b)}, colWing{(c, d)}\nErasing {val} at {eNodes}"
    #                             baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "XYZ-Wing L", current_node)
    #                             newPuzzles.append(tempPuzzle)
    #             elif len(rowWing) > 0 and len(colWing) == 0:
    #                 for x, y in rowWing:
    #                     if self.inBox([(x, y), (i, j)]): continue
    #                     tempRowSet = self.getSet((x, y))
    #                     for a in range(rowOffset, rowOffset + 3):
    #                         if a == i: continue
    #                         for b in range(colOffset, colOffset + 3):
    #                             if b == j: continue
    #                             tempBoxSet = self.getSet((a, b))
    #                             if len(tempBoxSet) == 2 and len(tempBoxSet | tempRowSet | tempSet) == 3 and tempBoxSet != tempRowSet:
    #                                 eVal, eNodes = (tempRowSet & tempBoxSet).pop(), set()
    #                                 for eCol in range(colOffset, colOffset + 3):
    #                                     if eCol == j: continue
    #                                     eNodes.add((i, eCol))
    #                                 baseCopy.updateNotesDX(list(eNodes), {eVal})
    #                                 if self.stuck(baseCopy): continue
    #                                 eNodes = self.puzzleDifference(baseCopy)
    #                                 note = f"XYZ-Wing Sit 2 Row, Root: ({i}, {j}), rowWing {(x, y)}, boxWing {(a, b)}"
    #                                 baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "XYZ-Wing Box (Row)", current_node)
    #                                 newPuzzles.append(tempPuzzle)
    #             elif len(colWing) > 0 and len(rowWing) == 0:
    #                 for x, y in colWing:
    #                     if self.inBox([(x, y), (i, j)]): continue
    #                     tempColSet = self.getSet((x, y))
    #                     for a in range(rowOffset, rowOffset + 3):
    #                         if a == i: continue
    #                         for b in range(colOffset, colOffset + 3):
    #                             if b == j: continue
    #                             tempBoxSet = self.getSet((a, b))
    #                             if len(tempBoxSet) == 2 and len(tempBoxSet | tempColSet | tempSet) == 3 and tempBoxSet != tempColSet:
    #                                 eVal, eNodes = (tempColSet & tempBoxSet).pop(), set()
    #                                 for eRow in range(rowOffset, rowOffset + 3):
    #                                     if eRow == i: continue
    #                                     eNodes.add((eRow, j))
    #                                 baseCopy.updateNotesDX(list(eNodes), {eVal})
    #                                 if self.stuck(baseCopy): continue
    #                                 eNodes = self.puzzleDifference(baseCopy)
    #                                 note = f"XYZ-Wing Sit 2 Col, Root: ({i}, {j}), colWing {(x, y)}, boxWing {(a, b)}"
    #                                 baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "XYZ-Wing Box (Col)", current_node)
    #                                 newPuzzles.append(tempPuzzle)
    #     return baseCopy, newPuzzles
    # ********************************************************************************************************************
    def bug(self):
        bugx, bugy, bugFound = -1, -1, False
        for i in range(9):
            for j in range(9):
                if self.locked[i][j]: continue
                tempSet = self.getSet((i, j))
                if len(tempSet) > 3 or (len(tempSet) == 3 and bugFound): return
                if len(tempSet) == 3:
                    bugx, bugy, bugFound = i, j, True
        if not bugFound: return
        for val in self.getSet((bugx, bugy)):
            if sum(1 for r in range(9) if val in self.layout[r][bugy].note) % 2 == 1:
                self.layout[bugx][bugy].setVal(val, (bugx, bugy))
                return True
        return False
    # ********************************************************************************************************************
    # ***********************************************DIABOLICAL STRATEGIES************************************************
    # ********************************************************************************************************************
    def xCycles(self, baseCopy, current_node):
        newPuzzles = []
        remaining = self.getRemaining()
        functions = {(self.inRow, self.getAnyRowIdxs), (self.inCol, self.getAnyColIdxs), (self.inBox, self.getAnyBoxIdxs)}
        for val in remaining:
            strongLinks, weakLinks = self.getAllXCConnectedNodes(val)
            completedCycles = self.getXCycle(strongLinks, weakLinks, val)
            completedCycles.sort(key=lambda x: len(x[1]))
            for cType, cycle in completedCycles:
                t1eNodes, t2fNodes, t3eNodes = set(), set(), set()
                if cType == 1:
                    for idx in range(1, len(cycle), 2):
                        nextIdx = (idx + 1) % len(cycle)
                        for typeFunc, getFunc in functions:
                            if typeFunc([cycle[idx], cycle[nextIdx]]):
                                t1eNodes |= getFunc(cycle[idx], {val}) - {cycle[idx], cycle[nextIdx]}
                elif cType == 2:
                    t2fNodes.add(cycle[0])
                elif cType == 3:
                    end1, end2 = cycle[0], cycle[-2]
                    end1Connections = (self.getAnyRowIdxs(end1, {val}) |
                                       self.getAnyColIdxs(end1, {val}) |
                                       self.getAnyBoxIdxs(end1, {val})) - {end1}
                    end2Connections = (self.getAnyRowIdxs(end2, {val}) |
                                       self.getAnyColIdxs(end2, {val}) |
                                       self.getAnyBoxIdxs(end2, {val})) - {end2}
                    t3eNodes |= (end1Connections & end2Connections) - set(cycle)

                t3eNodes -= t1eNodes
                note = f""
                for x in cycle:
                    note += f"{x}\n"
                if t1eNodes:
                    eNodes = {(val, node) for node in t1eNodes if val in self.layout[node[0]][node[1]].note}
                    if eNodes and not uberPrune(current_node, ("X-Cycles Type 1", cycle, eNodes, None)):
                        baseCopy.updateNotesGX(eNodes)
                        if self.stuck(baseCopy): continue
                        diffNodes = self.puzzleDifference(baseCopy)
                        note += f"X-Cycles Rule 1 removing {val} from: {diffNodes}"
                        baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "X-Cycles Type 1", current_node, cycle)
                        if not any(tempPuzzle.stringRepAll() == p.stringRepAll() for p in newPuzzles):
                            newPuzzles.append(tempPuzzle)
                elif t2fNodes:
                    eNodes = set()
                    for node in t2fNodes:
                        r, c = node
                        for otherVal in self.getSet(node):
                            if otherVal != val and otherVal in self.layout[r][c].note:
                                eNodes.add((otherVal, node))
                    if eNodes and not uberPrune(current_node, ("X-Cycles Type 2", cycle, eNodes, None)):
                        # # DEBUG PRINT
                        # print(f"Type 2 cycle for val={val}: {cycle}")
                        # for i in range(len(cycle)):
                        #     a = cycle[i]
                        #     b = cycle[(i+1) % len(cycle)]
                        #     isStrong = b in strongLinks.get(a, set())
                        #     isWeak = b in weakLinks.get(a, set())
                        #     print(f"  {a} -> {b}: strong={isStrong}, weak={isWeak}")
                        # # END DEBUG PRINT
                        baseCopy.updateNotesGX(eNodes)
                        if self.stuck(baseCopy): continue
                        diffNodes = self.puzzleDifference(baseCopy)
                        note += f"X-Cycles Rule 2 found {val} at node(s): {t2fNodes}, removing {diffNodes}"
                        baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "X-Cycles Type 2", current_node, cycle)
                        if not any(tempPuzzle.stringRepAll() == p.stringRepAll() for p in newPuzzles):
                            newPuzzles.append(tempPuzzle)
                elif t3eNodes:
                    eNodes = {(val, node) for node in t3eNodes if val in self.layout[node[0]][node[1]].note}
                    if eNodes and not uberPrune(current_node, ("X-Cycles Type 3", cycle, eNodes, None)):
                        baseCopy.updateNotesGX(eNodes)
                        if self.stuck(baseCopy): continue
                        diffNodes = self.puzzleDifference(baseCopy)
                        note += f"X-Cycles Rule 3 removing {val} from: {diffNodes}"
                        baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "X-Cycles Type 3", current_node, cycle)
                        if not any(tempPuzzle.stringRepAll() == p.stringRepAll() for p in newPuzzles):
                            newPuzzles.append(tempPuzzle)
        return baseCopy, newPuzzles
    
    # def xCycles(self, baseCopy, current_node):
    #     newPuzzles = []
    #     remaining = self.getRemaining()
    #     functions = {(self.inRow, self.getAnyRowIdxs), (self.inCol, self.getAnyColIdxs), (self.inBox, self.getAnyBoxIdxs)}
    #     for val in remaining:
    #         strongLinks, weakLinks = self.getAllXCConnectedNodes(val)
    #         completedCycles = self.getXCycle(strongLinks, weakLinks)
    #         t1eNodes, t2fNodes, t3eNodes = set(), set(), set()
    #         for cType, cycle in completedCycles:
    #             if cType == 1:
    #                 for idx in range(1, len(cycle), 2):
    #                     for typeFunc, getFunc in functions:
    #                         if typeFunc([cycle[idx], cycle[idx + 1]]):
    #                             t1eNodes|= getFunc(cycle[idx], {val}) - {cycle[idx], cycle[idx + 1]}
    #             if cType == 2:
    #                 t2fNodes.add(cycle[0])
    #             if cType == 3:
    #                 t3eNodes.add(cycle[-2])
    #         t3eNodes -= t1eNodes
    #         if t1eNodes:
    #             baseCopy.updateNotesDX(t1eNodes, {val})
    #             if self.stuck(baseCopy): continue
    #             note = f"{t1eNodes}\nX-Cycles Rule 1 removing {val} from: {t1eNodes}"
    #             if not any(baseCopy.stuck(newPuzzle) for newPuzzle in newPuzzles):
    #                 baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "X-Cycles Type 1", current_node, completedCycles)
    #                 newPuzzles.append(tempPuzzle)
    #         if t2fNodes:
    #             for node in t2fNodes:
    #                 baseCopy.layout[node[0]][node[1]].setVal(val, node)
    #             if self.stuck(baseCopy): continue
    #             note = f"{t2fNodes}\nX-Cycles Rule 2 found {val} at node(s): {t2fNodes}"
    #             if not any(baseCopy.stuck(newPuzzle) for newPuzzle in newPuzzles):
    #                 baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "X-Cycles Type 2", current_node, completedCycles)
    #                 newPuzzles.append(tempPuzzle)
    #         if t3eNodes:
    #             print(f"XCycles Rule 3 removing {val} from: {t3eNodes}")
    #             baseCopy.updateNotesDX(t3eNodes, {val})
    #             if self.stuck(baseCopy): continue
    #             note = f"{t3eNodes}\nX-Cycles Rule 3 removing {val} from: {t3eNodes}"
    #             if not any(baseCopy.stuck(newPuzzle) for newPuzzle in newPuzzles):
    #                 baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "X-Cycles Type 3", current_node, completedCycles)
    #                 newPuzzles.append(tempPuzzle)
    #     return baseCopy, newPuzzles
        
    def getXCycle(self, strongLinks, weakLinks, val):
        completedCycles = []
        seen = set()
        stack = [[node] for node in strongLinks.keys()]
        
        while stack:
            path = stack.pop()
            last = path[-1]
            useStrong = (len(path) % 2 == 1)
            links = strongLinks if useStrong else weakLinks
            if last not in links: continue
            path_set = set(path)
            
            for nxt in links[last]:
                if len(path) >= 2 and nxt == path[-2]: continue
                if nxt in path_set and nxt != path[0]: continue
                if nxt == path[0] and len(path) >= 4:
                    cycle = path
                    min_idx = cycle.index(min(cycle))
                    rotated = cycle[min_idx:] + cycle[:min_idx]
                    forward = tuple(rotated)
                    backward = tuple([rotated[0]] + list(reversed(rotated[1:])))
                    canonical = min(forward, backward)
                    if canonical not in seen:
                        seen.add(canonical)
                        # cType = self.classifyXCycle(list(canonical), strongLinks, weakLinks, val)
                        # if cType is None: continue
                        # completedCycles.append((cType, list(canonical)))
                        # ------------------------------------------------
                        cType, validRotation = self.classifyXCycle(list(canonical), strongLinks, weakLinks, val)
                        if cType is None: continue
                        completedCycles.append((cType, validRotation))
                else:
                    stack.append(path + [nxt])
        
        completedCycles.sort(key=lambda x: x[0])
        return completedCycles

    # def classifyXCycle(self, cycle, strongLinks, weakLinks):
    #     n = len(cycle)
    #     # check that all links exist and properly alternate strong/(strong or weak)
    #     # odd positions (0->1, 2->3, etc.) must be strong
    #     # even positions (1->2, 3->4, etc.) can be strong or weak
    #     for i in range(n):
    #         a = cycle[i]
    #         b = cycle[(i + 1) % n]
    #         isStrong = b in strongLinks.get(a, set())
    #         isWeak = b in weakLinks.get(a, set())
    #         if i % 2 == 0:
    #             if not isStrong:
    #                 if n == 4:
    #                     print(f"Length-4 cycle rejected at position {i}: {a} -> {b}, isStrong={isStrong}, isWeak={isWeak}")
    #                 return None
    #         if i % 2 == 0:  # must be strong
    #             if not isStrong:
    #                 return None  # invalid cycle
    #         else:  # can be strong or weak
    #             if not isStrong and not isWeak:
    #                 return None  # invalid cycle
        
    #     # closing link is between cycle[-1] and cycle[0], which is index n-1 (even if n is odd)
    #     closingLinkIsStrong = cycle[0] in strongLinks.get(cycle[-1], set())
        
    #     if n % 2 == 0:
    #         return 1  # even length, all alternating = nice cycle
    #     else:
    #         if closingLinkIsStrong:
    #             return 2  # odd length, closing link strong = type 2
    #         else:
    #             return 3  # odd length, closing link weak = type 3
    # def classifyXCycle(self, cycle, strongLinks, weakLinks):
    #     n = len(cycle)
        
    #     def checkPhase(c):
    #         for i in range(n):
    #             a = c[i]
    #             b = c[(i + 1) % n]
    #             isStrong = b in strongLinks.get(a, set())
    #             isWeak = b in weakLinks.get(a, set())
    #             if i % 2 == 0:  # must be strong
    #                 if not isStrong:
    #                     return False
    #             else:  # can be strong or weak
    #                 if not isStrong and not isWeak:
    #                     return False
    #         return True
        
    #     # try both phases — original and shifted by 1
    #     for shift in range(n):
    #         rotated = cycle[shift:] + cycle[:shift]
    #         if checkPhase(rotated):
    #             closingLinkIsStrong = rotated[0] in strongLinks.get(rotated[-1], set())
    #             if n % 2 == 0:
    #                 return 1
    #             else:
    #                 return 2 if closingLinkIsStrong else 3
    #     if n == 4:
    #         print(f"Length-4 cycle rejected entirely: {cycle}")
    #     return None

    def classifyXCycle(self, cycle, strongLinks, weakLinks, val):
        n = len(cycle)
        
        for i in range(n):
            a = cycle[i]
            b = cycle[(i + 1) % n]
            c = cycle[(i + 2) % n]
            ab_strong = b in strongLinks.get(a, set())
            bc_strong = c in strongLinks.get(b, set())
            if not ab_strong and not bc_strong:
                return None, None
    
        def checkPhase(c):
            for i in range(n):
                a = c[i]
                b = c[(i + 1) % n]
                isStrong = b in strongLinks.get(a, set())
                isWeak = b in weakLinks.get(a, set())
                if i % 2 == 0:
                    if not isStrong:
                        return False
                else:
                    if not isStrong and not isWeak:
                        return False
            return True
        
        for shift in range(n):
            rotated = cycle[shift:] + cycle[:shift]
            if checkPhase(rotated):
                closingLinkIsStrong = rotated[0] in strongLinks.get(rotated[-1], set())
                if n % 2 == 0:
                    return 1, rotated
                else:
                    return (2 if closingLinkIsStrong else 3), rotated
        
        return None, None
    
    # def getXCycle(self, strongLinks, weakLinks):
    #     completedCycles = []
    #     seen = set()
    #     stack = [[node] for node in strongLinks.keys()]
        
    #     while stack:
    #         path = stack.pop()
    #         last = path[-1]
    #         useStrong = (len(path) % 2 == 1)
    #         links = strongLinks if useStrong else weakLinks
    #         if last not in links: continue
    #         path_set = set(path)
            
    #         for nxt in links[last]:
    #             if len(path) >= 2 and nxt == path[-2]: continue
    #             if nxt in path_set and nxt != path[0]: continue
    #             # nlr1, nlr2, nlr3 logic here...
    #             stack.append(path + [nxt])
        
    #     completedCycles.sort(key=lambda x: x[0])
    #     return completedCycles

    def getAllXCConnectedNodes(self, val):
        strongLinks, weakLinks = {}, {}
        
        def add_link(d, a, b):
            d.setdefault(a, set()).add(b)
            d.setdefault(b, set()).add(a)
    
        sources = []
        for row in range(9):
            sources.append(self.getAnyRowIdxs((row, 0), {val}))
        for col in range(9):
            sources.append(self.getAnyColIdxs((0, col), {val}))
        for rBox in range(0, 9, 3):
            for cBox in range(0, 9, 3):
                sources.append(self.getAnyBoxIdxs((rBox, cBox), {val}))
    
        for idxs in sources:
            if not idxs: continue
            if len(idxs) == 2:
                a, b = tuple(idxs)
                add_link(strongLinks, a, b)
                add_link(weakLinks, a, b)
            elif len(idxs) > 2:
                for a, b in itertools.combinations(idxs, 2):
                    add_link(weakLinks, a, b)  # remove the strongLinks check
    
        return strongLinks, weakLinks
    
    # def getAllXCConnectedNodes(self, val):
    #     strongLinks, weakLinks = {}, {}
        
    #     def add_link(d, a, b):
    #         d.setdefault(a, set()).add(b)
    #         d.setdefault(b, set()).add(a)
    
    #     sources = []
    #     for row in range(9):
    #         sources.append(self.getAnyRowIdxs((row, 0), {val}))
    #     for col in range(9):
    #         sources.append(self.getAnyColIdxs((0, col), {val}))
    #     for rBox in range(0, 9, 3):
    #         for cBox in range(0, 9, 3):
    #             sources.append(self.getAnyBoxIdxs((rBox, cBox), {val}))
    
    #     for idxs in sources:
    #         if not idxs: continue
    #         if len(idxs) == 2:
    #             a, b = tuple(idxs)
    #             add_link(strongLinks, a, b)
    #             add_link(weakLinks, a, b)
    #         elif len(idxs) > 2:
    #             for a, b in itertools.combinations(idxs, 2):
    #                 if b not in strongLinks.get(a, ()):
    #                     add_link(weakLinks, a, b)
    
    #     return strongLinks, weakLinks
        
    # ********************************************************************************************************************
    def medusa3D(self, baseCopy, current_node):
        newPuzzles = []
        
        remaining = sorted(self.getRemaining())
        completedGroups = []
        medusaLinks = self.getMedusaLinks(remaining)
        
        for val in remaining:
            nodesDone = set()
            for i in range(9):
                for j in range(9):
                    if val not in self.layout[i][j].note: continue
                    if (i, j, val, 'yellow') in nodesDone or (i, j, val, 'green') in nodesDone: continue
                    firstNode = (i, j, val, 'green')
                    group = [[firstNode]]
                    nodesDone.add(firstNode)
                    while True:
                        nextLayer = []
                        for currentNode in group[-1]:
                            for neighbor in self.getMedusaNeighbors(currentNode, nodesDone, medusaLinks):
                                nodesDone.add(neighbor)
                                nextLayer.append(neighbor)
                        if not nextLayer:
                            break
                        group.append(nextLayer)
                    if sum(len(layer) for layer in group) > 2:
                        completedGroups.append(group)
        
        seenChains = set()
        uniqueGroups = []
        for group in completedGroups:
            nodes = frozenset((r, c, d) for chain_step in group for (r, c, d, color) in chain_step)
            if nodes not in seenChains:
                seenChains.add(nodes)
                uniqueGroups.append(group)
        
        for group in uniqueGroups:
            normalized = [node for layer in group for node in layer]
            normalized_set = set(normalized)
            groupStr = '\n'.join(str(layer) for layer in group) + '\n'
            puzFlipGroup = [[(x, y, v) for x, y, v, c in layer] for layer in group]
            eCells4, eCells5 = {}, {}

            connections = {}
            for x, y, v, c in normalized:
                if (x, y, v) not in connections:
                    connections[(x, y, v)] = (
                        self.getAnyRowIdxs((x, y), {v}) |
                        self.getAnyColIdxs((x, y), {v}) |
                        self.getAnyBoxIdxs((x, y), {v})
                    ) - {(x, y)}

            for a, b in itertools.combinations(normalized, 2):
                ax, ay, aVal, aColor = a
                bx, by, bVal, bColor = b
                if a == b: continue

                # Rule 1
                if (ax, ay, aColor) == (bx, by, bColor) and aVal != bVal:
                    eNodes = set()
                    note = f"{groupStr}3D Medusa Rule 1 found {aVal} at {(ax, ay)} and {bVal} at {(bx, by)}, removing all {aColor} nodes\n"
                    for x, y, v, color in normalized:
                        if color == aColor:
                            if v in self.layout[x][y].note:
                                eNodes.add((v, (x, y)))
                    if eNodes and not uberPrune(current_node, ("3D Medusa Rule 1", puzFlipGroup, eNodes, None)):
                        baseCopy.updateNotesGX(eNodes)
                        diffNodes = self.puzzleDifference(baseCopy)
                        note += f"Removing {diffNodes}\n"
                        baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "3D Medusa Rule 1", current_node, puzFlipGroup)
                        newPuzzles.append(tempPuzzle)
                    continue

                # Rule 2
                if (aVal, aColor) == (bVal, bColor) and self.hasConnection([(ax, ay), (bx, by)]):
                    eNodes = set()
                    note = f"{groupStr}3D Medusa Rule 2 found {aVal} at {(ax, ay)} and {bVal} at {(bx, by)}, removing all {aColor} nodes\n"
                    for x, y, v, color in normalized:
                        if color == aColor:
                            if v in self.layout[x][y].note:
                                eNodes.add((v, (x, y)))
                    if eNodes and not uberPrune(current_node, ("3D Medusa Rule 2", puzFlipGroup, eNodes, None)):
                        baseCopy.updateNotesGX(eNodes)
                        diffNodes = self.puzzleDifference(baseCopy)
                        note += f"Removing {diffNodes}\n"
                        baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "3D Medusa Rule 2", current_node, puzFlipGroup)
                        newPuzzles.append(tempPuzzle)
                    continue

                # Rule 3
                if (ax, ay) == (bx, by) and aColor != bColor and aVal != bVal and len(medusaLinks.get((ax, ay, aVal), set())) == 1 and len(medusaLinks.get((bx, by, bVal), set())) == 1 and len(self.getSet((ax, ay))) > 2:
                    eNodes = set()
                    note = f"{groupStr}3D Medusa Rule 3 {(ax, ay, aVal, aColor)} {(bx, by, bVal, bColor)}\n"
                    for v in self.getSet((ax, ay)):
                        if v == aVal or v == bVal: continue
                        if v in self.layout[ax][ay].note:
                            eNodes.add((v, (ax, ay)))
                    if eNodes and not uberPrune(current_node, ("3D Medusa Rule 3", puzFlipGroup, eNodes, None)):
                        baseCopy.updateNotesGX(eNodes)
                        diffNodes = self.puzzleDifference(baseCopy)
                        note += f"Removing {diffNodes}\n"
                        baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "3D Medusa Rule 3", current_node, puzFlipGroup)
                        newPuzzles.append(tempPuzzle)
                    continue

                # Rule 4 set creator
                if aVal == bVal and aColor != bColor:
                    green_cell = (ax, ay) if aColor == 'green' else (bx, by)
                    yellow_cell = (ax, ay) if aColor == 'yellow' else (bx, by)
                    candidates = connections.get((green_cell[0], green_cell[1], aVal), set()) & \
                                 connections.get((yellow_cell[0], yellow_cell[1], aVal), set())
                    for cell in candidates:
                        if (cell[0], cell[1], aVal, 'green') not in normalized_set and \
                           (cell[0], cell[1], aVal, 'yellow') not in normalized_set:
                            eCells4.setdefault(aVal, set()).add(cell)

                # Rule 5 set creator
                if (ax, ay) == (bx, by) or aColor == bColor or aVal == bVal or not self.hasConnection([(ax, ay), (bx, by)]): continue
                if bVal in self.getSet((ax, ay)):
                    eCells5.setdefault(bVal, set()).add((ax, ay))
                if aVal in self.getSet((bx, by)):
                    eCells5.setdefault(aVal, set()).add((bx, by))

            # Rule 4
            if eCells4:
                eNodes = {(v, cell) for v, cells in eCells4.items() for cell in cells if v in self.layout[cell[0]][cell[1]].note}
                if eNodes and not uberPrune(current_node, ("3D Medusa Rule 4", puzFlipGroup, eNodes, None)):
                    note = f"{groupStr}3D Medusa Rule 4\n"
                    baseCopy.updateNotesGX(eNodes)
                    diffNodes = self.puzzleDifference(baseCopy)
                    note += f"Removing {diffNodes}\n"
                    baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "3D Medusa Rule 4", current_node, puzFlipGroup)
                    newPuzzles.append(tempPuzzle)
            eCells4 = {}

            # Rule 5
            if eCells5:
                eNodes = {(v, cell) for v, cells in eCells5.items() for cell in cells if v in self.layout[cell[0]][cell[1]].note}
                if eNodes and not uberPrune(current_node, ("3D Medusa Rule 5", puzFlipGroup, eNodes, None)):
                    note = f"{groupStr}3D Medusa Rule 5\n"
                    baseCopy.updateNotesGX(eNodes)
                    diffNodes = self.puzzleDifference(baseCopy)
                    note += f"Removing {diffNodes}\n"
                    baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "3D Medusa Rule 5", current_node, puzFlipGroup)
                    newPuzzles.append(tempPuzzle)
            eCells5 = {}

            # Rule 6
            normalized_cells = {(x, y) for x, y, v, c in normalized}
            for i in range(9):
                for j in range(9):
                    if self.locked[i][j] or (i, j) in normalized_cells: continue
                    tempSet = self.getSet((i, j))
                    if not tempSet: continue
                    goal = {color: {v: set() for v in tempSet} for color in {'yellow', 'green'}}
                    for x, y, v, color in normalized:
                        if v in tempSet and (x, y) in connections.get((i, j, v), set()):
                            goal[color][v].add((x, y))
                    for color, vals in goal.items():
                        if any(not coords for coords in vals.values()): continue
                        eNodes = set()
                        for x, y, v, eColor in normalized:
                            if eColor != color: continue
                            if v in self.layout[x][y].note:
                                eNodes.add((v, (x, y)))
                        if eNodes and not uberPrune(current_node, ("3D Medusa Rule 6", puzFlipGroup, eNodes, None)):
                            note = f"{groupStr}3D Medusa Rule 6 removing all {color} nodes\n"
                            baseCopy.updateNotesGX(eNodes)
                            diffNodes = self.puzzleDifference(baseCopy)
                            note += f"Removing {diffNodes}\n"
                            baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "3D Medusa Rule 6", current_node, puzFlipGroup)
                            newPuzzles.append(tempPuzzle)

        return baseCopy, newPuzzles
    # def medusa3D(self, baseCopy, current_node):
    #     newPuzzles = []
        
    #     timer = time.perf_counter()
    #     remaining = sorted(self.getRemaining())
    #     completedGroups = []
    #     medusaLinks = self.getMedusaLinks(remaining)
        
    #     for val in remaining:
    #         nodesDone = set()
    #         for i in range(9):
    #             for j in range(9):
    #                 if val not in self.layout[i][j].note: continue
    #                 if (i, j, val, 'yellow') in nodesDone or (i, j, val, 'green') in nodesDone: continue
    #                 firstNode = (i, j, val, 'green')
    #                 group = [[firstNode]]
    #                 nodesDone.add(firstNode)
    #                 while True:
    #                     nextLayer = []
    #                     for currentNode in group[-1]:
    #                         for neighbor in self.getMedusaNeighbors(currentNode, nodesDone, medusaLinks):
    #                             nodesDone.add(neighbor)
    #                             nextLayer.append(neighbor)
    #                     if not nextLayer:
    #                         break
    #                     group.append(nextLayer)
    #                 if sum(len(layer) for layer in group) > 2:
    #                     completedGroups.append(group)
        
    #     seenChains = set()
    #     uniqueGroups = []
        
    #     for group in completedGroups:
    #         # flatten all nodes in the group, strip color
    #         nodes = frozenset(
    #             (r, c, d)
    #             for chain_step in group
    #             for (r, c, d, color) in chain_step
    #         )
    #         if nodes not in seenChains:
    #             seenChains.add(nodes)
    #             uniqueGroups.append(group)
        
    #     for group in uniqueGroups:
    #         normalized = [node for layer in group for node in layer]
    #         normalized_set = set(normalized)
    #         groupStr = '\n'.join(str(layer) for layer in group) + '\n'
    #         puzFlipGroup = [[(x, y, v) for x, y, v, c in layer] for layer in group]
    #         eCells, eCells4, eCells5 = {}, {}, {}

    #         connections = {}
    #         for x, y, v, c in normalized:
    #             if (x, y, v) not in connections:
    #                 connections[(x, y, v)] = (
    #                     self.getAnyRowIdxs((x, y), {v}) |
    #                     self.getAnyColIdxs((x, y), {v}) |
    #                     self.getAnyBoxIdxs((x, y), {v})
    #                 ) - {(x, y)}

            
    #         for a, b in itertools.combinations(normalized, 2):
    #             ax, ay, aVal, aColor = a
    #             bx, by, bVal, bColor = b
    #             if a == b: continue
    #                 # rule 1
    #             if (ax, ay, aColor) == (bx, by, bColor) and aVal != bVal:
    #                 note = f"{groupStr}3D Medusa Rule 1 found {aVal} at {(ax, ay)} and {bVal} at {(bx, by)}, removing all {aColor} nodes\n"
    #                 for x, y, val, color in normalized:
    #                     if color == aColor == bColor:
    #                         if val not in eCells:
    #                             eCells[val] = set()
    #                         eCells[val].add((x, y))
    #                 for val, cells in eCells.items():
    #                     note += f"Removing {val} from {cells}\n"
    #                     baseCopy.updateNotesDX(cells, {val})
    #                 if not any(baseCopy.stuck(newPuzzle) for newPuzzle in newPuzzles):
    #                     baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "3D Medusa Rule 1", current_node, puzFlipGroup)
    #                     newPuzzles.append(tempPuzzle)
    #             # Rule 2
    #             if (aVal, aColor) == (bVal, bColor) and self.hasConnection([(ax, ay), (bx, by)]):
    #                 note = f"{groupStr}3D Medusa Rule 2 found {aVal} at {(ax, ay)} and {bVal} at {(bx, by)}, removing all {aColor} nodes\n"
    #                 for x, y, val, color in normalized:
    #                     if color == aColor == bColor:
    #                         if val not in eCells:
    #                             eCells[val] = set()
    #                         eCells[val].add((x, y))
    #                 for val, cells in eCells.items():
    #                     note += f"Removing {val} from {cells}\n"
    #                     baseCopy.updateNotesDX(cells, {val})
    #                 if not any(baseCopy.stuck(newPuzzle) for newPuzzle in newPuzzles):
    #                     baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "3D Medusa Rule 2", current_node, puzFlipGroup)
    #                     newPuzzles.append(tempPuzzle)
                
    #             # Rule 3
    #             if (ax, ay) == (bx, by) and aColor != bColor and aVal != bVal and len(medusaLinks.get((ax, ay, aVal), set())) == 1 and len(medusaLinks.get((bx, by, bVal), set())) == 1 and len(self.getSet((ax, ay))) > 2:
    #                 note = f"{groupStr}3D Medusa Rule 3 {(ax, ay, aVal, aColor)} {(bx, by, bVal, bColor)}\n"
    #                 for val in self.getSet((ax, ay)):
    #                     if val == aVal or val == bVal: continue
    #                     eCells[val] = set()
    #                     eCells[val].add((ax, ay))
    #                 for val, cells in eCells.items():
    #                     note += f"Removing {val} from {cells}\n"
    #                     baseCopy.updateNotesDX(cells, {val})
    #                 if not any(baseCopy.stuck(newPuzzle) for newPuzzle in newPuzzles):
    #                     baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "3D Medusa Rule 3", current_node, puzFlipGroup)
    #                     newPuzzles.append(tempPuzzle)
    #             # Rule 4 set creator
    #             if aVal == bVal and aColor != bColor:
    #                 green_cell = (ax, ay) if aColor == 'green' else (bx, by)
    #                 yellow_cell = (ax, ay) if aColor == 'yellow' else (bx, by)
    #                 candidates = connections.get((green_cell[0], green_cell[1], aVal), set()) & \
    #                              connections.get((yellow_cell[0], yellow_cell[1], aVal), set())
    #                 for cell in candidates:
    #                     if (cell[0], cell[1], aVal, 'green') not in normalized_set and \
    #                        (cell[0], cell[1], aVal, 'yellow') not in normalized_set:
    #                         eCells4.setdefault(aVal, set()).add(cell)
    #             # Rule 5 set creator            
    #             if (ax, ay) == (bx, by) or aColor == bColor or aVal == bVal or not self.hasConnection([(ax, ay), (bx, by)]): continue
    #             if bVal in self.getSet((ax, ay)):
    #                 if bVal not in eCells5:
    #                     eCells5[bVal] = set()
    #                 eCells5[bVal].add((ax, ay))
    #             if aVal in self.getSet((bx, by)):
    #                 if aVal not in eCells5:
    #                     eCells5[aVal] = set()
    #                 eCells5[aVal].add((bx, by))
    #         # Rule 6
    #         if eCells4:
    #             note = f"{groupStr}3D Medusa Rule 4\n"
    #             for val, cells in eCells4.items():
    #                 baseCopy.updateNotesDX(cells, {val})
    #                 note += f"Removing {val} from {cells}\n"
    #             if not any(baseCopy.stuck(newPuzzle) for newPuzzle in newPuzzles):
    #                 baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "3D Medusa Rule 4", current_node, puzFlipGroup)
    #                 newPuzzles.append(tempPuzzle)
    #         eCells4 = {}
    #         if eCells5:
    #             note = f"{groupStr}3D Medusa Rule 5\n"
    #             for val, cells in eCells5.items():
    #                 baseCopy.updateNotesDX(cells, {val})
    #                 note += f"Removing {val} from {cells}\n"
    #             if not any(baseCopy.stuck(newPuzzle) for newPuzzle in newPuzzles):
    #                 baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "3D Medusa Rule 5", current_node, puzFlipGroup)
    #                 newPuzzles.append(tempPuzzle)
    #         eCells5 = {}
    #         normalized_cells = {(x, y) for x, y, v, c in normalized}
    #         for i in range(9):
    #             for j in range(9):
    #                 if self.locked[i][j] or (i, j) in normalized_cells: continue
    #                 tempSet = self.getSet((i, j))
    #                 if not tempSet: continue
    #                 goal = {color: {v: set() for v in tempSet} for color in {'yellow', 'green'}}
    #                 for x, y, v, color in normalized:
    #                     if v in tempSet and (x, y) in connections.get((i, j, v), set()):
    #                         goal[color][v].add((x, y))
    #                 for color, vals in goal.items():
    #                     if any(not coords for coords in vals.values()): continue
    #                     note = f"{groupStr}3D Medusa Rule 6 removing all {color} nodes\n"
    #                     for x, y, v, eColor in normalized:
    #                         if eColor != color: continue
    #                         eCells.setdefault(v, set()).add((x, y))
    #                     for v, cells in eCells.items():
    #                         self.updateNotesDX(cells, {v})
    #                         note += f"Removing {v} from {cells}.\n"
    #                     if not any(baseCopy.stuck(newPuzzle) for newPuzzle in newPuzzles):
    #                         baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "3D Medusa Rule 6", current_node, puzFlipGroup)
    #                         newPuzzles.append(tempPuzzle)
    #     return baseCopy, newPuzzles
        
    def getMedusaLinks(self, remaining):
        links = {}    
        def add_link(a, b):
            links.setdefault(a, set()).add(b)
            links.setdefault(b, set()).add(a)
        for val in remaining:
            sources = []
            for row in range(9):
                sources.append((self.getAnyRowIdxs((row, 0), {val}), val))
            for col in range(9):
                sources.append((self.getAnyColIdxs((0, col), {val}), val))
            for rBox in range(0, 9, 3):
                for cBox in range(0, 9, 3):
                    sources.append((self.getAnyBoxIdxs((rBox, cBox), {val}), val))
            for idxs, v in sources:
                if len(idxs) == 2:
                    (r1, c1), (r2, c2) = tuple(idxs)
                    add_link((r1, c1, v), (r2, c2, v))
        for i in range(9):
            for j in range(9):
                cellSet = self.getSet((i, j))
                if len(cellSet) == 2:
                    v1, v2 = tuple(cellSet)
                    add_link((i, j, v1), (i, j, v2))
        return links

    def getMedusaNeighbors(self, currentNode, visited, medusaLinks):
        i, j, val, color = currentNode
        newColor = 'yellow' if color == 'green' else 'green'
        result = []
        for ni, nj, nval in medusaLinks.get((i, j, val), set()):
            candidate = (ni, nj, nval, newColor)
            if candidate not in visited:
                result.append(candidate)
        return result
        
    # ********************************************************************************************************************
    def jellyfish(self, baseCopy, current_node):
        newPuzzles = []
        for val in self.getRemaining():
            rowSet = {r: {c for c in range(9) if val in self.layout[r][c].note} for r in range(9) if any(val in self.layout[r][c].note for c in range(9))}
            rowKeys = [r for r in rowSet if 2 <= len(rowSet[r]) <= 4]
            for rowCombo in itertools.combinations(rowKeys, 4):
                r1, r2, r3, r4 = rowCombo
                cols = rowSet[r1] | rowSet[r2] | rowSet[r3] | rowSet[r4]
                if len(cols) == 4:
                    tempRowSet = set(rowCombo)
                    tempColSet = cols
                    eNodes = set()
                    for c in tempColSet:
                        ignoreNodes = {(r, c) for r in tempRowSet}
                        eNodes |= {(val, (r, c)) for r in range(9) if val in self.layout[r][c].note and (r, c) not in ignoreNodes}
                    if not eNodes: continue
                    group = (frozenset(tempRowSet), frozenset(tempColSet))
                    note = f"Jellyfish on value {val}: rows {sorted(tempRowSet)}, columns {sorted(tempColSet)}"
                    if not uberPrune(current_node, ("Jellyfish Row", group, eNodes, None)):
                        baseCopy.updateNotesGX(eNodes)
                        if self.stuck(baseCopy): continue
                        diffNodes = self.puzzleDifference(baseCopy)
                        note += f" removed {val} from {diffNodes}"
                        baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Jellyfish Row", current_node, group)
                        newPuzzles.append(tempPuzzle)
            colSet = {c: {r for r in range(9) if val in self.layout[r][c].note} for c in range(9) if any(val in self.layout[r][c].note for r in range(9))}
            colKeys = [c for c in colSet if 2 <= len(colSet[c]) <= 4]
            for colCombo in itertools.combinations(colKeys, 4):
                c1, c2, c3, c4 = colCombo
                rows = colSet[c1] | colSet[c2] | colSet[c3] | colSet[c4]
                if len(rows) == 4:
                    tempColSet = set(colCombo)
                    tempRowSet = rows
                    eNodes = set()
                    for r in tempRowSet:
                        ignoreNodes = {(r, c) for c in tempColSet}
                        eNodes |= {(val, (r, c)) for c in range(9) if val in self.layout[r][c].note and (r, c) not in ignoreNodes}
                    if not eNodes: continue
                    group = (frozenset(tempRowSet), frozenset(tempColSet))
                    note = f"Jellyfish on value {val}: columns {sorted(tempColSet)}, rows {sorted(tempRowSet)}"
                    if not uberPrune(current_node, ("Jellyfish Col", group, eNodes, None)):
                        baseCopy.updateNotesGX(eNodes)
                        if self.stuck(baseCopy): continue
                        diffNodes = self.puzzleDifference(baseCopy)
                        note += f" removed {val} from {diffNodes}"
                        baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Jellyfish Col", current_node, group)
                        newPuzzles.append(tempPuzzle)
        return baseCopy, newPuzzles
    # def jellyfish(self, baseCopy, current_node):
    #     newPuzzles = []
    #     for val in self.getRemaining():
    #         rowSet = {r: {c for c in range(9) if val in self.layout[r][c].note} for r in range(9) if any(val in self.layout[r][c].note for c in range(9))}
    #         rowKeys = [r for r in rowSet if 2 <= len(rowSet[r]) <= 4]
    #         for rowCombo in itertools.combinations(rowKeys, 4):
    #             r1, r2, r3, r4 = rowCombo
    #             cols = rowSet[r1] | rowSet[r2] | rowSet[r3] | rowSet[r4]
    #             if len(cols) == 4:
    #                 tempRowSet = set(rowCombo)
    #                 tempColSet = cols
    #                 for c in tempColSet:
    #                     ignoreNodes = [(r, c) for r in tempRowSet]
    #                     baseCopy.subUpdateNotes('col', ignoreNodes, {val})
    #                 if self.stuck(baseCopy): continue
    #                 note = f"Jellyfish on value {val}: rows {sorted(tempRowSet)}, columns {sorted(tempColSet)}"
    #                 baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Jellyfish Row", current_node)
    #                 if not any(baseCopy.stuck(newPuzzle) for newPuzzle in newPuzzles):
    #                     newPuzzles.append(tempPuzzle)
    #         colSet = {c: {r for r in range(9) if val in self.layout[r][c].note} for c in range(9) if any(val in self.layout[r][c].note for r in range(9))}
    #         colKeys = [c for c in colSet if 2 <= len(colSet[c]) <= 4]
    #         for colCombo in itertools.combinations(colKeys, 4):
    #             c1, c2, c3, c4 = colCombo
    #             rows = colSet[c1] | colSet[c2] | colSet[c3] | colSet[c4]
    #             if len(rows) == 4:
    #                 tempColSet = set(colCombo)
    #                 tempRowSet = rows
    #                 for r in tempRowSet:
    #                     ignoreNodes = [(r, c) for c in tempColSet]
    #                     baseCopy.subUpdateNotes('row', ignoreNodes, {val})
    #                 if not self.stuck(baseCopy): continue
    #                 note = f"Jellyfish on value {val}: columns {sorted(tempColSet)}, rows {sorted(tempRowSet)}"
    #                 baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Jellyfish Col", current_node)
    #                 if not any(baseCopy.stuck(newPuzzle) for newPuzzle in newPuzzles):
    #                     newPuzzles.append(tempPuzzle)
    #     return baseCopy, newPuzzles
    # ********************************************************************************************************************

    def uniqueRectangles(self, baseCopy, current_node):
        newPuzzles = []
        
        def getSet(r, c):
            return self.getSet((r, c))
        
        def processOrientation(flip):
            # flip=False: normal (rows as floor), flip=True: transposed (cols as floor)
            nonlocal baseCopy
            def coord(a, b):
                return (b, a) if flip else (a, b)
            def getAnyLineIdxs(node, valSet):
                if flip: return self.getAnyColIdxs(node, valSet)
                else: return self.getAnyRowIdxs(node, valSet)
            def getAnyOrthoIdxs(node, valSet):
                if flip: return self.getAnyRowIdxs(node, valSet)
                else: return self.getAnyColIdxs(node, valSet)
            def getLineCells(node):
                if flip: return self.getAllColCoords(node)
                else: return self.getAllRowCoords(node)
            def singleLineCheck(nodes, valSet):
                if flip: return self.singleColCheck(nodes, valSet)
                else: return self.singleRowCheck(nodes, valSet)
            def getExLineIdxs(node, valSet):
                if flip: return self.getExColIdxs(node, valSet)
                else: return self.getExRowIdxs(node, valSet)
            def typeof():
                return 'col' if flip else 'row'
            
            results = []
            
            # build floor sets — pairs of cells on the same line with exactly comboSet as their candidates
            for combo in itertools.combinations(self.getRemaining(), 2):
                comboSet = set(combo)
                for primary in range(9):
                    matchingSecondary = [s for s in range(9) 
                                         if self.getSet(coord(primary, s)) == comboSet]
                    if len(matchingSecondary) != 2: continue
                    s1, s2 = matchingSecondary[0], matchingSecondary[1]
                    n1, n2 = coord(primary, s1), coord(primary, s2)
                    if self.locked[n1[0]][n1[1]] or self.locked[n2[0]][n2[1]]: continue
                    
                    for tempPrimary in range(9):
                        if primary == tempPrimary: continue
                        n3, n4 = coord(tempPrimary, s1), coord(tempPrimary, s2)
                        if self.locked[n3[0]][n3[1]] or self.locked[n4[0]][n4[1]]: continue
                        n3Set, n4Set = self.getSet(n3), self.getSet(n4)
                        if not (comboSet <= (n3Set & n4Set)): continue
                        group = [n1, n2, n3, n4]
                        floorInBox = self.inBox([n1, n2])
                        ceilInBoxWithFloor = self.inBox([n1, n3])
                        suffix = "Col" if flip else "Row"
    
                        # Type 1
                        if floorInBox:
                            if (n3Set == comboSet) != (n4Set == comboSet):
                                evilNode = n4 if n3Set == comboSet else n3
                                eNodes = {(v, evilNode) for v in comboSet if v in self.layout[evilNode[0]][evilNode[1]].note}
                                if eNodes and not uberPrune(current_node, (f"Unique Rectangles {suffix} 1", group, eNodes, None)):
                                    baseCopy.updateNotesGX(eNodes)
                                    diffNodes = self.puzzleDifference(baseCopy)
                                    note = f"Unique Rectangles {suffix} Type 1 floor {n1} & {n2} vals {combo}\nRemoving {combo} from {diffNodes}"
                                    baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, f"Unique Rectangles {suffix} 1", current_node, group)
                                    results.append(tempPuzzle)
    
                        # Types 2A, 3B, 3/3B, 4A — floor in box, ceil NOT in box with floor
                        if floorInBox and not ceilInBoxWithFloor:
                            # Type 2A
                            
                            if len(n3Set | n4Set) == 3 and n3Set == n4Set:
                                eVal = (n3Set - comboSet).pop()
                                eNodes = {(eVal, (r, c)) for r, c in
                                          [(r, c) for r, c in self.getAllBoxCoords(n3) if (r, c) not in [n3, n4]] +
                                          [(r, c) for r, c in getLineCells(n3) if (r, c) not in [n3, n4]]
                                          if eVal in self.layout[r][c].note}
                                if eNodes and not uberPrune(current_node, (f"Unique Rectangles {suffix} 2A", group, eNodes, None)):
                                    baseCopy.updateNotesGX(eNodes)
                                    diffNodes = self.puzzleDifference(baseCopy)
                                    note = f"Unique Rectangles {suffix} Type 2A floor {n1} & {n2} vals {combo}, found {n3Set} at {n3}&{n4}\nRemoving {eVal} from {diffNodes}"
                                    baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, f"Unique Rectangles {suffix} 2A", current_node, group)
                                    results.append(tempPuzzle)
                                
                            if len(n3Set | n4Set) > 3 and n3Set != n4Set:
                                # Type 2D
                                if len(n3Set | n4Set) > 3:
                                    targetSet = (n3Set | n4Set) - comboSet
                                    eNodes = set()
                                    targetNodes = getExLineIdxs(n3, targetSet)
                                    if targetNodes:
                                        targetNode = targetNodes.pop()
                                        unionSet = n3Set | n4Set
                                        for r, c in getLineCells(n3):
                                            if (r, c) in [n3, n4, targetNode]: continue
                                            if unionSet <= self.getSet((r, c)):
                                                eNodes |= {(v, (r, c)) for v in targetSet if v in self.layout[r][c].note}
                                    targetNodes = self.getExBoxIdxs(n3, targetSet)
                                    if targetNodes:
                                        targetNode = targetNodes.pop()
                                        unionSet = n3Set | n4Set
                                        for r, c in self.getAllBoxCoords(n3):
                                            if (r, c) in [n3, n4, targetNode]: continue
                                            if unionSet <= self.getSet((r, c)):
                                                eNodes |= {(v, (r, c)) for v in targetSet if v in self.layout[r][c].note}
                                    if eNodes and not uberPrune(current_node, (f"Unique Rectangles {suffix} 2D", group, eNodes, None)):
                                        baseCopy.updateNotesGX(eNodes)
                                        diffNodes = self.puzzleDifference(baseCopy)
                                        note = f"Unique Rectangles {suffix} Type 2D floor {n1}&{n2} vals {combo}, found {n3Set} at {n3} and {n4Set} at {n4}\nErasing {diffNodes}"
                                        baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, f"Unique Rectangles {suffix} 2D", current_node, group)
                                        results.append(tempPuzzle)
              
                                # Type 3B
                                if len(n3Set) == len(n4Set) == 3:
                                    targetSet = (n3Set | n4Set) - comboSet
                                    eNodes = set()
                                    # for getEx in [getExLineIdxs, self.getExBoxIdxs]:
                                    #     targetNodes = getEx(n3, targetSet)
                                    #     if targetNodes:
                                    #         targetNode = targetNodes.pop()
                                    #         eNodes |= {(v, (r, c)) for v in targetSet for r, c in [targetNode, n3, n4] if v in self.layout[r][c].note}
                                    # ----------------------------------------------------
                                    targetNodes = getExLineIdxs(n3, targetSet)
                                    if targetNodes:
                                        targetNode = targetNodes.pop()
                                        eNodes |= {(v, (r, c)) for v in targetSet
                                                   for r, c in getLineCells(n3)
                                                   if (r, c) not in [n3, n4, targetNode]
                                                   and v in self.layout[r][c].note}
                                    targetNodes = self.getExBoxIdxs(n3, targetSet)
                                    if targetNodes:
                                        targetNode = targetNodes.pop()
                                        eNodes |= {(v, (r, c)) for v in targetSet
                                                   for r, c in self.getAllBoxCoords(n3)
                                                   if (r, c) not in [n3, n4, targetNode]
                                                   and v in self.layout[r][c].note}
                                    if eNodes and not uberPrune(current_node, (f"Unique Rectangles {suffix} 3B", group, eNodes, None)):
                                        baseCopy.updateNotesGX(eNodes)
                                        diffNodes = self.puzzleDifference(baseCopy)
                                        note = f"Unique Rectangles {suffix} Type 3B floor {n1}&{n2} vals {combo}, found {n3Set} at {n3} and {n4Set} at {n4}\nErasing {diffNodes}"
                                        baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, f"Unique Rectangles {suffix} 3B", current_node, group)
                                        results.append(tempPuzzle)
    
                                # Type 3/3B Pseudo
                                # if (len(n3Set) == 3 and len(n4Set) == 4) or (len(n3Set) == 4 and len(n4Set) == 3):
                                #     x, y, z = self.findPseudoLoop(typeof(), comboSet, [n3, n4])
                                #     if x:
                                #         eNodes = {(v, (r, c)) for v in z for r, c in y if v in self.layout[r][c].note}
                                #         if eNodes and not uberPrune(current_node, (f"Unique Rectangles {suffix} 3/3B", group, eNodes, None)):
                                #             baseCopy.updateNotesGX(eNodes)
                                #             diffNodes = self.puzzleDifference(baseCopy)
                                #             note = f"Unique Rectangles {suffix} Type 3/3B floor {n1}&{n2} vals {combo}, ceiling {n3}&{n4}\nErasing {diffNodes}"
                                #             baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, f"Unique Rectangles {suffix} 3/3B", current_node, group)
                                #             results.append(tempPuzzle)
                                # Type 3/3B Pseudo
                                # if (len(n3Set) == 3 and len(n4Set) == 4) or (len(n3Set) == 4 and len(n4Set) == 3):
                            if 4 <= len(n3Set | n4Set) <= 5:
                                found, excludeNodes, targetSet = self.findPseudoLoop(flip, comboSet, [n3, n4])
                                if found:
                                    boxCells = self.getAllBoxCoords(n3)
                                    excludeSet = set(map(tuple, excludeNodes))
                                    eNodes = {
                                        (v, (r, c)) for v in targetSet
                                        for r, c in boxCells
                                        if (r, c) not in excludeSet
                                        and not self.locked[r][c]
                                        and v in self.layout[r][c].note
                                        and v not in comboSet
                                    }
                                    if eNodes and not uberPrune(current_node, (f"Unique Rectangles {suffix} 3/3B", group, eNodes, None)):
                                        baseCopy.updateNotesGX(eNodes)
                                        diffNodes = self.puzzleDifference(baseCopy)
                                        note = f"Unique Rectangles {suffix} Type 3/3B floor {n1}&{n2} vals {combo}, ceiling {n3}&{n4}, pseudo loop {[n for n in excludeNodes if n not in [n3, n4]]}\nErasing {diffNodes}"
                                        baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, f"Unique Rectangles {suffix} 3/3B", current_node, group)
                                        results.append(tempPuzzle)
    
                            # Type 4A
                            if singleLineCheck([n3, n4], {combo[0]}) ^ singleLineCheck([n3, n4], {combo[1]}):
                                critVal = combo[0] if singleLineCheck([n3, n4], {combo[0]}) else combo[1]
                                eVal = (comboSet - {critVal}).pop()
                                eNodes = {(eVal, (r, c)) for r, c in [n3, n4] if eVal in self.layout[r][c].note}
                                if eNodes and not uberPrune(current_node, (f"Unique Rectangles {suffix} 4A", group, eNodes, None)):
                                    baseCopy.updateNotesGX(eNodes)
                                    diffNodes = self.puzzleDifference(baseCopy)
                                    note = f"Unique Rectangles {suffix} Type 4A floor {n1}&{n2} vals {combo}, {critVal} exclusive to line\nRemoving {eVal} from {diffNodes}"
                                    baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, f"Unique Rectangles {suffix} 4A", current_node, group)
                                    results.append(tempPuzzle)
    
                        # Types 2B, 3A, 4B — floor NOT in box, ceil in box with floor
                        if not floorInBox and ceilInBoxWithFloor:
                            # Type 2B
                            if len(n3Set | n4Set) == 3 and n3Set == n4Set:
                                eVal = (n3Set - comboSet).pop()
                                eNodes = {(eVal, (r, c)) for r, c in getLineCells(n3) if (r, c) not in [n3, n4] and eVal in self.layout[r][c].note}
                                if eNodes and not uberPrune(current_node, (f"Unique Rectangles {suffix} 2B", group, eNodes, None)):
                                    baseCopy.updateNotesGX(eNodes)
                                    diffNodes = self.puzzleDifference(baseCopy)
                                    note = f"Unique Rectangles {suffix} Type 2B floor {n1}&{n2} vals {combo}, found {n3Set} at {n3}&{n4}\nRemoving {eVal} from {diffNodes}"
                                    baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, f"Unique Rectangles {suffix} 2B", current_node, group)
                                    results.append(tempPuzzle)
                            # Type 3A
                            if len(n3Set | n4Set) == 4 and n3Set != n4Set and len(n3Set) == len(n4Set) == 3 and comboSet == (n3Set & n4Set):
                                targetSet = (n3Set | n4Set) - comboSet
                                targetNodes = getExLineIdxs(n3, targetSet)
                                eNodes = set()
                                if targetNodes:
                                    targetNode = targetNodes.pop()
                                    eNodes = {(eVal, (r, c)) for r, c in getLineCells(n3) if (r, c) not in [n3, n4, targetNode] for eVal in targetSet if eVal in self.layout[r][c].note}
                                if eNodes and not uberPrune(current_node, (f"Unique Rectangles {suffix} 3A", group, eNodes, None)):
                                    baseCopy.updateNotesGX(eNodes)
                                    diffNodes = self.puzzleDifference(baseCopy)
                                    note = f"Unique Rectangles {suffix} Type 3A floor {n1}&{n2} vals {combo}, found {n3Set} at {n3} and {n4Set} at {n4}\nErasing {diffNodes}"
                                    baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, f"Unique Rectangles {suffix} 3A", current_node, group)
                                    results.append(tempPuzzle)
                            # Type 4B
                            if singleLineCheck([n3, n4], {combo[0]}) ^ singleLineCheck([n3, n4], {combo[1]}):
                                critVal = combo[0] if singleLineCheck([n3, n4], {combo[0]}) else combo[1]
                                eVal = (comboSet - {critVal}).pop()
                                eNodes = {(eVal, (r, c)) for r, c in [n3, n4] if eVal in self.layout[r][c].note}
                                if eNodes and not uberPrune(current_node, (f"Unique Rectangles {suffix} 4B", group, eNodes, None)):
                                    baseCopy.updateNotesGX(eNodes)
                                    diffNodes = self.puzzleDifference(baseCopy)
                                    note = f"Unique Rectangles {suffix} Type 4B floor {n1}&{n2} vals {combo}, {critVal} exclusive to line\nRemoving {eVal} from {diffNodes}"
                                    baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, f"Unique Rectangles {suffix} 4B", current_node, group)
                                    results.append(tempPuzzle)
    
            return results
    
        newPuzzles.extend(processOrientation(False))  # Row orientation
        newPuzzles.extend(processOrientation(True))   # Col orientation
    
        # Type 2C and Type 5 (diagonal — same for both orientations, run once)
        rowRPSets, colRPSets = set(), set()
        for combo in itertools.combinations(self.getRemaining(), 2):
            comboSet = set(combo)
            rowRP = sorted(self.getRowChuteRemotePairs(comboSet))
            colRP = sorted(self.getColChuteRemotePairs(comboSet))
            for n1, n2 in rowRP: rowRPSets.add((combo, n1, n2))
            for n1, n2 in colRP: colRPSets.add((combo, n1, n2))
    
        for combo, n1, n2 in colRPSets | rowRPSets:
            comboSet = set(combo)
            x1, y1 = n1
            x2, y2 = n2
            n3, n4 = (x1, y2), (x2, y1)
            group = [n1, n2, n3, n4]
            n3Set, n4Set = self.getSet(n3), self.getSet(n4)
            if not (comboSet <= (n3Set & n4Set)): continue
    
            if n3Set == n4Set and len(n3Set) == 3:
                eVal = (n3Set - comboSet).pop()
                eNodes = set()
                if self.sameColChute([n1, n2]):
                    for base, col in [(x1, y1), (x2, y2)]:
                        offset = self.getOffset(base)
                        for row in range(offset, offset + 3):
                            if row == base: continue
                            if eVal in self.layout[row][col].note: eNodes.add((eVal, (row, col)))
                if self.sameRowChute([n1, n2]):
                    for base, row in [(y1, x1), (y2, x2)]:
                        offset = self.getOffset(base)
                        for col in range(offset, offset + 3):
                            if col == base: continue
                            if eVal in self.layout[row][col].note: eNodes.add((eVal, (row, col)))
                if eNodes and not uberPrune(current_node, ("Unique Rectangles 2C", group, eNodes, None)):
                    baseCopy.updateNotesGX(eNodes)
                    diffNodes = self.puzzleDifference(baseCopy)
                    note = f"Unique Rectangles Type 2C found {comboSet} in {n1} and {n2}, erasing {diffNodes}"
                    baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Unique Rectangles 2C", current_node, group)
                    newPuzzles.append(tempPuzzle)
    
            r5Vals = {(node, val): [0, 0] for node in [n1, n2] for val in combo}
            for val in combo:
                for base in [n1, n2]:
                    for check in [n3, n4]:
                        if not self.singleRowCheck([base, check], {val}): r5Vals[(base, val)][0] += 1
                        if not self.singleColCheck([base, check], {val}): r5Vals[(base, val)][0] += 1
                        if self.singleBoxCheck([base, check], {val}): r5Vals[(base, val)][1] += 1
    
            eNodes = set()
            for (node, critVal), countArry in r5Vals.items():
                if countArry[0] == 2 and countArry[1] == 1:
                    eVal = (comboSet - {critVal}).pop()
                    if eVal in self.layout[node[0]][node[1]].note:
                        eNodes.add((eVal, node))
            if eNodes and not uberPrune(current_node, ("Unique Rectangles 5", group, eNodes, None)):
                baseCopy.updateNotesGX(eNodes)
                diffNodes = self.puzzleDifference(baseCopy)
                note = f"Unique Rectangles Type 5 found {comboSet} in {n1}&{n2}\nRemoving {diffNodes}"
                baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Unique Rectangles 5", current_node, group)
                newPuzzles.append(tempPuzzle)
    
        return baseCopy, newPuzzles
    # def uniqueRectangles(self, baseCopy, current_node):
    #     newPuzzles = []
    #     rowSets, colSets, rowRPSets, colRPSets = set(), set(), set(), set()
    #     for combo in itertools.combinations(self.getRemaining(), 2):
    #         comboSet = set(combo)
    #         for row in range(9):
    #             matchingCols = [c for c in range(9) if self.getSet((row, c)) == comboSet]
    #             if len(matchingCols) == 2: rowSets.add((combo, row, matchingCols[0], matchingCols[1]))
    #         for col in range(9):
    #             matchingRows = [r for r in range(9) if self.getSet((r, col)) == comboSet]
    #             if len(matchingRows) == 2: colSets.add((combo, col, matchingRows[0], matchingRows[1]))
    #         rowRP = sorted(self.getRowChuteRemotePairs(comboSet))
    #         colRP = sorted(self.getColChuteRemotePairs(comboSet))
    #         for n1, n2 in rowRP: rowRPSets.add((combo, n1, n2))
    #         for n1, n2 in colRP: colRPSets.add((combo, n1, n2))

    #     for combo, row, col1, col2 in rowSets:
    #         comboSet = set(combo)
    #         n1, n2 = (row, col1), (row, col2)
    #         for tempRow in range(9):
    #             if row == tempRow or self.locked[tempRow][col1] or self.locked[tempRow][col2]: continue
    #             n3, n4 = (tempRow, col1), (tempRow, col2)
    #             n3Set, n4Set = self.getSet(n3), self.getSet(n4)
    #             if not (comboSet <= (n3Set & n4Set)): continue
    #             group = [n1, n2, n3, n4]

    #             # Type 1
    #             if self.inBox([n1, n2]):
    #                 if n3Set == comboSet and n4Set != comboSet:
    #                     eNodes = {(v, n4) for v in comboSet if v in self.layout[n4[0]][n4[1]].note}
    #                     if eNodes and not uberPrune(current_node, ("Unique Rectangles Row 1", group, eNodes, None)):
    #                         baseCopy.updateNotesGX(eNodes)
    #                         diffNodes = self.puzzleDifference(baseCopy)
    #                         note = f"Unique Rectangles Row Type 1 with floor {n1} & {n2} and vals {combo}, found vals {combo} at {n3}\nRemoving {combo} from {diffNodes}"
    #                         baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Unique Rectangles Row 1", current_node, group)
    #                         newPuzzles.append(tempPuzzle)
    #                 elif n4Set == comboSet and n3Set != comboSet:
    #                     eNodes = {(v, n3) for v in comboSet if v in self.layout[n3[0]][n3[1]].note}
    #                     if eNodes and not uberPrune(current_node, ("Unique Rectangles Row 1", group, eNodes, None)):
    #                         baseCopy.updateNotesGX(eNodes)
    #                         diffNodes = self.puzzleDifference(baseCopy)
    #                         note = f"Unique Rectangles Row Type 1 with floor {n1} & {n2} and vals {combo}, found vals {combo} at {n4}\nRemoving {combo} from {diffNodes}"
    #                         baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Unique Rectangles Row 1", current_node, group)
    #                         newPuzzles.append(tempPuzzle)

    #             if self.inBox([n1, n2]) and not self.inBox([n1, n3]):
    #                 # Type 2A
    #                 if len(n3Set | n4Set) == 3 and n3Set == n4Set:
    #                     eVal = (n3Set - comboSet).pop()
    #                     eNodes = {(eVal, (r, c)) for r, c in
    #                               [(r, c) for r, c in self.getBoxCells(n3) if (r, c) not in [n3, n4]] +
    #                               [(r, c) for r, c in self.getRowCells(n3) if (r, c) not in [n3, n4]]
    #                               if eVal in self.layout[r][c].note}
    #                     if eNodes and not uberPrune(current_node, ("Unique Rectangles Row 2A", group, eNodes, None)):
    #                         baseCopy.updateNotesGX(eNodes)
    #                         diffNodes = self.puzzleDifference(baseCopy)
    #                         note = f"Unique Rectangles Row Type 2A with floor {n1} & {n2} and vals {combo}, found vals {n3Set} at {n3} & {n4}\nRemoving {eVal} from {diffNodes}"
    #                         baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Unique Rectangles Row 2A", current_node, group)
    #                         newPuzzles.append(tempPuzzle)

    #                 if len(n3Set | n4Set) >= 3 and n3Set != n4Set:
    #                     # Type 3B
    #                     if len(n3Set) == len(n4Set) == 3:
    #                         targetSet = (n3Set | n4Set) - comboSet
    #                         eNodes = set()
    #                         targetNodes = self.getExRowIdxs((tempRow, col1), targetSet)
    #                         if targetNodes:
    #                             targetNode = targetNodes.pop()
    #                             eNodes |= {(v, (r, c)) for v in targetSet for r, c in [targetNode, n3, n4] if v in self.layout[r][c].note}
    #                         targetNodes = self.getExBoxIdxs((tempRow, col1), targetSet)
    #                         if targetNodes:
    #                             targetNode = targetNodes.pop()
    #                             eNodes |= {(v, (r, c)) for v in targetSet for r, c in [targetNode, n3, n4] if v in self.layout[r][c].note}
    #                         if eNodes and not uberPrune(current_node, ("Unique Rectangles Row 3B", group, eNodes, None)):
    #                             baseCopy.updateNotesGX(eNodes)
    #                             diffNodes = self.puzzleDifference(baseCopy)
    #                             note = f"Unique Rectangles Row Type 3B with floor {n1} & {n2} and vals {combo}, found {n3Set} at {n3} and {n4Set} at {n4}\nErasing {diffNodes}"
    #                             baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Unique Rectangles Row 3B", current_node, group)
    #                             newPuzzles.append(tempPuzzle)

    #                     # Type 3/3B Pseudo
    #                     if (len(n3Set) == 3 and len(n4Set) == 4) or (len(n3Set) == 4 and len(n4Set) == 3):
    #                         x, y, z = self.findPseudoLoop('row', comboSet, [n3, n4])
    #                         if x:
    #                             eNodes = {(v, (r, c)) for v in z for r, c in y if v in self.layout[r][c].note}
    #                             if eNodes and not uberPrune(current_node, ("Unique Rectangles Row 3/3B", group, eNodes, None)):
    #                                 baseCopy.updateNotesGX(eNodes)
    #                                 diffNodes = self.puzzleDifference(baseCopy)
    #                                 note = f"Unique Rectangles Row Type 3/3B pseudo with floor {n1} & {n2} and vals {combo}, found ceiling {n3} & {n4}\nErasing {diffNodes}"
    #                                 baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Unique Rectangles Row 3/3B", current_node, group)
    #                                 newPuzzles.append(tempPuzzle)

    #                     # Type 4A
    #                     if self.singleRowCheck([n3, n4], {combo[0]}) ^ self.singleRowCheck([n3, n4], {combo[1]}):
    #                         if self.singleRowCheck([n3, n4], {combo[0]}): critVal, eVal = combo[0], combo[1]
    #                         else: critVal, eVal = combo[1], combo[0]
    #                         eNodes = {(eVal, (r, c)) for r, c in [n3, n4] if eVal in self.layout[r][c].note}
    #                         if eNodes and not uberPrune(current_node, ("Unique Rectangles Row 4A", group, eNodes, None)):
    #                             baseCopy.updateNotesGX(eNodes)
    #                             diffNodes = self.puzzleDifference(baseCopy)
    #                             note = f"Unique Rectangles Row Type 4A with floor {n1} & {n2} and vals {combo}, found {critVal} exclusive to row\nRemoving {eVal} from {diffNodes}"
    #                             baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Unique Rectangles Row 4A", current_node, group)
    #                             newPuzzles.append(tempPuzzle)

    #             if not self.inBox([n1, n2]) and self.inBox([n1, n3]):
    #                 # Type 2B
    #                 if len(n3Set | n4Set) == 3 and n3Set == n4Set:
    #                     eVal = (n3Set - comboSet).pop()
    #                     eNodes = {(eVal, (r, c)) for r, c in self.getRowCells(n3) if (r, c) not in [n3, n4] and eVal in self.layout[r][c].note}
    #                     if eNodes and not uberPrune(current_node, ("Unique Rectangles Row 2B", group, eNodes, None)):
    #                         baseCopy.updateNotesGX(eNodes)
    #                         diffNodes = self.puzzleDifference(baseCopy)
    #                         note = f"Unique Rectangles Row Type 2B with floor {n1} & {n2} and vals {combo}, found vals {n3Set} at {n3} & {n4}\nRemoving {eVal} from {diffNodes}"
    #                         baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Unique Rectangles Row 2B", current_node, group)
    #                         newPuzzles.append(tempPuzzle)

    #                 # Type 3A
    #                 if len(n3Set | n4Set) == 4 and n3Set != n4Set and len(n3Set) == len(n4Set) == 3:
    #                     targetSet = (n3Set | n4Set) - comboSet
    #                     eNodes = set()
    #                     targetNodes = self.getExRowIdxs((tempRow, col1), targetSet)
    #                     if targetNodes:
    #                         targetNode = targetNodes.pop()
    #                         eNodes |= {(v, (r, c)) for v in targetSet for r, c in [targetNode, n3, n4] if v in self.layout[r][c].note}
    #                     if eNodes and not uberPrune(current_node, ("Unique Rectangles Row 3A", group, eNodes, None)):
    #                         baseCopy.updateNotesGX(eNodes)
    #                         diffNodes = self.puzzleDifference(baseCopy)
    #                         note = f"Unique Rectangles Row Type 3A with floor {n1} & {n2} and vals {combo}, found {n3Set} at {n3} and {n4Set} at {n4}\nErasing {diffNodes}"
    #                         baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Unique Rectangles Row 3A", current_node, group)
    #                         newPuzzles.append(tempPuzzle)

    #                 # Type 4B
    #                 if self.singleRowCheck([n3, n4], {combo[0]}) ^ self.singleRowCheck([n3, n4], {combo[1]}):
    #                     if self.singleRowCheck([n3, n4], {combo[0]}): critVal, eVal = combo[0], combo[1]
    #                     else: critVal, eVal = combo[1], combo[0]
    #                     eNodes = {(eVal, (r, c)) for r, c in [n3, n4] if eVal in self.layout[r][c].note}
    #                     if eNodes and not uberPrune(current_node, ("Unique Rectangles Row 4B", group, eNodes, None)):
    #                         baseCopy.updateNotesGX(eNodes)
    #                         diffNodes = self.puzzleDifference(baseCopy)
    #                         note = f"Unique Rectangles Row Type 4B with floor {n1} & {n2} and vals {combo}, found {critVal} exclusive to row\nRemoving {eVal} from {diffNodes}"
    #                         baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Unique Rectangles Row 4B", current_node, group)
    #                         newPuzzles.append(tempPuzzle)

    #     for combo, col, row1, row2 in colSets:
    #         comboSet = set(combo)
    #         n1, n2 = (row1, col), (row2, col)
    #         for tempCol in range(9):
    #             if col == tempCol or self.locked[row1][tempCol] or self.locked[row2][tempCol]: continue
    #             n3, n4 = (row1, tempCol), (row2, tempCol)
    #             n3Set, n4Set = self.getSet(n3), self.getSet(n4)
    #             if not (comboSet <= (n3Set & n4Set)): continue
    #             group = [n1, n2, n3, n4]

    #             # Type 1
    #             if self.inBox([n1, n2]):
    #                 if n3Set == comboSet and comboSet < n4Set:
    #                     eNodes = {(v, n4) for v in comboSet if v in self.layout[n4[0]][n4[1]].note}
    #                     if eNodes and not uberPrune(current_node, ("Unique Rectangles Col 1", group, eNodes, None)):
    #                         baseCopy.updateNotesGX(eNodes)
    #                         diffNodes = self.puzzleDifference(baseCopy)
    #                         note = f"Unique Rectangles Col Type 1 with floor {n1} & {n2} and vals {combo}, found vals {combo} at {n3}\nRemoving {combo} from {diffNodes}"
    #                         baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Unique Rectangles Col 1", current_node, group)
    #                         newPuzzles.append(tempPuzzle)
    #                 elif n4Set == comboSet and comboSet < n3Set:
    #                     eNodes = {(v, n3) for v in comboSet if v in self.layout[n3[0]][n3[1]].note}
    #                     if eNodes and not uberPrune(current_node, ("Unique Rectangles Col 1", group, eNodes, None)):
    #                         baseCopy.updateNotesGX(eNodes)
    #                         diffNodes = self.puzzleDifference(baseCopy)
    #                         note = f"Unique Rectangles Col Type 1 with floor {n1} & {n2} and vals {combo}, found vals {combo} at {n4}\nRemoving {combo} from {diffNodes}"
    #                         baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Unique Rectangles Col 1", current_node, group)
    #                         newPuzzles.append(tempPuzzle)

    #             if self.inBox([n1, n2]) and not self.inBox([n1, n3]):
    #                 # Type 2A
    #                 if len(n3Set | n4Set) == 3 and n3Set == n4Set:
    #                     eVal = (n3Set - comboSet).pop()
    #                     eNodes = {(eVal, (r, c)) for r, c in
    #                               [(r, c) for r, c in self.getBoxCells(n3) if (r, c) not in [n3, n4]] +
    #                               [(r, c) for r, c in self.getColCells(n3) if (r, c) not in [n3, n4]]
    #                               if eVal in self.layout[r][c].note}
    #                     if eNodes and not uberPrune(current_node, ("Unique Rectangles Col 2A", group, eNodes, None)):
    #                         baseCopy.updateNotesGX(eNodes)
    #                         diffNodes = self.puzzleDifference(baseCopy)
    #                         note = f"Unique Rectangles Col Type 2A with floor {n1} & {n2} and vals {combo}, found vals {n3Set} at {n3} & {n4}\nRemoving {eVal} from {diffNodes}"
    #                         baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Unique Rectangles Col 2A", current_node, group)
    #                         newPuzzles.append(tempPuzzle)

    #                 if len(n3Set | n4Set) >= 3 and n3Set != n4Set:
    #                     # Type 3B
    #                     if len(n3Set) == len(n4Set) == 3:
    #                         targetSet = (n3Set | n4Set) - comboSet
    #                         eNodes = set()
    #                         targetNodes = self.getExColIdxs((row1, tempCol), targetSet)
    #                         if targetNodes:
    #                             targetNode = targetNodes.pop()
    #                             eNodes |= {(v, (r, c)) for v in targetSet for r, c in [targetNode, n3, n4] if v in self.layout[r][c].note}
    #                         targetNodes = self.getExBoxIdxs((row1, tempCol), targetSet)
    #                         if targetNodes:
    #                             targetNode = targetNodes.pop()
    #                             eNodes |= {(v, (r, c)) for v in targetSet for r, c in [targetNode, n3, n4] if v in self.layout[r][c].note}
    #                         if eNodes and not uberPrune(current_node, ("Unique Rectangles Col 3B", group, eNodes, None)):
    #                             baseCopy.updateNotesGX(eNodes)
    #                             diffNodes = self.puzzleDifference(baseCopy)
    #                             note = f"Unique Rectangles Col Type 3B with floor {n1} & {n2} and vals {combo}, found {n3Set} at {n3} and {n4Set} at {n4}\nErasing {diffNodes}"
    #                             baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Unique Rectangles Col 3B", current_node, group)
    #                             newPuzzles.append(tempPuzzle)

    #                     # Type 3/3B Pseudo
    #                     if (len(n3Set) == 3 and len(n4Set) == 4) or (len(n3Set) == 4 and len(n4Set) == 3):
    #                         x, y, z = self.findPseudoLoop('col', comboSet, [n3, n4])
    #                         if x:
    #                             eNodes = {(v, (r, c)) for v in z for r, c in y if v in self.layout[r][c].note}
    #                             if eNodes and not uberPrune(current_node, ("Unique Rectangles Col 3/3B", group, eNodes, None)):
    #                                 baseCopy.updateNotesGX(eNodes)
    #                                 diffNodes = self.puzzleDifference(baseCopy)
    #                                 note = f"Unique Rectangles Col Type 3/3B with floor {n1} & {n2} and vals {combo}, found ceiling {n3} & {n4}\nErasing {diffNodes}"
    #                                 baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Unique Rectangles Col 3/3B", current_node, group)
    #                                 newPuzzles.append(tempPuzzle)

    #                 # Type 4A
    #                 if self.singleColCheck([n3, n4], {combo[0]}) ^ self.singleColCheck([n3, n4], {combo[1]}):
    #                     if self.singleColCheck([n3, n4], {combo[0]}): critVal, eVal = combo[0], combo[1]
    #                     else: critVal, eVal = combo[1], combo[0]
    #                     eNodes = {(eVal, (r, c)) for r, c in [n3, n4] if eVal in self.layout[r][c].note}
    #                     if eNodes and not uberPrune(current_node, ("Unique Rectangles Col 4A", group, eNodes, None)):
    #                         baseCopy.updateNotesGX(eNodes)
    #                         diffNodes = self.puzzleDifference(baseCopy)
    #                         note = f"Unique Rectangles Col Type 4A with floor {n1} & {n2} and vals {combo}, found {critVal} exclusive to col\nRemoving {eVal} from {diffNodes}"
    #                         baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Unique Rectangles Col 4A", current_node, group)
    #                         newPuzzles.append(tempPuzzle)

    #             if not self.inBox([n1, n2]) and self.inBox([n1, n3]):
    #                 # Type 2B
    #                 if len(n3Set | n4Set) == 3 and n3Set == n4Set:
    #                     eVal = (n3Set - comboSet).pop()
    #                     eNodes = {(eVal, (r, c)) for r, c in self.getColCells(n3) if (r, c) not in [n3, n4] and eVal in self.layout[r][c].note}
    #                     if eNodes and not uberPrune(current_node, ("Unique Rectangles Col 2B", group, eNodes, None)):
    #                         baseCopy.updateNotesGX(eNodes)
    #                         diffNodes = self.puzzleDifference(baseCopy)
    #                         note = f"Unique Rectangles Col Type 2B with floor {n1} & {n2} and vals {combo}, found vals {n3Set} at {n3} & {n4}\nRemoving {eVal} from {diffNodes}"
    #                         baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Unique Rectangles Col 2B", current_node, group)
    #                         newPuzzles.append(tempPuzzle)

    #                 # Type 3A
    #                 if len(n3Set | n4Set) == 4 and n3Set != n4Set and len(n3Set) == len(n4Set) == 3 and comboSet == (n3Set & n4Set):
    #                     targetSet = (n3Set | n4Set) - comboSet
    #                     eNodes = set()
    #                     targetNodes = self.getExColIdxs((row1, tempCol), targetSet)
    #                     if targetNodes:
    #                         targetNode = targetNodes.pop()
    #                         eNodes |= {(v, (r, c)) for v in targetSet for r, c in [targetNode, n3, n4] if v in self.layout[r][c].note}
    #                     if eNodes and not uberPrune(current_node, ("Unique Rectangles Col 3A", group, eNodes, None)):
    #                         baseCopy.updateNotesGX(eNodes)
    #                         diffNodes = self.puzzleDifference(baseCopy)
    #                         note = f"Unique Rectangles Col Type 3A with floor {n1} & {n2} and vals {combo}, found {n3Set} at {n3} and {n4Set} at {n4}\nErasing {diffNodes}"
    #                         baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Unique Rectangles Col 3A", current_node, group)
    #                         newPuzzles.append(tempPuzzle)

    #                 # Type 4B
    #                 if self.singleColCheck([n3, n4], {combo[0]}) ^ self.singleColCheck([n3, n4], {combo[1]}):
    #                     if self.singleColCheck([n3, n4], {combo[0]}): critVal, eVal = combo[0], combo[1]
    #                     else: critVal, eVal = combo[1], combo[0]
    #                     eNodes = {(eVal, (r, c)) for r, c in [n3, n4] if eVal in self.layout[r][c].note}
    #                     if eNodes and not uberPrune(current_node, ("Unique Rectangles Col 4B", group, eNodes, None)):
    #                         baseCopy.updateNotesGX(eNodes)
    #                         diffNodes = self.puzzleDifference(baseCopy)
    #                         note = f"Unique Rectangles Col Type 4B with floor {n1} & {n2} and vals {combo}, found {critVal} exclusive to col\nRemoving {eVal} from {diffNodes}"
    #                         baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Unique Rectangles Col 4B", current_node, group)
    #                         newPuzzles.append(tempPuzzle)

    #     for combo, n1, n2 in colRPSets | rowRPSets:
    #         comboSet = set(combo)
    #         x1, y1 = n1
    #         x2, y2 = n2
    #         n3, n4 = (x1, y2), (x2, y1)
    #         group = [n1, n2, n3, n4]
    #         r5Vals = {(node, val): [0, 0] for node in [n1, n2] for val in combo}
    #         n3Set, n4Set = self.getSet(n3), self.getSet(n4)
    #         if not(comboSet <= (n3Set & n4Set)): continue

    #         if n3Set == n4Set and len(n3Set) == 3:
    #             eVal = (n3Set - comboSet).pop()
    #             eNodes = set()
    #             if self.sameColChute([n1, n2]):
    #                 rowOffset1, rowOffset2 = self.getOffset(x1), self.getOffset(x2)
    #                 for row in range(rowOffset1, rowOffset1 + 3):
    #                     if row == x1: continue
    #                     if eVal in self.layout[row][y1].note: eNodes.add((eVal, (row, y1)))
    #                 for row in range(rowOffset2, rowOffset2 + 3):
    #                     if row == x2: continue
    #                     if eVal in self.layout[row][y2].note: eNodes.add((eVal, (row, y2)))
    #             if self.sameRowChute([n1, n2]):
    #                 colOffset1, colOffset2 = self.getOffset(y1), self.getOffset(y2)
    #                 for col in range(colOffset1, colOffset1 + 3):
    #                     if col == y1: continue
    #                     if eVal in self.layout[x1][col].note: eNodes.add((eVal, (x1, col)))
    #                 for col in range(colOffset2, colOffset2 + 3):
    #                     if col == y2: continue
    #                     if eVal in self.layout[x2][col].note: eNodes.add((eVal, (x2, col)))
    #             if eNodes and not uberPrune(current_node, ("Unique Rectangles 2C", group, eNodes, None)):
    #                 baseCopy.updateNotesGX(eNodes)
    #                 diffNodes = self.puzzleDifference(baseCopy)
    #                 note = f"Unique Rectangles Type 2C found {comboSet} in {n1} and {n2}, erasing {diffNodes}"
    #                 baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Unique Rectangles 2C", current_node, group)
    #                 newPuzzles.append(tempPuzzle)

    #         for val in combo:
    #             funcs = [self.singleRowCheck, self.singleColCheck]
    #             for base in [n1, n2]:
    #                 for check in [n3, n4]:
    #                     for func in funcs:
    #                         if not func([base, check], {val}):
    #                             r5Vals[(base, val)][0] += 1
    #                     if self.singleBoxCheck([base, check], {val}):
    #                         r5Vals[(base, val)][1] += 1

    #         eNodes = set()
    #         for (node, critVal), countArry in r5Vals.items():
    #             if countArry[0] == 2 and countArry[1] == 1:
    #                 eVal = (comboSet - {critVal}).pop()
    #                 if eVal in self.layout[node[0]][node[1]].note:
    #                     eNodes.add((eVal, node))
    #         if eNodes and not uberPrune(current_node, ("Unique Rectangles 5", group, eNodes, None)):
    #             baseCopy.updateNotesGX(eNodes)
    #             diffNodes = self.puzzleDifference(baseCopy)
    #             note = f"Unique Rectangles Type 5 found {comboSet} in {n1} & {n2}\nRemoving {diffNodes}"
    #             baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Unique Rectangles 5", current_node, group)
    #             newPuzzles.append(tempPuzzle)

    #     return baseCopy, newPuzzles

    # def uniqueRectangles(self, baseCopy):
    #     newPuzzles = []
    #     rowSets, colSets, rowRPSets, colRPSets = set(), set(), set(), set()
    #     for combo in itertools.combinations(self.getRemaining(), 2):
    #         comboSet = set(combo)
    #         for row in range(9):
    #             matchingCols = [c for c in range(9) if self.getSet((row, c)) == comboSet]
    #             if len(matchingCols) == 2: rowSets.add((combo, row, matchingCols[0], matchingCols[1]))
    #         for col in range(9):
    #             matchingRows = [r for r in range(9) if self.getSet((r, col)) == comboSet]
    #             if len(matchingRows) == 2: colSets.add((combo, col, matchingRows[0], matchingRows[1]))
    #         rowRP = sorted(self.getRowChuteRemotePairs(comboSet))
    #         colRP = sorted(self.getColChuteRemotePairs(comboSet))
    #         for n1, n2 in rowRP: rowRPSets.add((combo, n1, n2))
    #         for n1, n2 in colRP: colRPSets.add((combo, n1, n2))
    #     # print("RowSets")
    #     # if rowSets:
    #     #     for combo, row, col1, col2 in rowSets:
    #     #         print(f"{combo}: {(row, col1)} {(row, col2)}")
    #     # print("ColSets")
    #     # if colSets:
    #     #     for combo, col, row1, row2 in colSets:
    #     #         print(f"{combo}: {(row1, col)} {(row2, col)}")
    #     for combo, row, col1, col2 in rowSets:
    #         comboSet = set(combo)
    #         n1, n2 = (row, col1), (row, col2)
    #         for tempRow in range(9):
    #             if row == tempRow or self.locked[tempRow][col1] or self.locked[tempRow][col2]: continue
    #             n3, n4 = (tempRow, col1), (tempRow, col2)
    #             n3Set, n4Set = self.getSet(n3), self.getSet(n4)
    #             if not (comboSet <= (n3Set & n4Set)): continue
    #             # Type 1
    #             if n3Set == comboSet and n4Set != comboSet:
    #                 baseCopy.updateNotesDX([n4], comboSet)
    #                 note = f"Unique Rectangles Row Type 1 with floor {n1} & {n2} and vals {combo}, found vals {combo} at {n3}\nRemoving {combo} from {n4}"
    #             elif n4Set == comboSet and n3Set != comboSet:
    #                 baseCopy.updateNotesDX([n3], comboSet)
    #                 note = f"Unique Rectangles Row Type 1 with floor {n1} & {n2} and vals {combo}, found vals {combo} at {n4}\nremoving {combo} from {n3}"
    #             if not self.stuck(baseCopy):
    #                 baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Unique Rectangles Row 1", current_node)
    #                 newPuzzles.append(tempPuzzle)
    #             if self.inBox([n1, n2]) and not self.inBox([n1, n3]): 
    #                 # Type 2A
    #                 if len(n3Set | n4Set) == 3 and n3Set == n4Set:
    #                     eVal = (n3Set - comboSet).pop()
    #                     baseCopy.subUpdateNotes('box', [n3, n4], {eVal})
    #                     baseCopy.subUpdateNotes('row', [n3, n4], {eVal})
    #                     if not self.stuck(baseCopy): 
    #                         note = f"Unique Rectangles Row Type 2A with floor {n1} & {n2} and vals {combo}, found vals {n3Set} at {n3} & {n4}\nRemoving {eVal} from row and box"
    #                         baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Unique Rectangles Row 2A", current_node)
    #                         newPuzzles.append(tempPuzzle)
    #                 if len(n3Set | n4Set) >= 3 and n3Set != n4Set:
    #                     # Type 3B
    #                     if len(n3Set) == len(n4Set) == 3:
    #                         targetSet = (n3Set | n4Set) - comboSet
    #                         targetNodes = self.getExRowIdxs((tempRow, col1), targetSet)
    #                         if targetNodes:
    #                             targetNode = targetNodes.pop()
    #                             baseCopy.subUpdateNotes('row', [targetNode, n3, n4], targetSet)
    #                         targetNodes = self.getExBoxIdxs((tempRow, col1), targetSet)
    #                         if targetNodes:
    #                             targetNode = targetNodes.pop()
    #                             baseCopy.subUpdateNotes('box', [targetNode, n3, n4], targetSet)
    #                         if not self.stuck(baseCopy): 
    #                             note = f"Unique Rectangles Row Type 3B with floor {n1} & {n2} and vals {combo}, found {n3Set} at {n3} and {n4Set} at {n4}\nFound conditions to erase {targetSet} from row/box or both"
    #                             baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Unique Rectangles Row 3B", current_node)
    #                             newPuzzles.append(tempPuzzle)
    #                     # Type 3/3B Pseudo
    #                     if (len(n3Set) == 3 and len(n4Set) == 4) or (len(n3Set) == 4 and len(n4Set) == 3):
    #                         x, y, z = self.findPseudoLoop('row', comboSet, [n3, n4])
    #                         if x: 
    #                             baseCopy.subUpdateNotes('row', y, z)
    #                             if not self.stuck(baseCopy): 
    #                                 note = f"Unique Rectangles Row Type 3/3B pseudo with floor {n1} & {n2} and vals {combo}, found ceiling {n3} & {n4}\nFound found a loop containing vals {z} at {y}, erasing {z} from row"
    #                                 baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Unique Rectangles Row 3/3B", current_node)
    #                                 newPuzzles.append(tempPuzzle)
    #                     # Type 4A 
    #                     if self.singleRowCheck([n3, n4], {combo[0]}) ^ self.singleRowCheck([n3, n4], {combo[1]}):
    #                         if self.singleRowCheck([n3, n4], {combo[0]}): critVal, eVal = combo[0], combo[1]
    #                         else: critVal, eVal = combo[1], combo[0]
    #                         baseCopy.updateNotesDX([n3, n4], {eVal})
    #                         if not self.stuck(baseCopy): 
    #                             note = f"Unique Rectangles Row Type 4A with floor {n1} & {n2} and vals {combo}, found {critVal} exclusive to row containing {n3} & {n4}\nRemoving {eVal} from nodes {n3} & {n4}"
    #                             baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Unique Rectangles Row 4A", current_node)
    #                             newPuzzles.append(tempPuzzle)
    #             if not self.inBox([n1, n2]) and self.inBox([n1, n3]):
    #                 # Type 2B
    #                 if len(n3Set | n4Set) == 3 and n3Set == n4Set:
    #                     eVal = (n3Set - comboSet).pop()
    #                     baseCopy.subUpdateNotes('row', [n3, n4], {eVal})
    #                     if not self.stuck(baseCopy): 
    #                         note = f"Unique Rectangles Row Type 2B with floor {n1} & {n2} and vals {combo}, found vals {n3Set} at {n3} & {n4}\nRemoving {eVal} from row"
    #                         baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Unique Rectangles Row 2B", current_node)
    #                         newPuzzles.append(tempPuzzle)
    #                 # Type 3A
    #                 if len(n3Set | n4Set) == 4 and n3Set != n4Set and len(n3Set) == len(n4Set) == 3:
    #                     targetSet = (n3Set | n4Set) - comboSet
    #                     targetNodes = self.getExRowIdxs((tempRow, col1), targetSet)
    #                     if targetNodes:
    #                         targetNode = targetNodes.pop()
    #                         baseCopy.subUpdateNotes('row', [targetNode, n3, n4], targetSet)
    #                     if not self.stuck(baseCopy): 
    #                         note = f"Unique Rectangles Row Type 3A with floor {n1} & {n2} and vals {combo}, found {n3Set} at {n3} and {n4Set} at {n4}\nFound {targetSet} at {targetNode}, erasing {targetSet} in row {tempRow}"
    #                         baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Unique Rectangles Row 3A", current_node)
    #                         newPuzzles.append(tempPuzzle)
    #                 if self.singleRowCheck([n3, n4], {combo[0]}) ^ self.singleRowCheck([n3, n4], {combo[1]}):
    #                     if self.singleRowCheck([n3, n4], {combo[0]}): critVal, eVal = combo[0], combo[1]
    #                     else: critVal, eVal = combo[1], combo[0]
    #                     baseCopy.updateNotesDX([n3, n4], {eVal})
    #                     if not self.stuck(baseCopy): 
    #                         note = f"Unique Rectangles Row Type 4B with floor {n1} & {n2} and vals {combo}, found {critVal} exclusive to row containing {n3} & {n4}\nRemoving {eVal} from nodes {n3} & {n4}"
    #                         baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Unique Rectangles Row 4B", current_node)
    #                         newPuzzles.append(tempPuzzle)

    #     for combo, col, row1, row2 in colSets:
    #         comboSet = set(combo)
    #         n1, n2 = (row1, col), (row2, col)
    #         for tempCol in range(9):
    #             if col == tempCol or self.locked[row1][tempCol] or self.locked[row2][tempCol]: continue
    #             n3, n4 = (row1, tempCol), (row2, tempCol)
    #             n3Set, n4Set = self.getSet(n3), self.getSet(n4)
    #             if not (comboSet <= (n3Set & n4Set)): continue
    #             # Type 1
    #             if n3Set == comboSet and comboSet < n4Set:
    #                 baseCopy.updateNotesDX([n4], comboSet)
    #                 note = f"Unique Rectangles Col Type 1 with floor {n1} & {n2} and vals {combo}, found vals {combo} at {n3}\nRemoving {combo} from {n4}"
    #             elif n4Set == comboSet and comboSet < n3Set:
    #                 baseCopy.updateNotesDX([n3], comboSet)
    #                 note = f"Unique Rectangles Col Type 1 with floor {n1} & {n2} and vals {combo}, found vals {combo} at {n4}\nremoving {combo} from {n3}"
    #             if not self.stuck(baseCopy):
    #                 baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Unique Rectangles Col 1", current_node)
    #                 newPuzzles.append(tempPuzzle)
    #             if self.inBox([n1, n2]) and not self.inBox([n1, n3]):
    #                 # Type 2A
    #                 if len(n3Set | n4Set) == 3 and n3Set == n4Set:
    #                     eVal = (n3Set - comboSet).pop()
    #                     baseCopy.subUpdateNotes('box', [n3, n4], {eVal})
    #                     baseCopy.subUpdateNotes('col', [n3, n4], {eVal})
    #                     if not self.stuck(baseCopy): 
    #                         note = f"Unique Rectangles Col Type 2A with floor {n1} & {n2} and vals {combo}, found vals {n3Set} at {n3} & {n4}\nRemoving {eVal} from row and box"
    #                         baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Unique Rectangles Col 2A", current_node)
    #                         newPuzzles.append(tempPuzzle)
    #                 if len(n3Set | n4Set) >= 3 and n3Set != n4Set:
    #                     # Type 3B
    #                     if len(n3Set) == len(n4Set) == 3:
    #                         targetSet = (n3Set | n4Set) - comboSet
    #                         targetNodes = self.getExColIdxs((row1, tempCol), targetSet)
    #                         if targetNodes:
    #                             targetNode = targetNodes.pop()
    #                             baseCopy.subUpdateNotes('col', [targetNode, n3, n4], targetSet)
    #                         targetNodes = self.getExBoxIdxs((row1, tempCol), targetSet)
    #                         if targetNodes:
    #                             targetNode = targetNodes.pop()
    #                             baseCopy.subUpdateNotes('box', [targetNode, n3, n4], targetSet)
    #                         if not self.stuck(baseCopy): 
    #                             note = f"Unique Rectangles Col Type 3B with floor {n1} & {n2} and vals {combo}, found {n3Set} at {n3} and {n4Set} at {n4}\nFound conditions to erase {targetSet} from col/box or both"
    #                             baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Unique Rectangles Col 3B", current_node)
    #                             newPuzzles.append(tempPuzzle)
    #                     # Type 3/3B Pseudo
    #                     if (len(n3Set) == 3 and len(n4Set) == 4) or (len(n3Set) == 4 and len(n4Set) == 3):
    #                         x, y, z = self.findPseudoLoop('col', comboSet, [n3, n4])
    #                         if x: 
    #                             baseCopy.subUpdateNotes('col', y, z)
    #                             if not self.stuck(baseCopy): 
    #                                 note = f"Unique Rectangles Col Type 3/3B with floor {n1} & {n2} and vals {combo}, found ceiling {n3} & {n4}\nFound found a loop containing vals {z} at {y}, erasing {z} from row"
    #                                 baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Unique Rectangles Col 3/3B", current_node)
    #                                 newPuzzles.append(tempPuzzle)
    #                 # Type 4A
    #                 if self.singleColCheck([n3, n4], {combo[0]}) ^ self.singleColCheck([n3, n4], {combo[1]}):
    #                     if self.singleColCheck([n3, n4], {combo[0]}): critVal, eVal = combo[0], combo[1]
    #                     else: critVal, eVal = combo[1], combo[0]
    #                     baseCopy.updateNotesDX([n3, n4], {eVal})
    #                     if not self.stuck(baseCopy): 
    #                         note = f"Unique Rectangles Col Type 4A with floor {n1} & {n2} and vals {combo}, found {critVal} exclusive to col containing {n3} & {n4}\nRemoving {eVal} from nodes {n3} & {n4}"
    #                         baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Unique Rectangles Col 4A", current_node)
    #                         newPuzzles.append(tempPuzzle)
                                
    #             if not self.inBox([n1, n2]) and self.inBox([n1, n3]):
    #                 # Type 2B
    #                 if len(n3Set | n4Set) == 3 and n3Set == n4Set:
    #                     eVal = (n3Set - comboSet).pop()
    #                     baseCopy.subUpdateNotes('col', [n3, n4], {eVal})
    #                     if not self.stuck(baseCopy): 
    #                         note = f"Unique Rectangles Col Type 2B with floor {n1} & {n2} and vals {combo}, found vals {n3Set} at {n3} & {n4}\nRemoving {eVal} from row"
    #                         baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Unique Rectangles Col 2B", current_node)
    #                         newPuzzles.append(tempPuzzle)
    #                 # Type 3A
    #                 if len(n3Set | n4Set) == 4 and n3Set != n4Set and len(n3Set) == len(n4Set) == 3 and comboSet == (n3Set & n4Set):
    #                     targetSet = (n3Set | n4Set) - comboSet
    #                     targetNodes = self.getExColIdxs((row1, tempCol), targetSet)
    #                     if targetNodes:
    #                         targetNode = targetNodes.pop()
    #                         baseCopy.subUpdateNotes('col', [targetNode, n3, n4], targetSet)
    #                     if not self.stuck(baseCopy): 
    #                         note = f"Unique Rectangles Col Type 3A with floor {n1} & {n2} and vals {combo}, found {n3Set} at {n3} and {n4Set} at {n4}\nFound {targetSet} at {(tempRow, tempCol)}, erasing {targetSet} in col {tempCol}"
    #                         baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Unique Rectangles Col 3A", current_node)
    #                         newPuzzles.append(tempPuzzle)
    #                 # Type 4B
    #                 if self.singleColCheck([n3, n4], {combo[0]}) ^ self.singleColCheck([n3, n4], {combo[1]}):
    #                     if self.singleColCheck([n3, n4], {combo[0]}): critVal, eVal = combo[0], combo[1]
    #                     else: critVal, eVal = combo[1], combo[0]
    #                     baseCopy.updateNotesDX([n3, n4], {eVal})
    #                     if not self.stuck(baseCopy): 
    #                         note = f"Unique Rectangles Col Type 4B with floor {n1} & {n2} and vals {combo}, found {critVal} exclusive to col containing {n3} & {n4}\nRemoving {eVal} from nodes {n3} & {n4}"
    #                         baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Unique Rectangles Col 4B", current_node)
    #                         newPuzzles.append(tempPuzzle)
       
    #     for combo, n1, n2 in colRPSets | rowRPSets:
    #         comboSet = set(combo)
    #         x1, y1 = n1
    #         x2, y2 = n2
    #         n3, n4 = (x1, y2), (x2, y1)
    #         r5Vals = {(node, val): [0, 0] for node in [n1, n2] for val in combo}
    #         n3Set, n4Set = self.getSet(n3), self.getSet(n4)
    #         if not(comboSet <= (n3Set & n4Set)): continue 
    #         if n3Set == n4Set and len(n3Set) == 3:
    #             eVal, eNodes = (n3Set - comboSet).pop(), []
    #             if self.sameColChute([n1, n2]):
    #                 rowOffset1, rowOffset2 = self.getOffset(x1), self.getOffset(x2)
    #                 for row in range(rowOffset1, rowOffset1 + 3):
    #                     if row == x1: continue
    #                     eNodes += [(row, y1)]
    #                 for row in range(rowOffset2, rowOffset2 + 3):
    #                     if row == x2: continue
    #                     eNodes += [(row, y2)]
    #             if self.sameRowChute([n1, n2]):
    #                 colOffset1, colOffset2 = self.getOffset(y1), self.getOffset(y2)
    #                 for col in range(colOffset1, colOffset1 + 3):
    #                     if col == y1: continue
    #                     eNodes += [(x1, col)]
    #                 for col in range(colOffset2, colOffset2 + 3):
    #                     if col == y2: continue
    #                     eNodes += [(x2, col)]
    #             baseCopy.updateNotesDX(eNodes, {eVal})
    #             if not self.stuck(baseCopy):
    #                 note = f"Unique Rectangles Type 2C found {comboSet} in {n1} and {n2}, erasing {eVal} from {eNodes}"
    #                 baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Unique Rectangles 2C", current_node)
    #                 newPuzzles.append(tempPuzzle)
    #         for val in combo:
    #             funcs = [self.singleRowCheck, self.singleColCheck]
    #             for base in [n1, n2]:
    #                 for check in [n3, n4]:
    #                     for func in funcs:
    #                         if not func([base, check], {val}):
    #                             r5Vals[(base, val)][0] += 1
    #                     if self.singleBoxCheck([base, check], {val}):
    #                         r5Vals[(base, val)][1] += 1
    #         for (node, critVal), countArry in r5Vals.items():
    #             # print(node, critVal, countArry)
    #             if countArry[0] == 2 and countArry[1] == 1: 
    #                 eVal = (comboSet - {critVal}).pop()
    #                 baseCopy.updateNotesDX([node], {eVal})
    #         if not self.stuck(baseCopy): 
    #             note = f"Unique Rectangles Type 5 found {comboSet} in {n1} & {n2}\nFound that one of {combo} had strong links in the square, rows, and columns\nRemoving one of {combo} from either {n1}, {n2} or both"
    #             baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Unique Rectangles 5", current_node)
    #             newPuzzles.append(tempPuzzle)
    #     return baseCopy, newPuzzles
        
    # def findPseudoLoop(self, typeof, combo, ceilingNodes):
    #     ceiling = (self.getSet(ceilingNodes[0]) | self.getSet(ceilingNodes[1])) - combo
    #     for idx in range(9):
    #         if typeof == 'row': r, c = ceilingNodes[0][0], idx
    #         else: r, c = idx, ceilingNodes[0][1]
    #         if self.locked[r][c]: continue
    #         cand = self.getSet((r, c))
    #         if cand & combo: continue
    #         if not (cand & ceiling): continue
    #         coords = [(r, c)] + ceilingNodes
    #         master = set(cand)
    #         for step in range(idx + 1, 9):
    #             if typeof == 'row': rr, cc = r, step
    #             else: rr, cc = step, c
    #             if self.locked[rr][cc]: continue
    #             temp = self.getSet((rr, cc))
    #             if temp & combo: continue
    #             if not (temp & ceiling): continue
    #             coords.append((rr, cc))
    #             master |= temp
    #             if len(coords) >= 3 and len(master) == len(coords) - 1: return True, coords, master
    #     return False, None, None
    def findPseudoLoop(self, flip, comboSet, ceilingNodes):
        n3, n4 = ceilingNodes
        boxCells = self.getAllBoxCoords(n3)
        if not self.inBox(ceilingNodes): return False, None, None
        
        if flip:
            ceilCol = n3[1]
            boxColOffset = self.getOffset(ceilCol)
            otherCols = [c for c in range(boxColOffset, boxColOffset + 3) if c != ceilCol]
            pseudoPairs = [((n3[0], c), (n4[0], c)) for c in otherCols]
        else:
            ceilRow = n3[0]
            boxRowOffset = self.getOffset(ceilRow)
            otherRows = [r for r in range(boxRowOffset, boxRowOffset + 3) if r != ceilRow]
            pseudoPairs = [((r, n3[1]), (r, n4[1])) for r in otherRows]
        
        for p1, p2 in pseudoPairs:
            if self.locked[p1[0]][p1[1]] or self.locked[p2[0]][p2[1]]: continue
            if self.getSet(p1) & comboSet or self.getSet(p2) & comboSet: continue
            
            p1Set = self.getSet(p1)
            p2Set = self.getSet(p2)
            n3Set = self.getSet(n3)
            n4Set = self.getSet(n4)
            
            ceilingExtras = (n3Set | n4Set) - comboSet
            pseudoVals = p1Set | p2Set
            if not (ceilingExtras & pseudoVals): continue
            
            allExtras = ceilingExtras | pseudoVals
            if len(allExtras) > 3: continue
            
            targetSet = pseudoVals
            excludeNodes = {n3, n4, p1, p2}
            eNodes = {
                (v, (r, c)) for v in targetSet
                for r, c in boxCells
                if (r, c) not in excludeNodes
                and not self.locked[r][c]
                and v in self.layout[r][c].note
                and v not in comboSet
            }
            
            if eNodes:
                return True, list(excludeNodes), targetSet
        
        return False, None, None
    # ********************************************************************************************************************    
    def tridagon(self, baseCopy, current_node):
        newPuzzles = []
        remaining = self.getRemaining()
        boxIdxs = [0, 3, 6]
        rowAdjBoxes, colAdjBoxes = {}, {}
        for r in boxIdxs:
            for c in boxIdxs:
                boxRoot = (r, c)
                rowAdjBoxes[boxRoot] = self.getRowAdjacentBoxes(boxRoot)
                colAdjBoxes[boxRoot] = self.getColAdjacentBoxes(boxRoot)
    
        boxNodes, pattern, comboRoots, imperfectBoxes = {}, {}, {}, {}
    
        for combo in itertools.combinations(remaining, 3):
            comboSet = set(combo)
            for rBox in boxIdxs:
                for cBox in boxIdxs:
                    boxRoot = (rBox, cBox)
                    tempKey = (boxRoot, tuple(combo))
                    if tempKey not in boxNodes:
                        boxNodes[tempKey] = self.getNodes(boxRoot, comboSet)
                    nodes = boxNodes[tempKey]
                    if len(nodes) < 3: continue
                    ascKey = (boxRoot, tuple(combo), 1)
                    if ascKey not in pattern:
                        pattern[ascKey] = self.getAscPattern(boxRoot, comboSet)
                    ascBox = pattern[ascKey]
                    if ascBox is not None:
                        if self.isPerfect(comboSet, ascBox):
                            comboRoots[combo, boxRoot] = (1, ascBox)
                        else:
                            imperfectBoxes[combo, boxRoot] = (1, ascBox)
                    dscKey = (boxRoot, tuple(combo), 0)
                    if dscKey not in pattern:
                        pattern[dscKey] = self.getDscPattern(boxRoot, comboSet)
                    dscBox = pattern[dscKey]
                    if dscBox is not None:
                        if self.isPerfect(comboSet, dscBox):
                            comboRoots[combo, boxRoot] = (0, dscBox)
                        else:
                            imperfectBoxes[combo, boxRoot] = (0, dscBox)
    
        for comboRBox, (typeOf, goodNodes) in comboRoots.items():
            comboSet = set(comboRBox[0])
            combo = comboRBox[0]
            rootBox = comboRBox[1]
            goalType = 1 if typeOf == 0 else 0
            rowBoxes, colBoxes = {}, {}
    
            for adjBox in rowAdjBoxes[rootBox]:
                if (comboRBox[0], adjBox) in comboRoots and comboRoots[comboRBox[0], adjBox][0] == goalType:
                    rowBoxes[adjBox] = comboRoots[comboRBox[0], adjBox][1]
            for adjBox in colAdjBoxes[rootBox]:
                if (comboRBox[0], adjBox) in comboRoots and comboRoots[comboRBox[0], adjBox][0] == goalType:
                    colBoxes[adjBox] = comboRoots[comboRBox[0], adjBox][1]
    
            if not rowBoxes:
                for adjBox in rowAdjBoxes[rootBox]:
                    if (comboRBox[0], adjBox) in imperfectBoxes and imperfectBoxes[comboRBox[0], adjBox][0] == goalType:
                        rowBoxes[adjBox] = imperfectBoxes[comboRBox[0], adjBox][1]
            if not colBoxes:
                for adjBox in colAdjBoxes[rootBox]:
                    if (comboRBox[0], adjBox) in imperfectBoxes and imperfectBoxes[comboRBox[0], adjBox][0] == goalType:
                        colBoxes[adjBox] = imperfectBoxes[comboRBox[0], adjBox][1]
    
            if not (rowBoxes or colBoxes): continue
    
            for rowBox, rowIndexes in rowBoxes.items():
                for colBox, colIndexes in colBoxes.items():
                    cornerBox = (colBox[0], rowBox[1])
                    cornerKey = (cornerBox, tuple(combo), goalType)
                    if cornerKey not in pattern:
                        if goalType == 1:
                            pattern[cornerKey] = self.getAscPattern(cornerBox, comboSet)
                        else:
                            pattern[cornerKey] = self.getDscPattern(cornerBox, comboSet)
                    cornerNodes = pattern[cornerKey]
                    if cornerNodes is None: continue
    
                    evilBox = []
                    for nodeSet in [rowIndexes, colIndexes, cornerNodes]:
                        if not self.isPerfect(comboSet, set(nodeSet)):
                            evilBox += nodeSet
                    if len(evilBox) != 3: continue
    
                    targetNodes = self.getGuardians(comboSet, evilBox)
                    targetValSet = {(self.getSet(node) - comboSet).pop() for node in targetNodes}
                    if len(targetValSet) != 1: continue
                    targetVal = targetValSet.pop()
                    group = evilBox
    
                    if len(targetNodes) == 1:
                        targetNode = targetNodes.pop()
                        eNodes = {(eVal, targetNode) for eVal in combo}
                        if eNodes and not uberPrune(current_node, ("Tridagon Type 1", group, eNodes, None)):
                            baseCopy.updateNotesGX(eNodes)
                            if self.stuck(baseCopy): continue
                            diffNodes = self.puzzleDifference(baseCopy)
                            note = f"Tridagon Type 1 found vals {comboSet}\nRoot {rootBox} RowBox {rowBox}, ColBox {colBox}, & CornerBox {cornerBox}\nFound a bad box with nodes {evilBox} at {targetNode}\nSetting {targetNode} to {targetVal}"
                            baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Tridagon Type 1", current_node, group)
                            newPuzzles.append(tempPuzzle)
    
                    elif len(targetNodes) == 2:
                        # eNodes = {(targetVal, node) for node in targetNodes if targetVal in self.layout[node[0]][node[1]].note}
                        eNodes = {(targetVal, node) for node in self.getAllBoxCoords(evilBox[0]) - set(evilBox) if targetVal in self.getSet(node)}
                        if eNodes and not uberPrune(current_node, ("Tridagon Type 2", group, eNodes, None)):
                            baseCopy.updateNotesGX(eNodes)
                            if self.stuck(baseCopy): continue
                            diffNodes = self.puzzleDifference(baseCopy)
                            note = f"Tridagon Type 2 found vals {comboSet}\nRoot {rootBox} RowBox {rowBox}, ColBox {colBox}, & CornerBox {cornerBox}\nFound a bad box with nodes {evilBox}\nRemoving {targetVal} from {diffNodes}"
                            baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Tridagon Type 2", current_node, group)
                            newPuzzles.append(tempPuzzle)
    
        return baseCopy, newPuzzles
    # def tridagon(self, tempCopy):
    #     remaining = self.getRemaining()
    #     boxIdxs = [0, 3, 6]
    #     rowAdjBoxes, colAdjBoxes = {}, {}
    #     for r in boxIdxs:
    #         for c in boxIdxs:
    #             boxRoot = (r, c)
    #             rowAdjBoxes[boxRoot] = self.getRowAdjacentBoxes(boxRoot)
    #             colAdjBoxes[boxRoot] = self.getColAdjacentBoxes(boxRoot)
    
    #     boxNodes, pattern, comboRoots, imperfectBoxes = {}, {}, {}, {}
    
    #     for combo in itertools.combinations(remaining, 3):
    #         comboSet = set(combo)
    #         for rBox in boxIdxs:
    #             for cBox in boxIdxs:
    #                 boxRoot = (rBox, cBox)
    #                 tempKey = (boxRoot, tuple(combo))
    #                 if tempKey not in boxNodes:
    #                     boxNodes[tempKey] = self.getNodes(boxRoot, comboSet)
    #                 nodes = boxNodes[tempKey]
    #                 if len(nodes) < 3: continue #pruningw
    #                 # ASC
    #                 ascKey = (boxRoot, tuple(combo), 1)
    #                 if ascKey not in pattern:
    #                     pattern[ascKey] = self.getAscPattern(boxRoot, comboSet)
    #                 ascBox = pattern[ascKey]
    #                 if ascBox is not None:
    #                     if self.isPerfect(comboSet, ascBox):
    #                         comboRoots[combo, boxRoot] = (1, ascBox)
    #                     else:
    #                         imperfectBoxes[combo, boxRoot] = (1, ascBox)
    #                 # DSC
    #                 dscKey = (boxRoot, tuple(combo), 0)
    #                 if dscKey not in pattern:
    #                     pattern[dscKey] = self.getDscPattern(boxRoot, comboSet)
    #                 dscBox = pattern[dscKey]
    #                 if dscBox is not None:
    #                     if self.isPerfect(comboSet, dscBox):
    #                         comboRoots[combo, boxRoot] = (0, dscBox)
    #                     else:
    #                         imperfectBoxes[combo, boxRoot] = (0, dscBox)

    #     for comboRBox, (typeOf, goodNodes) in comboRoots.items():
    #         comboSet = set(comboRBox[0])
    #         rootBox = comboRBox[1]
    #         goalType = 1 if typeOf == 0 else 0
    #         rowBoxes, colBoxes = {}, {}
    
    #         for adjBox in rowAdjBoxes[rootBox]:
    #             if (comboRBox[0], adjBox) in comboRoots and comboRoots[comboRBox[0], adjBox][0] == goalType:
    #                 rowBoxes[adjBox] = comboRoots[comboRBox[0], adjBox][1]
    #         for adjBox in colAdjBoxes[rootBox]:
    #             if (comboRBox[0], adjBox) in comboRoots and comboRoots[comboRBox[0], adjBox][0] == goalType:
    #                 colBoxes[adjBox] = comboRoots[comboRBox[0], adjBox][1]
    
    #         if not rowBoxes:
    #             for adjBox in rowAdjBoxes[rootBox]:
    #                 if (comboRBox[0], adjBox) in imperfectBoxes and imperfectBoxes[comboRBox[0], adjBox][0] == goalType:
    #                     rowBoxes[adjBox] = imperfectBoxes[comboRBox[0], adjBox][1]
    #         if not colBoxes:
    #             for adjBox in colAdjBoxes[rootBox]:
    #                 if (comboRBox[0], adjBox) in imperfectBoxes and imperfectBoxes[comboRBox[0], adjBox][0] == goalType:
    #                     colBoxes[adjBox] = imperfectBoxes[comboRBox[0], adjBox][1]
    
    #         if not (rowBoxes or colBoxes): continue #pruning
                
    #         for rowBox, rowIndexes in rowBoxes.items():
    #             for colBox, colIndexes in colBoxes.items():
    #                 cornerBox = (colBox[0], rowBox[1])
    #                 cornerKey = (cornerBox, tuple(combo), goalType)
    #                 if cornerKey not in pattern:
    #                     if goalType == 1:
    #                         pattern[cornerKey] = self.getAscPattern(cornerBox, comboSet)
    #                     else:
    #                         pattern[cornerKey] = self.getDscPattern(cornerBox, comboSet)
    #                 cornerNodes = pattern[cornerKey]
    #                 if cornerNodes is None: continue # pruning
    
    #                 evilBox = []
    #                 for nodeSet in [rowIndexes, colIndexes, cornerNodes]:
    #                     if not self.isPerfect(comboSet, set(nodeSet)):
    #                         evilBox += nodeSet
    #                 if len(evilBox) != 3: continue # pruning
                        
    #                 targetNodes = self.getGuardians(comboSet, evilBox)
    #                 targetValSet = { (self.getSet(node) - comboSet).pop() for node in targetNodes }
    #                 if len(targetValSet) != 1: continue # pruning
    #                 targetVal = targetValSet.pop()
                    
    #                 if len(targetNodes) == 1:
    #                     targetNode = targetNodes.pop()
    #                     self.layout[targetNode[0]][targetNode[1]].setVal(targetVal, (targetNode[0], targetNode[1]))
    #                     return print(f"Tridagon Type 1 found vals {comboSet}\nRoot {rootBox} RowBox {rowBox}, ColBox {colBox}, & CornerBox {cornerBox}\nFound a bad box with nodes {evilBox} at {targetNode}\nSetting {targetNode} to {targetVal}")
    #                 if len(targetNodes) == 2:
    #                     self.updateNotesDX(targetNodes, {targetVal})
    #                     return print(f"Tridagon Type 2 found vals {comboSet}\nRoot {rootBox} RowBox {rowBox}, ColBox {colBox}, & CornerBox {cornerBox}\nFound a bad box with nodes {evilBox}\nSetting {targetNode} to {targetVal}")

    
    def getNodes(self, boxRoot, combo):
        rowOffset, colOffset = boxRoot
        goodNodes = []
        for row in range(rowOffset, rowOffset + 3):
            for col in range(colOffset, colOffset + 3):
                tempSet = self.getSet((row, col))
                if self.layout[row][col].val == 0 and (combo <= tempSet or tempSet <= combo): goodNodes.append((row, col))
        goodNodes.sort(key=lambda item: (item[1], -item[0]))
        return goodNodes
        
    def getAscPattern(self, boxRoot, combo):
        nodes = self.getNodes(boxRoot, combo)
        if len(nodes) < 3: return None
        possibleASCTriples = [{(0, 0), (2, 1), (1, 2)},
                              {(1, 0), (0, 1), (2, 2)},
                              {(0, 2), (1, 1), (2, 0)}]
        for triple in itertools.combinations(nodes, 3):
            normalized = {(r - boxRoot[0], c - boxRoot[1]) for r, c in triple}
            if normalized in possibleASCTriples: return list(triple)
        return None
        
    def getDscPattern(self, boxRoot, combo):
        nodes = self.getNodes(boxRoot, combo)
        if len(nodes) < 3: return None
        possibleDSCTriples = [{(0, 0), (1, 1), (2, 2)},
                              {(1, 0), (2, 1), (0, 2)},
                              {(2, 0), (0, 1), (1, 2)}]
        for triple in itertools.combinations(nodes, 3):
            normalized = {(r - boxRoot[0], c - boxRoot[1]) for r, c in triple}
            if normalized in possibleDSCTriples: return list(triple)
        return None
    
    def getRowAdjacentBoxes(self, boxRoot):
        boxes = []
        for i in range(0, 9, 3):
            if i != boxRoot[1]: boxes += [(boxRoot[0], i)] # row boxes
        return boxes

    def getColAdjacentBoxes(self, boxRoot):
        boxes = []
        for i in range(0, 9, 3):
            if i != boxRoot[0]: boxes += [(i, boxRoot[1])] # col boxes
        return boxes
    
    def isPerfect(self, comboSet, nodes):
        return all(self.getSet(node) <= comboSet for node in nodes)

    def getGuardians(self, comboSet, nodes):
        return set(node for node in nodes if not(self.getSet(node) <= comboSet))
    # ********************************************************************************************************************
    def fireworks(self, baseCopy, current_node):
        newPuzzles = []
        remaining = self.getRemaining()
        doubles = [frozenset(x) for x in itertools.combinations(remaining, 2)]
        triples = [frozenset(x) for x in itertools.combinations(remaining, 3)]
        
        doublesCoords = {combo: set() for combo in doubles}
        triplesCoords = {combo: set() for combo in triples}
        
        for r in range(9):
            for c in range(9):
                tempSet = self.getSet((r, c))
                if not tempSet: continue
                for x in doubles:
                    if x <= tempSet:
                        doublesCoords[x].add((r, c))
                for x in triples:
                    if x <= tempSet:
                        triplesCoords[x].add((r, c))
    
        # Triple Fireworks
        for combo in triplesCoords:
            for rr, rc in triplesCoords[combo]:
                boxIdxs = self.getAllBoxCoords((rr, rc))
                
                rowLine = {(rr, c) for c in range(9) if (rr, c) not in boxIdxs 
                           and self.getSet((rr, c)) & combo}
                colLine = {(r, rc) for r in range(9) if (r, rc) not in boxIdxs 
                           and self.getSet((r, rc)) & combo}
                
                if len(rowLine) != 1 or len(colLine) != 1: continue
                
                rowNode = next(iter(rowLine))
                colNode = next(iter(colLine))
                rowSet = self.getSet(rowNode) & combo
                colSet = self.getSet(colNode) & combo
                
                if len(rowSet) < 2 or len(colSet) < 2 or rowSet == colSet: continue
                
                valid = True
                for val in combo:
                    rowCheck = self.getAnyRowIdxs((rr, rc), {val}) - boxIdxs
                    colCheck = self.getAnyColIdxs((rr, rc), {val}) - boxIdxs
                    if rowCheck and rowCheck != {rowNode}: valid = False; break
                    if colCheck and colCheck != {colNode}: valid = False; break
                if not valid: continue
                
                group = [(rr, rc), rowNode, colNode]
                eNodes = {(eVal, node) for node in group 
                          for eVal in self.getSet(node) - combo
                          if eVal in self.layout[node[0]][node[1]].note}
                
                if eNodes and not uberPrune(current_node, ("Fireworks Triple", group, eNodes, None)):
                    baseCopy.updateNotesGX(eNodes)
                    if self.stuck(baseCopy): continue
                    diffNodes = self.puzzleDifference(baseCopy)
                    note = f"Fireworks Triple Pattern at root {rr,rc}, row node {rowNode}, col node {colNode}\nRemoving all non-combo values ({set(combo)}) from {diffNodes}"
                    baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Fireworks Triple", current_node, group)
                    newPuzzles.append(tempPuzzle)
    
        # Quadruple Fireworks
        doublesPatterns = []
        for combo in doublesCoords:
            for root in doublesCoords[combo]:
                boxIdxs = self.getAllBoxCoords(root)
                rr, rc = root
                
                rowLine = {(rr, c) for c in range(9) if (rr, c) not in boxIdxs 
                           and self.getSet((rr, c)) & combo}
                colLine = {(r, rc) for r in range(9) if (r, rc) not in boxIdxs 
                           and self.getSet((r, rc)) & combo}
                
                if len(rowLine) != 1 or len(colLine) != 1: continue
                
                rowNode = next(iter(rowLine))
                colNode = next(iter(colLine))
                rowSet = self.getSet(rowNode) & combo
                colSet = self.getSet(colNode) & combo
                
                if rowSet != combo or colSet != combo: continue
                
                valid = True
                for val in combo:
                    rowCheck = self.getAnyRowIdxs(root, {val}) - boxIdxs
                    colCheck = self.getAnyColIdxs(root, {val}) - boxIdxs
                    if rowCheck and rowCheck != {rowNode}: valid = False; break
                    if colCheck and colCheck != {colNode}: valid = False; break
                if not valid: continue
                
                doublesPatterns.append((combo, root, rowNode, colNode))
    
        patternsByNodes = {}
        for pattern in doublesPatterns:
            combo, root, rowNode, colNode = pattern
            patternsByNodes.setdefault((rowNode, colNode), []).append(pattern)
    
        for patternA in doublesPatterns:
            comboA, rootA, rowNodeA, colNodeA = patternA
            complementKey = (colNodeA, rowNodeA)
            if complementKey not in patternsByNodes: continue
            for patternB in patternsByNodes[complementKey]:
                comboB, rootB, rowNodeB, colNodeB = patternB
                if comboA == comboB or rootA == rootB: continue
                uberCombo = comboA | comboB
                group = [rootA, rootB, rowNodeA, rowNodeB]
                
                eNodes = set()
                for sharedNode in [rowNodeA, rowNodeB]:
                    eNodes |= {(eVal, sharedNode) for eVal in self.getSet(sharedNode) - uberCombo
                               if eVal in self.layout[sharedNode[0]][sharedNode[1]].note}
                eNodes |= {(eVal, rootA) for eVal in self.getSet(rootA) - comboA
                           if eVal in self.layout[rootA[0]][rootA[1]].note}
                eNodes |= {(eVal, rootB) for eVal in self.getSet(rootB) - comboB
                           if eVal in self.layout[rootB[0]][rootB[1]].note}
                
                if eNodes and not uberPrune(current_node, ("Fireworks Quadruple", group, eNodes, None)):
                    baseCopy.updateNotesGX(eNodes)
                    if self.stuck(baseCopy): continue
                    diffNodes = self.puzzleDifference(baseCopy)
                    note = f"Fireworks Quadruple Pattern\nCombo: {set(comboA)} Root: {rootA}, Row Node: {rowNodeA}, Col Node: {colNodeA}\nCombo: {set(comboB)} Root: {rootB}, Row Node: {rowNodeB}, Col Node: {colNodeB}\nRemoving {diffNodes}"
                    baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Fireworks Quadruple", current_node, group)
                    newPuzzles.append(tempPuzzle)
    
        return baseCopy, newPuzzles
    # def fireworks(self, tempcopy):
    #     for i in range(9):
    #         for j in range(9):
    #             if self.locked[i][j]: continue
    #             currentSet = self.getSet((i, j))
    #             for combo in itertools.combinations(currentSet, 3):
    #                 comboSet = set(combo)
    #                 rowNode, colNode = (-1, -1), (-1, -1)
    #                 rowCount, colCount = 0, 0
    #                 for idx in range(9):
    #                     if not self.inBox([(idx, j), (i, j)]) and not self.locked[idx][j]:
    #                         if len(self.getSet((idx, j)) & comboSet) >= 1:
    #                             rowNode = (idx, j)
    #                             rowCount += 1
    #                     if not self.inBox([(i, idx), (i, j)]) and not self.locked[i][idx]:
    #                         if len(self.getSet((i, idx)) & comboSet) >= 1:
    #                             colNode = (i, idx)
    #                             colCount += 1
    #                 if rowCount != 1 or colCount != 1: continue
    #                 if not len(self.getSet(rowNode) & comboSet) >= 2 or not len(self.getSet(colNode) & comboSet) >= 2: continue
    #                 self.updateNotesIgnoreDX([(i, j), rowNode, colNode], combo)
    #                 if not self.stuck(tempcopy):
    #                     return print(f"Triple Firework found {combo} exclusive to nodes {[(i, j), rowNode, colNode]}")
                        
    #             for baseCombo in itertools.combinations(currentSet, 2):
    #                 comboSet = set(combo)
    #                 rowNode, colNode = (-1, -1), (-1, -1)
    #                 rowCount, colCount = 0, 0
    #                 for idx in range(9):
    #                     if not self.inBox([(idx, j), (i, j)]) and not self.locked[idx][j]:
    #                         if len(self.getSet((idx, j)) & comboSet) >= 1:
    #                             rowNode = (idx, j)
    #                             rowCount += 1
    #                     if not self.inBox([(i, idx), (i, j)]) and not self.locked[i][idx]:
    #                         if len(self.getSet((i, idx)) & comboSet) >= 1:
    #                             colNode = (i, idx)
    #                             colCount += 1
    #                 if rowCount != 1 or colCount != 1: continue
    #                 if not len(self.getSet(rowNode) & comboSet) >= 2 or not len(self.getSet(colNode) & comboSet) >= 2: continue
    #                 self.updateNotesIgnoreDX([(i, j), rowNode, colNode], combo)
    #                 if not self.stuck(tempcopy):
    #                     return print(f"Triple Firework found {combo} exclusive to nodes {[(i, j), rowNode, colNode]}")
    # def fireworkUtil(self):
    #     tempCopy = copy.deepcopy(self)
    #     remaining = self.getRemaining()
    #     for combo in itertools.combinations(remaining, 3):
    #         self.tripleFirework(set(combo), tempCopy)
    #         if not self.stuck(tempCopy):
    #             return
    #     comboPairs = list(itertools.combinations(remaining, 2))
    #     comboPairDoubles = list(itertools.permutations(comboPairs, 2))
    #     for combo1, combo2 in comboPairDoubles:
    #         if len(set(combo1) & set(combo2)) > 0:
    #             continue
    #         self.quadFirework(set(combo1), set(combo2), tempCopy)
    #         if not self.stuck(tempCopy):
    #             return
    # def tripleFirework(self, combo, tempCopy):
    #     nonCombo = {1,2,3,4,5,6,7,8,9} - combo
    #     for i in range(9):
    #         for j in range(9):
    #             if self.layout[i][j].val != 0: continue
    #             tempSet = self.getSet((i, j))
    #             if not (combo <= tempSet): continue
    #             rowOffset, colOffset = self.getOffset(i), self.getOffset(j)
    #             inRow, inCol, outRow, outCol = set(), set(), dict(), dict()
    #             rowSet, colSet, outSet = set(), set(), set()
    #             badSet = False
    #             boxNodes = set((i, j))
    #             for tempRow in range(rowOffset, rowOffset + 3): boxNodes.add((tempRow, j))
    #             for tempCol in range(colOffset, colOffset + 3): boxNodes.add((i, tempCol))
    #             for tempVal in combo:
    #                 if len(self.getAnyRowIdxs([(i, j)], {val}) - boxNodes) != 1 or len(self.getAnyColIdxs([(i, j)], {val}) - boxNodes) !+ 1: badSet = True
    #             if badSet: continue
    #             for extra in range(9):
    #                 if not self.inBox([(i, j), (extra, j)]):
    #                     tempSet = self.getSet((extra, j))
    #                     if self.locked[extra][j]: colSet.add(self.layout[extra][j].val)
    #                     elif len(tempSet & combo) == 2
    #                         colSet |= self.getSet((extra, j))
    #                 if not self.inBox([(i, j), (i, extra)]): 
    #             for col in range(9):
    #                 tempSet = self.getSet((i, col))
    #                 if colOffset <= col < colOffset + 3: continue
    #                 if self.locked[i][col]:
    #                 elif len(tempSet & combo) >= 2: 
                        
    #             for col in range(9):
    #                 tempSet = self.getSet((i, col))
    #                 if colOffset <= col < colOffset + 3:
    #                     if col == j: continue
    #                     inCol = inCol.union(tempSet & combo)
    #                 elif len(tempSet & combo) > 0: outCol[col], colWing = tempSet & combo, (i, col)
    #             if len(outCol) != 1 or outCol[colWing] | inCol != combo: continue
    #             for row in range(9):
    #                 tempSet = self.getSet((row, j))
    #                 if rowOffset <= row < rowOffset + 3:
    #                     if row == i: continue
    #                     inRow = inRow.union(tempSet & combo)
    #                 else:
    #                     if len(tempSet & combo) > 0: outRow[row], rowWing = tempSet & combo, (row, j)
    #             if len(outRow) != 1 or outRow[rowWing] | inRow != combo: continue
    #             if len(outRow[rowWing]) < 3 and len(outCol[colWing]) < 3 and outRow[rowWing] == outCol[colWing]:  continue
    #             self.updateNotesDX([(i, j), rowWing, colWing], (self.getRemaining() - combo))
    #             if not self.stuck(tempCopy):
    #                 print(f"Triple Firework found locked combo {combo} in {(i, j)}, {rowWing}, & {colWing}\nRemoving non column values from these 3 nodes.")
    #                 # print(f"Combo: {combo} Root: {(i, j)}")
    #                 # print(f"colWing: {(i, colWing)}, inCol: {inCol}, outCol {outCol}")
    #                 # print(f"rowWing: {(rowWing, j)}, inRow: {inRow}, outRow {outRow}")
    #                 return
    
    # def quadFirework(self, combo1, combo2, tempCopy):
    #     for i in range(9):
    #         for j in range(9):
    #             if self.layout[i][j].val != 0:
    #                 continue
    #             tempSet = set(self.layout[i][j].note) - {0}
    #             if not (combo1 <= tempSet):
    #                 continue
    #             rowOffset1 = (i//3) * 3
    #             colOffset1 = (j//3) * 3
    #             inCol1 = set()
    #             outCol1 = dict()
    #             inRow1 = set()
    #             outRow1 = dict()
    #             for col in range(9):
    #                 tempSet = set(self.layout[i][col].note) - {0}
    #                 if colOffset1 <= col < colOffset1 + 3:
    #                     if col == j:
    #                         continue
    #                     inCol1 = inCol1.union(set(tempSet & combo1))
    #                 else:
    #                     if len(tempSet & combo1) == 2:
    #                         outCol1[col] = set(tempSet & combo1)
    #                         colWing = col
    #             if len(outCol1) != 1:
    #                 continue
    #             for row in range(9):
    #                 tempSet = set(self.layout[row][j].note) - {0}
    #                 if rowOffset1 <= row < rowOffset1 + 3:
    #                     if row == i:
    #                         continue
    #                     inRow1 = inRow1.union(set(tempSet & combo1))
    #                 else:
    #                     if len(tempSet & combo1) == 2:
    #                         outRow1[row] = set(tempSet & combo1)
    #                         rowWing = row
    #             if len(outRow1) != 1:
    #                 continue
    #             # first double firework found, now checking for other double firework
    #             tempSet = set(self.layout[rowWing][colWing].note) - {0}
    #             if not (combo2 <= tempSet):
    #                 continue
    #             rowOffset2 = (rowWing//3) * 3
    #             colOffset2 = (colWing//3) * 3
    #             inCol2 = set()
    #             outCol2 = dict()
    #             inRow2 = set()
    #             outRow2 = dict()
    #             for col in range(9):
    #                 tempSet = set(self.layout[rowWing][col].note) - {0}
    #                 if colOffset2 <= col < colOffset2 + 3:
    #                     if col == colWing:
    #                         continue
    #                     inCol2 = inCol2.union(set(tempSet & combo2))
    #                 else:
    #                     if len(tempSet & combo2) > 0:
    #                         outCol2[col] = set(tempSet & combo2)
    #                         colWingCheck = col
    #             if len(outCol2) != 1:
    #                 continue
    #             for row in range(9):
    #                 tempSet = set(self.layout[row][colWing].note) - {0}
    #                 if rowOffset2 <= row < rowOffset2 + 3:
    #                     if row == rowWing:
    #                         continue
    #                     inRow2 = inRow2.union(set(tempSet & combo2))
    #                 else:
    #                     if len(tempSet & combo2) > 0:
    #                         outRow2[row] = set(tempSet & combo2)
    #                         rowWingCheck = row
    #             if len(outRow2) != 1:
    #                 continue
    #             if (i, colWing) != (rowWingCheck, colWing) or (rowWing, j) != (rowWing, colWingCheck):
    #                 continue
    #             print(f"Combo1: {combo1} Root: {(i, j)}")
    #             print(f"colWing: {(i, colWing)}, inCol: {inCol1}, outCol {outCol1}")
    #             print(f"rowWing: {(rowWing, j)}, inRow: {inRow1}, outRow {outRow1}")
    #             print(f"Combo2: {combo2} Root: {(rowWing, colWing)}")
    #             print(f"colWing: {(rowWing, colWingCheck)}, inCol: {inCol2}, outCol {outCol2}")
    #             print(f"rowWing: {(rowWingCheck, colWing)}, inRow: {inRow2}, outRow {outRow2}")
    #             safeSet = combo1 | combo2
    #             for eVal in range(1, 10):
    #                 if eVal not in safeSet:
    #                     self.layout[i][colWing].note[eVal-1] = 0
    #                     self.layout[rowWing][j].note[eVal-1] = 0
    #                 if eVal not in combo1:
    #                     self.layout[i][j].note[eVal-1] = 0
    #                 if eVal not in combo2:
    #                     self.layout[rowWing][colWing].note[eVal-1] = 0
    #             if not self.stuck(tempCopy):
    #                 return
                
    # ********************************************************************************************************************
    def twinXYChains(self, baseCopy, current_node):
        newPuzzles = []
        allTwos = set(self.getAllIdxsOfLen(2))
        allThrees = set(self.getAllIdxsOfLen(3))
        allTwoOrThree = allTwos | allThrees
        rectangles = set()
    
        for root in allThrees:
            rootSet = self.getSet(root)
            rootRow, rootCol = root
            rowIdxs, colIdxs = [], []
    
            for r in range(9):
                if r == rootRow or self.locked[r][rootCol]: continue
                node = (r, rootCol)
                tempSet = self.getSet(node)
                if node in allTwoOrThree:
                    if len(rootSet & tempSet) >= 1:
                        rowIdxs.append(node)
            if not rowIdxs: continue
    
            for c in range(9):
                if c == rootCol or self.locked[rootRow][c]: continue
                node = (rootRow, c)
                tempSet = self.getSet(node)
                if node in allTwoOrThree:
                    if len(rootSet & tempSet) >= 1:
                        colIdxs.append(node)
            if not colIdxs: continue
    
            if len(colIdxs) >= 2:
                for c1, c2 in itertools.combinations(colIdxs, 2):
                    for rowNode in rowIdxs:
                        rectangles.add(frozenset([
                            root, rowNode,
                            (rootRow, c1[1]), (rowNode[0], c1[1]),
                            (rootRow, c2[1]), (rowNode[0], c2[1])
                        ]))
            if len(rowIdxs) >= 2:
                for r1, r2 in itertools.combinations(rowIdxs, 2):
                    for colNode in colIdxs:
                        rectangles.add(frozenset([
                            root, colNode,
                            (r1[0], rootCol), (r1[0], colNode[1]),
                            (r2[0], rootCol), (r2[0], colNode[1])
                        ]))
    
        for rectangle in rectangles:
            rectangle = sorted(rectangle)
            if any(self.locked[r][c] for (r, c) in rectangle): continue
    
            nodeSets = {node: self.getSet(node) for node in rectangle}
            allVals = set().union(*nodeSets.values())
            if len(allVals) != 6: continue
    
            # doing it the evil way, feel free to make better later
            valNodes = {val: [] for val in allVals}
            goodRectangle = True
            for node, s in nodeSets.items():
                for val in s:
                    valNodes[val].append(node)
            for val, nodes in valNodes.items():
                if not self.hasConnection(nodes):
                    goodRectangle = False
            if not goodRectangle: continue
    
            eNodes = set()
            for val, nodes in valNodes.items():
                if self.inRow(nodes):
                    eNodes |= {(val, idx) for idx in self.getAnyRowIdxs(nodes[0], {val}) - set(rectangle)}
                if self.inCol(nodes):
                    eNodes |= {(val, idx) for idx in self.getAnyColIdxs(nodes[0], {val}) - set(rectangle)}
    
            group = rectangle
            if eNodes and not uberPrune(current_node, ("Twin XY Chains", group, eNodes, None)):
                baseCopy.updateNotesGX(eNodes)
                if self.stuck(baseCopy): continue
                diffNodes = self.puzzleDifference(baseCopy)
                note = f"Twin XY Chains found rectangle {rectangle}\nRemoving {allVals} from rows & columns in common with rectangle."
                baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Twin XY Chains", current_node, group)
                newPuzzles.append(tempPuzzle)
    
        return baseCopy, newPuzzles
    # ********************************************************************************************************************
    def skLoops(self, baseCopy, current_node):
        newPuzzles = []
        loops = self.getSKLoopPattern()
        for tl, tr, bl, br in loops:
            valSet = set()
            for x, y in [tl, tr, bl, br]:
                valSet.add(self.layout[x][y].val)
            tlrIdxs, tlcIdxs = self.getSKLoopCornerIdxs(tl)
            trrIdxs, trcIdxs = self.getSKLoopCornerIdxs(tr)
            blrIdxs, blcIdxs = self.getSKLoopCornerIdxs(bl)
            brrIdxs, brcIdxs = self.getSKLoopCornerIdxs(br)
            if any(len(idxs) == 0 for idxs in [tlrIdxs, tlcIdxs, trrIdxs, trcIdxs, blrIdxs, blcIdxs, brrIdxs, brcIdxs]):
                continue
            
            groupSets = {
                'tlr': frozenset().union(*[self.getSet(idx) for idx in tlrIdxs]),
                'tlc': frozenset().union(*[self.getSet(idx) for idx in tlcIdxs]),
                'trr': frozenset().union(*[self.getSet(idx) for idx in trrIdxs]),
                'trc': frozenset().union(*[self.getSet(idx) for idx in trcIdxs]),
                'blr': frozenset().union(*[self.getSet(idx) for idx in blrIdxs]),
                'blc': frozenset().union(*[self.getSet(idx) for idx in blcIdxs]),
                'brr': frozenset().union(*[self.getSet(idx) for idx in brrIdxs]),
                'brc': frozenset().union(*[self.getSet(idx) for idx in brcIdxs]),
            }
    
            row1Set = set(range(1, 10))
            row2Set = set(range(1, 10))
            col1Set = set(range(1, 10))
            col2Set = set(range(1, 10))
            for idx in tlrIdxs + trrIdxs:
                row1Set &= self.getSet(idx)
            for idx in blrIdxs + brrIdxs:
                row2Set &= self.getSet(idx)
            for idx in tlcIdxs + blcIdxs:
                col1Set &= self.getSet(idx)
            for idx in trcIdxs + brcIdxs:
                col2Set &= self.getSet(idx)
            if not row1Set or not row2Set or not col1Set or not col2Set:
                continue
    
            boxSets = {
                'tlSet': (groupSets['tlr'] & groupSets['tlc']) - row1Set - col1Set,
                'trSet': (groupSets['trr'] & groupSets['trc']) - row1Set - col2Set,
                'blSet': (groupSets['blr'] & groupSets['blc']) - row2Set - col1Set,
                'brSet': (groupSets['brr'] & groupSets['brc']) - row2Set - col2Set,
            }
            if any(len(s) == 0 for s in boxSets.values()): continue
    
            remainders = {
                'tlr': groupSets['tlr'] - row1Set - boxSets['tlSet'],
                'tlc': groupSets['tlc'] - col1Set - boxSets['tlSet'],
                'trr': groupSets['trr'] - row1Set - boxSets['trSet'],
                'trc': groupSets['trc'] - col2Set - boxSets['trSet'],
                'blr': groupSets['blr'] - row2Set - boxSets['blSet'],
                'blc': groupSets['blc'] - col1Set - boxSets['blSet'],
                'brr': groupSets['brr'] - row2Set - boxSets['brSet'],
                'brc': groupSets['brc'] - col2Set - boxSets['brSet'],
            }
            if any(len(r) > 0 for r in remainders.values()): continue
    
            linkCount = (len(row1Set) + len(row2Set) + len(col1Set) + len(col2Set) +
                        len(boxSets['tlSet']) + len(boxSets['trSet']) +
                        len(boxSets['blSet']) + len(boxSets['brSet']))
            if linkCount > 16: continue
    
            group = [[tl, tr, bl, br],
                     [row1Set, row2Set, col1Set, col2Set],
                     [boxSets['tlSet'], boxSets['trSet'], boxSets['blSet'], boxSets['brSet']]]
    
            eNodesLine = []
            excludeRows = set(range(self.getOffset(tl[0]), self.getOffset(tl[0]) + 3)) | \
                         set(range(self.getOffset(bl[0]), self.getOffset(bl[0]) + 3))
            excludeCols = set(range(self.getOffset(tl[1]), self.getOffset(tl[1]) + 3)) | \
                         set(range(self.getOffset(tr[1]), self.getOffset(tr[1]) + 3))
            otherRows = [r for r in range(9) if r not in excludeRows]
            otherCols = [c for c in range(9) if c not in excludeCols]
            for row in otherRows:
                for val in col1Set:
                    if val in self.layout[row][tl[1]].note:
                        eNodesLine.append((val, (row, tl[1])))
                for val in col2Set:
                    if val in self.layout[row][tr[1]].note:
                        eNodesLine.append((val, (row, tr[1])))
            for col in otherCols:
                for val in row1Set:
                    if val in self.layout[tl[0]][col].note:
                        eNodesLine.append((val, (tl[0], col)))
                for val in row2Set:
                    if val in self.layout[bl[0]][col].note:
                        eNodesLine.append((val, (bl[0], col)))
    
            eNodesBox = []
            for eVals, corner, cornerIdxs in [
                (boxSets['tlSet'], tl, tlrIdxs + tlcIdxs),
                (boxSets['trSet'], tr, trrIdxs + trcIdxs),
                (boxSets['blSet'], bl, blrIdxs + blcIdxs),
                (boxSets['brSet'], br, brrIdxs + brcIdxs)
            ]:
                excludeBox = self.getAllBoxCoords(corner) - ({corner} | set(cornerIdxs))
                for r, c in excludeBox:
                    for val in eVals:
                        if val in self.layout[r][c].note:
                            eNodesBox.append((val, (r, c)))
    
            eNodes = set(eNodesLine + eNodesBox)
            if eNodes and not uberPrune(current_node, ("SK Loop", group, eNodes, None)):
                baseCopy.updateNotesGX(eNodes)
                if self.stuck(baseCopy): continue
                diffNodes = self.puzzleDifference(baseCopy)
                note = (f"SK Loop Pattern: {tl}, {tr}, {bl}, {br}\n"
                        f"Row1: {row1Set} | Row2: {row2Set} | Col1: {col1Set} | Col2: {col2Set}\n"
                        f"Removing {diffNodes}")
                baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "SK Loop", current_node, group)
                newPuzzles.append(tempPuzzle)
    
        return baseCopy, newPuzzles
    def getSKLoopCornerIdxs(self, idx):
        x, y = idx
        rowOffset, colOffset = self.getOffset(x), self.getOffset(y)
        rowIdxs, colIdxs = [], []
        for r in range(rowOffset, rowOffset + 3):
            if r == x or self.locked[r][y]: continue
            colIdxs.append((r, y))
        for c in range(colOffset, colOffset + 3):            
            if c == y or self.locked[x][c]: continue
            rowIdxs.append((x, c))
        return rowIdxs, colIdxs
    
    def getSKLoopPattern(self):
        completedRows = {i for i in range(9) if all(self.locked[i][c] for c in range(9))}
        completedCols = {j for j in range(9) if all(self.locked[r][j] for r in range(9))}
        completedBoxes = set()
        for rBox in range(0, 9, 3):
            for cBox in range(0, 9, 3):
                if all(self.locked[r][c] for r in range(rBox, rBox+3) for c in range(cBox, cBox+3)):
                    completedBoxes.add((rBox//3, cBox//3))
        
        candidates = []
        for i in range(9):
            if i in completedRows: continue
            for j in range(9):
                if j in completedCols: continue
                if (i//3, j//3) in completedBoxes: continue
                if self.locked[i][j]:
                    candidates.append((i, j))
        
        byRow = {}
        for r, c in candidates:
            byRow.setdefault(r, set()).add(c)
        
        patterns = []
        rows = sorted(byRow.keys())
        for idx1, r1 in enumerate(rows):
            for r2 in rows[idx1+1:]:
                sharedCols = byRow[r1] & byRow[r2]
                if len(sharedCols) < 2: continue
                for c1, c2 in itertools.combinations(sharedCols, 2):
                    boxes = {(r1//3, c1//3), (r1//3, c2//3), (r2//3, c1//3), (r2//3, c2//3)}
                    if len(boxes) != 4: continue
                    
                    # sort into top-left, top-right, bottom-left, bottom-right
                    minR, maxR = min(r1, r2), max(r1, r2)
                    minC, maxC = min(c1, c2), max(c1, c2)
                    pattern = ((minR, minC), (minR, maxC), (maxR, minC), (maxR, maxC))
                    patterns.append(pattern)
        
        # sort patterns by top-left, then top-right, then bottom-left, then bottom-right
        patterns.sort(key=lambda p: (p[0], p[1], p[2], p[3]))
        return patterns
    # def SKLoops(self):
    #     tempCopy = copy.deepcopy(self)
    #     for tl, tr, bl, br in self.getDiagonalSymSquares():
    #         coordSet = {tl, tr, bl, br}
    #         if any(self.layout[r][c].val == 0 for (r,c) in coordSet):
    #             continue
    #         hozVals = {(x, y): set() for (x,y) in coordSet}
    #         verVals = {(x, y): set() for (x,y) in coordSet}
    #         sHozCellVals = {(x,y): set() for (x,y) in coordSet}
    #         sVerCellVals = {(x,y): set() for (x,y) in coordSet}
    #         for x, y in coordSet:
    #             rowOffset = (x//3) * 3
    #             colOffset = (y//3) * 3
    #             checkCol = set()
    #             checkRow = set()
    #             filledCount = 0
    #             for col in range(colOffset, colOffset + 3):
    #                 if col == y: 
    #                     continue
    #                 tempSet = set(self.layout[x][col].note) - {0}
    #                 hozVals[(x, y)] |= tempSet
    #                 checkCol.add((x, col))
    #                 if len(tempSet) == 0:
    #                     filledCount += 1
    #             for row in range(rowOffset, rowOffset + 3):
    #                 if row == x:
    #                     continue
    #                 tempSet = set(self.layout[row][y].note) - {0}
    #                 verVals[(x, y)] |= tempSet
    #                 checkRow.add((row, y))
    #                 if len(tempSet) == 0:
    #                     filledCount += 1
    #             if filledCount < 2:
    #                 for val in hozVals[(x, y)]:
    #                     if all(val in (set(self.layout[a][b].note) - {0}) for a, b in checkCol) or not all(self.layout[a][b].val == 0 for a, b in coordSet):
    #                         sHozCellVals[(x, y)].add(val)
    #                 for val in verVals[(x, y)]:
    #                     if all(val in (set(self.layout[a][b].note) - {0}) for a, b in checkRow) or not all(self.layout[a][b].val == 0 for a, b in coordSet):
    #                         sVerCellVals[(x, y)].add(val)
    #             else:
    #                 break
    #         if filledCount > 1:
    #             continue
    #         # for node in coordSet:
    #         #     print(f"{node}:\n HozVals {hozVals[node]}. SHozVals {sHozCellVals[node]}.\nVerVals {verVals[node]} \n")
    #         linkCount = 0
    #         totalCount1 = 0 # blue
    #         totalCount2 = 0 # green
    #         boxStrongVals = {(a, b): set() for a, b in coordSet}
    #         sHozPairVals = {((a, b), (x, y)): set(sHozCellVals[(a, b)] & sHozCellVals[(x, y)]) for (a, b), (x, y) in itertools.combinations(coordSet, 2) if a == x}
    #         sVerPairVals = {((a, b), (x, y)): set(sVerCellVals[(a, b)] & sVerCellVals[(x, y)]) for (a, b), (x, y) in itertools.combinations(coordSet, 2) if b == y}
    #         flip = True
    #         for ((a, b), (x, y)), vals in sHozPairVals.items():
    #             if len(vals) > 0:
    #                 linkCount += 1
    #             if flip:
    #                 flip = False
    #                 totalCount1 += len(hozVals[x, y])
    #                 totalCount2 += len(hozVals[a, b])
    #             else:
    #                 flip = True
    #                 totalCount1 += len(hozVals[a, b])
    #                 totalCount2 += len(hozVals[x, y])
    #         for ((a, b), (x, y)), vals in sVerPairVals.items():
    #             if len(vals) > 0:
    #                 linkCount += 1
    #             if flip:
    #                 flip = False
    #                 totalCount1 += len(verVals[a, b])
    #                 totalCount2 += len(verVals[x, y])
    #             else:
    #                 flip = True
    #                 totalCount1 += len(verVals[x, y])
    #                 totalCount2 += len(verVals[a, b])
    #         for x in coordSet:
    #             if len(hozVals[x] & verVals[x]) > 1:
    #                 linkCount += 1
    #         # print(f"LinkCount: {linkCount}")
    #         # print(f"totalCount1: {totalCount1}")
    #         # print(f"totalCount2: {totalCount2}")
    #         if linkCount != 8 or totalCount1 > 16 or totalCount2 > 16:
    #             # print("Bad counts")
    #             continue
    #         # print(f"good cycle {coordSet}")
    #         # erasing time!
    #         for (a, b) in coordSet:
    #             eVals = hozVals[(a, b)] | verVals[(a, b)]
    #             for (x, y) in coordSet:
    #                 if ((a, b), (x, y)) in sHozPairVals:
    #                     eVals -= sHozPairVals[((a, b), (x, y))]
    #                 if ((x, y), (a, b)) in sHozPairVals:
    #                     eVals -= sHozPairVals[((x, y), (a, b))]
    #                 if ((a, b), (x, y)) in sVerPairVals:
    #                     eVals -= sVerPairVals[((a, b), (x, y))]
    #                 if ((x, y), (a, b)) in sVerPairVals:
    #                     eVals -= sVerPairVals[((x, y), (a, b))]
    #             rowOffset = (a//3) * 3
    #             colOffset = (b//3) * 3
    #             ignore = set()
    #             for row in range(rowOffset, rowOffset + 3):
    #                 ignore.add((row, b))
    #             for col in range(colOffset, colOffset + 3):
    #                 ignore.add((a, col))
    #             self.subUpdateNotes('box', list(ignore), eVals)
    #             # print(f"Node: {(a, b)}\nIgnore Nodes: {ignore}\nErasing {eVals}\n")
    #         for (a, b), (x, y) in sHozPairVals:
    #             if a != x:
    #                 continue
    #             ignore = set()
    #             colOffset1 = (b//3) * 3
    #             colOffset2 = (y//3) * 3
    #             for col in range(9):
    #                 if colOffset1 <= col < colOffset1 + 3 or colOffset2 <= col < colOffset2 + 3:
    #                     ignore.add((a, col))
    #             eVals = set(hozVals[(a, b)] & hozVals[(x, y)])
    #             self.subUpdateNotes('row', list(ignore), sHozPairVals[((a, b), (x, y))])
    #             # print(f"Nodes: {(a, b), (x, y)}\nIgnore Nodes: {ignore}\nErasing {eVals}\n")
    #         for (a, b), (x, y) in sVerPairVals:
    #             if b != y:
    #                 continue
    #             ignore = set()
    #             rowOffset1 = (a//3) * 3
    #             rowOffset2 = (x//3) * 3
    #             for row in range(9):
    #                 if rowOffset1 <= row < rowOffset1 + 3 or rowOffset2 <= row < rowOffset2 + 3:
    #                     ignore.add((row, b))
    #             self.subUpdateNotes('col', list(ignore), sVerPairVals[((a, b), (x, y))])
    #             # print(f"Nodes: {(a, b), (x, y)}\nIgnore Nodes: {ignore}\nErasing {eVals}\n")
    #         if not self.stuck(tempCopy):
    #             print(f"Found SK loop {coordSet}")
    #             return
                
    # def getDiagonalSymSquares(self):
    #     squares = []
    #     fourCorners = {(0, 0), (0, 2), (2, 0), (2, 2)}
    #     for r1 in range(9):
    #         for r2 in range(r1 + 1, 9):
    #             for c1 in range(9):
    #                 for c2 in range(c1 + 1, 9):
    #                     TL = (r1, c1)
    #                     TR = (r1, c2)
    #                     BL = (r2, c1)
    #                     BR = (r2, c2)
    #                     if (self.layout[r1][c1].val == 0 or
    #                         self.layout[r1][c2].val == 0 or
    #                         self.layout[r2][c1].val == 0 or
    #                         self.layout[r2][c2].val == 0):
    #                         continue
    #                     boxes = {
    #                         (r1 // 3, c1 // 3),
    #                         (r1 // 3, c2 // 3),
    #                         (r2 // 3, c1 // 3),
    #                         (r2 // 3, c2 // 3)
    #                     }
    #                     if len(boxes) != 4:
    #                         continue
    #                     rel_pos = [
    #                         (r1 % 3) * 3 + (c1 % 3),
    #                         (r1 % 3) * 3 + (c2 % 3),
    #                         (r2 % 3) * 3 + (c1 % 3),
    #                         (r2 % 3) * 3 + (c2 % 3)
    #                     ]
    #                     if len(set(rel_pos)) == 1:
    #                         squares.append([TL, TR, BL, BR])
    #                         continue
    #                     normalized = {(r - ((r//3) * 3), c - ((c//3) * 3)) for r, c in [TL, TR, BL, BR]}
    #                     if len(normalized & fourCorners) == 4:
    #                         squares.append([TL, TR, BL, BR])
    #                         continue
    #     return squares
    # ********************************************************************************************************************

    def extUniqueRectangles(self, baseCopy, current_node):
        newPuzzles = []
        rowSets, colSets = set(), set()
        noteGrid = [[self.getSet((r, c)) for c in range(9)] for r in range(9)]
        for comboLen in range(2, 4):
            for combo in itertools.combinations(self.getRemaining(), comboLen):
                comboSet = set(combo)
                for row in range(9):
                    allCols = [c for c in range(9) if noteGrid[row][c] <= comboSet and not self.locked[row][c]]
                    for c1, c2 in itertools.combinations(allCols, 2):
                        if self.inBox([(row, c1), (row, c2)]) and (noteGrid[row][c1] == comboSet or noteGrid[row][c2] == comboSet):
                            rowSets.add((combo, row, c1, c2))
                for col in range(9):
                    allRows = [r for r in range(9) if noteGrid[r][col] <= comboSet and not self.locked[r][col]]
                    for r1, r2 in itertools.combinations(allRows, 2):
                        if self.inBox([(r1, col), (r2, col)]) and (noteGrid[r1][col] == comboSet or noteGrid[r2][col] == comboSet):
                            colSets.add((combo, col, r1, r2))
    
        # Rows
        for rs1, rs2 in itertools.combinations(rowSets, 2):
            combo1, r1, c11, c12 = rs1
            n1, n2 = (r1, c11), (r1, c12)
            comboSet1 = set(combo1)
            r1Offset = self.getOffset(r1)
    
            combo2, r2, c21, c22 = rs2
            n3, n4 = (r2, c21), (r2, c22)
            comboSet2 = set(combo2)
            r2Offset = self.getOffset(r2)
    
            comboSet = comboSet1 | comboSet2
    
            if len(comboSet) != 3 or self.inBox([n1, n3]) or c11 != c21 or c12 != c22: continue
    
            rows = [x for x in range(9) if x not in range(r1Offset, r1Offset + 3) and x not in range(r2Offset, r2Offset + 3)]
            c1, c2 = c11, c12
            for row in rows:
                if self.locked[row][c1] or self.locked[row][c2]: continue
                targetNode1, targetVal2 = None, None
                n5, n6 = (row, c1), (row, c2)
                n5Set, n6Set = noteGrid[row][c1], noteGrid[row][c2]
    
                # Type 1 Row
                if n5Set <= comboSet and not (n6Set <= comboSet) and len(n6Set & comboSet) != 0:
                    friendlyNode, targetNode1 = n5, n6
                elif n6Set <= comboSet and not (n5Set <= comboSet) and len(n5Set & comboSet) != 0:
                    friendlyNode, targetNode1 = n6, n5
                if targetNode1:
                    eNodes = {(eVal, targetNode1) for eVal in comboSet if eVal in noteGrid[targetNode1[0]][targetNode1[1]]}
                    group = [n1, n2, n3, n4, friendlyNode]
                    if eNodes and not uberPrune(current_node, ("Extended Rectangles Row Type 1", group, eNodes, None)):
                        baseCopy.updateNotesGX(eNodes)
                        if self.stuck(baseCopy): continue
                        diffNodes = self.puzzleDifference(baseCopy)
                        note = f"Extended Rectangles Row Type 1 found group {comboSet}\nAt nodes {n1, n2, n3, n4} and FriendlyNode{friendlyNode}\nRemoving {eNodes}"
                        baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Extended Rectangles Row Type 1", current_node, group)
                        newPuzzles.append(tempPuzzle)
                    targetNode1 = None
    
                # Type 2 Row
                if len(n5Set) == 4 and len(n5Set & n6Set) == 4 and comboSet == comboSet & n5Set:
                    targetVal2 = (n5Set - comboSet).pop()
                    checkNodes = (self.getAllBoxCoords(n5) | self.getAllRowCoords(n5)) - {n5, n6}
                    eNodes = {(targetVal2, (r, c)) for r, c in checkNodes if targetVal2 in noteGrid[r][c]}
                    group = [n1, n2, n3, n4, n5, n6]
                    if eNodes and not uberPrune(current_node, ("Extended Rectangles Row Type 2", group, eNodes, None)):
                        baseCopy.updateNotesGX(eNodes)
                        if self.stuck(baseCopy): continue
                        diffNodes = self.puzzleDifference(baseCopy)
                        note = f"Extended Rectangles Row Type 2 found group {comboSet}\nAt nodes {n1, n2, n3, n4}\nFound Roof Nodes {n5, n6} containing {n5Set}\nRemoving {targetVal2} from Roof Box & Row"
                        baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Extended Rectangles Row Type 2", current_node, group)
                        newPuzzles.append(tempPuzzle)
                    targetVal2 = None
    
                if len(comboSet1) != 2 or len(comboSet2) != 2: continue
                common = (comboSet1 & comboSet2).pop()
                seeking = comboSet - {common}
                if len(n5Set) == len(n6Set) == 3 and (n5Set & n6Set) == seeking:
                    dangerVal = None
                    checkNodes = (self.getAllBoxCoords(n5) | self.getAllRowCoords(n5)) - {n5, n6}
                    for val in seeking:
                        if not any(val in noteGrid[r][c] for r, c in checkNodes):
                            dangerVal = val
                    if dangerVal:
                        safeVal = (seeking - {dangerVal}).pop()
                        eNodes = {(safeVal, (r, c)) for r, c in [n5, n6]}
                        group = [n1, n2, n3, n4, n5, n6]
                        if eNodes and not uberPrune(current_node, ("Extended Rectangles Row Type 4", group, eNodes, None)):
                            baseCopy.updateNotesGX(eNodes)
                            if self.stuck(baseCopy): continue
                            diffNodes = self.puzzleDifference(baseCopy)
                            note = f"Extended Rectangles Row Type 4 found group {comboSet}\nAt nodes {n1, n2, n3, n4}\nFound Roof Nodes {n5, n6} containing {n5Set} & {n6Set}\nRemoving {safeVal} from Roof"
                            baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Extended Rectangles Row Type 4", current_node, group)
                            newPuzzles.append(tempPuzzle)
    
        # Columns
        for cs1, cs2 in itertools.combinations(colSets, 2):
            combo1, c1, r11, r12 = cs1
            n1, n2 = (r11, c1), (r12, c1)
            comboSet1 = set(combo1)
            c1Offset = self.getOffset(c1)
    
            combo2, c2, r21, r22 = cs2
            n3, n4 = (r21, c2), (r22, c2)
            comboSet2 = set(combo2)
            c2Offset = self.getOffset(c2)
    
            comboSet = comboSet1 | comboSet2
    
            if len(comboSet) != 3 or self.inBox([n1, n3]) or r11 != r21 or r12 != r22: continue
    
            cols = [x for x in range(9) if x not in range(c1Offset, c1Offset + 3) and x not in range(c2Offset, c2Offset + 3)]
            r1, r2 = r11, r12
            for col in cols:
                if self.locked[r1][col] or self.locked[r2][col]: continue
                targetNode1, targetVal2 = None, None
                n5, n6 = (r1, col), (r2, col)
                n5Set, n6Set = noteGrid[r1][col], noteGrid[r2][col]
    
                # Type 1 Col
                if n5Set <= comboSet and not (n6Set <= comboSet) and len(n6Set & comboSet) != 0:
                    friendlyNode, targetNode1 = n5, n6
                elif n6Set <= comboSet and not (n5Set <= comboSet) and len(n5Set & comboSet) != 0:
                    friendlyNode, targetNode1 = n6, n5
                if targetNode1:
                    eNodes = {(eVal, targetNode1) for eVal in comboSet if eVal in noteGrid[targetNode1[0]][targetNode1[1]]}
                    group = [n1, n2, n3, n4, friendlyNode]
                    if eNodes and not uberPrune(current_node, ("Extended Rectangles Col Type 1", group, eNodes, None)):
                        baseCopy.updateNotesGX(eNodes)
                        if self.stuck(baseCopy): continue
                        diffNodes = self.puzzleDifference(baseCopy)
                        note = f"Extended Rectangles Col Type 1 found group {comboSet}\nAt nodes {n1, n2, n3, n4} and FriendlyNode{friendlyNode}\nRemoving {eNodes}"
                        baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Extended Rectangles Col Type 1", current_node, group)
                        newPuzzles.append(tempPuzzle)
                    targetNode1 = None
    
                # Type 2 Col
                if len(n5Set) == 4 and len(n5Set & n6Set) == 4 and comboSet == comboSet & n5Set:
                    targetVal2 = (n5Set - comboSet).pop()
                    checkNodes = (self.getAllBoxCoords(n5) | self.getAllColCoords(n5)) - {n5, n6}
                    eNodes = {(targetVal2, (r, c)) for r, c in checkNodes if targetVal2 in noteGrid[r][c]}
                    group = [n1, n2, n3, n4, n5, n6]
                    if eNodes and not uberPrune(current_node, ("Extended Rectangles Col Type 2", group, eNodes, None)):
                        baseCopy.updateNotesGX(eNodes)
                        if self.stuck(baseCopy): continue
                        diffNodes = self.puzzleDifference(baseCopy)
                        note = f"Extended Rectangles Col Type 2 found group {comboSet}\nAt nodes {n1, n2, n3, n4}\nFound Roof Nodes {n5, n6} containing {n5Set}\nRemoving {targetVal2} from Roof Box & Col"
                        baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Extended Rectangles Col Type 2", current_node, group)
                        newPuzzles.append(tempPuzzle)
                    targetVal2 = None
    
                # Type 4 Col
                if len(comboSet1) != 2 or len(comboSet2) != 2: continue
                common = (comboSet1 & comboSet2).pop()
                seeking = comboSet - {common}
                if len(n5Set) == len(n6Set) == 3 and (n5Set & n6Set) == seeking:
                    dangerVal = None
                    checkNodes = (self.getAllBoxCoords(n5) | self.getAllColCoords(n5)) - {n5, n6}
                    for val in seeking:
                        if not any(val in noteGrid[r][c] for r, c in checkNodes):
                            dangerVal = val
                    if dangerVal:
                        safeVal = (seeking - {dangerVal}).pop()
                        eNodes = {(safeVal, (r, c)) for r, c in [n5, n6]}
                        group = [n1, n2, n3, n4, n5, n6]
                        if eNodes and not uberPrune(current_node, ("Extended Rectangles Col Type 4", group, eNodes, None)):
                            baseCopy.updateNotesGX(eNodes)
                            if self.stuck(baseCopy): continue
                            diffNodes = self.puzzleDifference(baseCopy)
                            note = f"Extended Rectangles Col Type 4 found group {comboSet}\nAt nodes {n1, n2, n3, n4}\nFound Roof Nodes {n5, n6} containing {n5Set} & {n6Set}\nRemoving {safeVal} from Roof"
                            baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Extended Rectangles Col Type 4", current_node, group)
                            newPuzzles.append(tempPuzzle)
    
        return baseCopy, newPuzzles
    
    # def extUniqueRectangles(self, baseCopy, current_node):
    #     newPuzzles = []
        
    #     def processOrientation(flip):
    #         nonlocal baseCopy
            
    #         def coord(a, b):
    #             return (b, a) if flip else (a, b)
    #         def getSet(r, c):
    #             return self.getSet(coord(r, c))
    #         def inBox(pairs):
    #             return self.inBox([coord(r, c) for r, c in pairs])
            
    #         # build pairs: (primary_idx, sec1, sec2) where primary is row (or col if flip)
    #         # pair nodes are in same box, both contain at least 2 combo values
    #         pairs = []
    #         for primary in range(9):
    #             matching = [s for s in range(9) 
    #                        if len(getSet(primary, s) & combo) >= 2
    #                        and not self.locked[coord(primary, s)[0]][coord(primary, s)[1]]]
    #             for s1, s2 in itertools.combinations(matching, 2):
    #                 if not inBox([(primary, s1), (primary, s2)]): continue
    #                 set1 = getSet(primary, s1)
    #                 set2 = getSet(primary, s2)
    #                 # union must contain at least 2 combo values
    #                 if len((set1 | set2) & combo) < 2: continue
    #                 pairs.append((primary, s1, s2, set1, set2))
            
    #         # group pairs by their secondary index pair for fast lookup
    #         pairsBySecondary = {}
    #         for p in pairs:
    #             primary, s1, s2, set1, set2 = p
    #             key = (min(s1, s2), max(s1, s2))
    #             pairsBySecondary.setdefault(key, []).append(p)
            
    #         # find triples of pairs sharing the same 2 secondary indices
    #         # across 3 different box-primaries
    #         for (s1, s2), samePairs in pairsBySecondary.items():
    #             if len(samePairs) < 3: continue
    #             for p1, p2, p3 in itertools.combinations(samePairs, 3):
    #                 r1, _, _, set1a, set1b = p1
    #                 r2, _, _, set2a, set2b = p2
    #                 r3, _, _, set3a, set3b = p3
    #                 # must be in 3 different box-primaries
    #                 if len({r1//3, r2//3, r3//3}) != 3: continue
    #                 # combo must be covered by union of all pairs
    #                 if not (combo <= (set1a | set1b | set2a | set2b | set3a | set3b)): continue
                    
    #                 n1, n2 = coord(r1, s1), coord(r1, s2)
    #                 n3, n4 = coord(r2, s1), coord(r2, s2)
    #                 n5, n6 = coord(r3, s1), coord(r3, s2)
    #                 group = [n1, n2, n3, n4, n5, n6]
                    
    #                 # determine which nodes have extra values beyond combo
    #                 extras = {node: self.getSet(node) - combo for node in group}
    #                 eCells = [node for node, extra in extras.items() if extra]
                    
    #                 # Type 1: exactly 1 problem node
    #                 if len(eCells) == 1:
    #                     evilNode = eCells[0]
    #                     eNodes = {(v, evilNode) for v in combo 
    #                              if v in self.layout[evilNode[0]][evilNode[1]].note}
    #                     if eNodes and not uberPrune(current_node, (f"Extended Rectangles {'Col' if flip else 'Row'} 1", group, eNodes, None)):
    #                         baseCopy.updateNotesGX(eNodes)
    #                         if self.stuck(baseCopy): continue
    #                         diffNodes = self.puzzleDifference(baseCopy)
    #                         note = f"Extended Rectangles {'Col' if flip else 'Row'} Type 1\nGroup: {group}\nRemoving {combo} from {evilNode}: {diffNodes}"
    #                         baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, f"Extended Rectangles {'Col' if flip else 'Row'} 1", current_node, group)
    #                         newPuzzles.append(tempPuzzle)
                    
    #                 # Type 2: exactly 2 problem nodes in same pair, same extra value
    #                 elif len(eCells) == 2:
    #                     ec1, ec2 = eCells
    #                     extra1, extra2 = extras[ec1], extras[ec2]
    #                     # must be in same pair (same primary index)
    #                     if ec1[0] != ec2[0] if not flip else ec1[1] != ec2[1]: continue
    #                     if extra1 != extra2 or len(extra1) != 1: continue
    #                     eVal = next(iter(extra1))
    #                     eNodes = set()
    #                     # erase from box and row/col
    #                     boxCells = self.getAllBoxCoords(ec1) - {ec1, ec2}
    #                     for r, c in boxCells:
    #                         if eVal in self.layout[r][c].note:
    #                             eNodes.add((eVal, (r, c)))
    #                     if flip:
    #                         for r in range(9):
    #                             if (r, ec1[1]) not in [ec1, ec2] and eVal in self.layout[r][ec1[1]].note:
    #                                 eNodes.add((eVal, (r, ec1[1])))
    #                             if (r, ec2[1]) not in [ec1, ec2] and eVal in self.layout[r][ec2[1]].note:
    #                                 eNodes.add((eVal, (r, ec2[1])))
    #                     else:
    #                         for c in range(9):
    #                             if (ec1[0], c) not in [ec1, ec2] and eVal in self.layout[ec1[0]][c].note:
    #                                 eNodes.add((eVal, (ec1[0], c)))
    #                     if eNodes and not uberPrune(current_node, (f"Extended Rectangles {'Col' if flip else 'Row'} 2", group, eNodes, None)):
    #                         baseCopy.updateNotesGX(eNodes)
    #                         if self.stuck(baseCopy): continue
    #                         diffNodes = self.puzzleDifference(baseCopy)
    #                         note = f"Extended Rectangles {'Col' if flip else 'Row'} Type 2\nGroup: {group}\nRemoving {eVal} from {diffNodes}"
    #                         baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, f"Extended Rectangles {'Col' if flip else 'Row'} 2", current_node, group)
    #                         newPuzzles.append(tempPuzzle)
    
    #                 # Type 4: 2 problem nodes in same pair, different extra values
    #                 elif len(eCells) == 2:
    #                     ec1, ec2 = eCells
    #                     extra1, extra2 = extras[ec1], extras[ec2]
    #                     if ec1[0] != ec2[0] if not flip else ec1[1] != ec2[1]: continue
    #                     if extra1 == extra2 or len(extra1) != 1 or len(extra2) != 1: continue
    #                     goalSet = combo - (self.getSet(ec1) & self.getSet(ec2) & combo)
    #                     eVal = None
    #                     for val in goalSet:
    #                         if flip:
    #                             if self.singleRowCheck([ec1, coord(r2, s1 if ec1 == coord(r3,s1) else s2)], {val}):
    #                                 continue
    #                         else:
    #                             if self.singleColCheck([ec1, coord(r2, s1 if ec1 == coord(r3,s1) else s2)], {val}):
    #                                 continue
    #                         eVal = val
    #                         break
    #                     if eVal is None: continue
    #                     eNodes = {(eVal, ec1), (eVal, ec2)}
    #                     eNodes = {(v, n) for v, n in eNodes if v in self.layout[n[0]][n[1]].note}
    #                     if eNodes and not uberPrune(current_node, (f"Extended Rectangles {'Col' if flip else 'Row'} 4", group, eNodes, None)):
    #                         baseCopy.updateNotesGX(eNodes)
    #                         if self.stuck(baseCopy): continue
    #                         diffNodes = self.puzzleDifference(baseCopy)
    #                         note = f"Extended Rectangles {'Col' if flip else 'Row'} Type 4\nGroup: {group}\nRemoving {eVal} from {diffNodes}"
    #                         baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, f"Extended Rectangles {'Col' if flip else 'Row'} 4", current_node, group)
    #                         newPuzzles.append(tempPuzzle)
        
    #     for combo in itertools.combinations(self.getRemaining(), 3):
    #         combo = set(combo)
    #         processOrientation(False)
    #         processOrientation(True)
    #     return baseCopy, newPuzzles
    # def extUniqueRectanglesUtil(self):
    #     tempCopy = copy.deepcopy(self)
    #     remaining = self.getRemaining()
    #     for combo in itertools.combinations(self.getRemaining(), 3):
    #         self.extUniqueRectangles(set(combo), tempCopy)
    #         if not self.stuck(tempCopy):
    #             return
    # def extUniqueRectangles(self, combo, tempCopy):
    #     rowSets = set()
    #     colSets = set()
    #     for row in range(9):
    #         matchingCols = [c for c in range(9) if set(self.layout[row][c].note) - {0} == combo or len((set(self.layout[row][c].note) - {0}) & combo) == 2]
    #         for c1, c2 in itertools.combinations(matchingCols, 2):
    #             tempSet1 = set(self.layout[row][c1].note) - {0}
    #             tempSet2 = set(self.layout[row][c2].note) - {0}
    #             if len(tempSet1 | tempSet2) > 0 and tempSet1 == tempSet2 and self.inBox([(row, c1), (row, c2)]):
    #                 pair = frozenset(((row, c1), (row, c2)))
    #                 rowSets.add(pair)
    #     for col in range(9):
    #         matchingRows = [r for r in range(9) if set(self.layout[r][col].note) - {0} == combo or len((set(self.layout[r][col].note) - {0}) & combo) == 2]
    #         for r1, r2 in itertools.combinations(matchingRows, 2):
    #             tempSet1 = set(self.layout[r1][col].note) - {0}
    #             tempSet2 = set(self.layout[r2][col].note) - {0}
    #             if len(tempSet1 | tempSet2) > 0 and tempSet1 == tempSet2 and self.inBox([(r1, col), (r2, col)]):
    #                 pair = frozenset(((r1, col), (r2, col)))
    #                 colSets.add(pair)
                    
    #     for ((a, b), (x, y)) in rowSets:
    #         # print(f"{combo}: {((a, b), (x, y))}")
    #         tempSet1 = set(self.layout[a][b].note) - {0}
    #         tempSet2 = set(self.layout[x][y].note) - {0}
    #         rowOffset1 = (a//3) * 3 
    #         for row2 in range(9):
    #             if rowOffset1 <= row2 < rowOffset1 + 3:
    #                 continue
    #             tempSet3 = set(self.layout[row2][b].note) - {0}
    #             tempSet4 = set(self.layout[row2][y].note) - {0}
    #             if len(tempSet3 & tempSet4 & combo) < 2:
    #                 continue
    #             rowOffset2 = (row2//3) * 3 
    #             for row3 in range(9):
    #                 if rowOffset1 <= row3 < rowOffset1 + 3 or rowOffset2 <= row3 < rowOffset2 + 3:
    #                     continue
    #                 tempSet5 = set(self.layout[row3][b].note) - {0}
    #                 tempSet6 = set(self.layout[row3][y].note) - {0}
    #                 if len(tempSet5 & tempSet6 & combo) < 2:
    #                     continue
    #                 if combo <= (tempSet1 & tempSet2) | (tempSet3 & tempSet4) | (tempSet5 & tempSet6):
    #                     goodGroup = [(a, b), (x, y), (row2, b), (row2, y), (row3, b), (row3, y)]
    #                     getAlters = {(c, d): set(self.layout[c][d].note) - {0} - combo for c, d in goodGroup}
    #                     eCells = []
    #                     for (c, d), vals in getAlters.items():
    #                         if len(vals) > 0:
    #                             eCells.append((c, d))
    #                     if len(eCells) == 1:
    #                         ex1, ey1 = eCells[0]
    #                         for val in combo:
    #                             self.layout[ex1][ey1].note[val-1] = 0
    #                         if not self.stuck(tempCopy):
    #                             print(goodGroup)
    #                             print(f"Extended Rectangles Row Type 1 removed {combo} from {(ex1, ey1)}")
    #                             return
                            
    #     for ((a, b), (x, y)) in colSets:
    #         # print(f"{combo}: {((a, b), (x, y))}")
    #         tempSet1 = set(self.layout[a][b].note) - {0}
    #         tempSet2 = set(self.layout[x][y].note) - {0}
    #         colOffset1 = (b//3) * 3
    #         for col2 in range(9):
    #             if colOffset1 <= col2 < colOffset1 + 3:
    #                 continue
    #             tempSet3 = set(self.layout[a][col2].note) - {0}
    #             tempSet4 = set(self.layout[x][col2].note) - {0}
    #             if len(tempSet3 & tempSet4 & combo) < 2:
    #                 continue
    #             colOffset2 = (col2//3) * 3 
    #             for col3 in range(9):
    #                 if colOffset1 <= col3 < colOffset1 + 3 or colOffset2 <= col3 < colOffset2 + 3:
    #                     continue
    #                 tempSet5 = set(self.layout[a][col3].note) - {0}
    #                 tempSet6 = set(self.layout[x][col3].note) - {0}
    #                 if len(tempSet5 & tempSet6 & combo) < 2:
    #                     continue
    #                 if combo <= (tempSet1 & tempSet2) | (tempSet3 & tempSet4) | (tempSet5 & tempSet6):
    #                     goodGroup = [(a, b), (x, y), (a, col2), (x, col2), (a, col3), (x, col3)]
    #                     getAlters = {(c, d): set(self.layout[c][d].note) - {0} - combo for c, d in goodGroup}
    #                     eCells = []
    #                     for (c, d), vals in getAlters.items():
    #                         if len(vals) > 0:
    #                             eCells.append((c, d))
    #                     if len(eCells) == 1:
    #                         ex1, ey1 = eCells[0]
    #                         for val in combo:
    #                             self.layout[ex1][ey1].note[val-1] = 0
    #                         if not self.stuck(tempCopy):
    #                             print(goodGroup)
    #                             print(f"Extended Rectangles Row Type 1 removed {combo} from {(ex1, ey1)}")
    #                             return

    #     for ((a, b), (x, y)) in rowSets:
    #         # print(f"{combo}: {((a, b), (x, y))}")
    #         tempSet1 = set(self.layout[a][b].note) - {0}
    #         tempSet2 = set(self.layout[x][y].note) - {0}
    #         if len(tempSet1 & tempSet2 & combo) != 3 or tempSet1 != tempSet2 or len(tempSet1) != 3:
    #             continue
    #         rowOffset1 = (a//3) * 3 
    #         for row2 in range(9):
    #             if rowOffset1 <= row2 < rowOffset1 + 3:
    #                 continue
    #             tempSet3 = set(self.layout[row2][b].note) - {0}
    #             tempSet4 = set(self.layout[row2][y].note) - {0}
    #             if len(tempSet3 & tempSet4 & combo) < 2 or not (combo <= tempSet1 | tempSet2 | tempSet3 | tempSet4):
    #                 continue
    #             rowOffset2 = (row2//3) * 3
    #             for row3 in range(9):
    #                 if rowOffset1 <= row3 < rowOffset1 + 3 or rowOffset2 <= row3 < rowOffset2 + 3:
    #                     continue
    #                 tempSet5 = set(self.layout[row3][b].note) - {0}
    #                 tempSet6 = set(self.layout[row3][y].note) - {0}
    #                 if tempSet5 != tempSet6 or len(tempSet5 & tempSet6) != 4 or not (combo <= tempSet5 | tempSet6):
    #                     continue
    #                 eVal = (tempSet5 - combo).pop()
    #                 ignoreCells = [(row3, b), (row3, y)]
    #                 self.subUpdateNotes('box', ignoreCells, {eVal})
    #                 self.subUpdateNotes('row', ignoreCells, {eVal})
    #                 if not self.stuck(tempCopy):
    #                     goodGroup = [(a, b), (x, y), (row2, b), (row2, y), (row3, b), (row3, y)]
    #                     print(goodGroup)
    #                     print(f"Extended Rectangles Row Type 2 removed {eVal} from box and row with {ignoreCells}")
    #                     return
                        
    #     for ((a, b), (x, y)) in colSets:
    #         # print(f"{combo}: {((a, b), (x, y))}")
    #         tempSet1 = set(self.layout[a][b].note) - {0}
    #         tempSet2 = set(self.layout[x][y].note) - {0}
    #         if len(tempSet1 & tempSet2 & combo) != 3 or tempSet1 != tempSet2 or len(tempSet1) != 3:
    #             continue
    #         colOffset1 = (b//3) * 3 
    #         for col2 in range(9):
    #             if colOffset1 <= col2 < colOffset1 + 3:
    #                 continue
    #             tempSet3 = set(self.layout[a][col2].note) - {0}
    #             tempSet4 = set(self.layout[x][col2].note) - {0}
    #             if len(tempSet3 & tempSet4 & combo) < 2 or not (combo <= tempSet1 | tempSet2 | tempSet3 | tempSet4):
    #                 continue
    #             colOffset2 = (col2//3) * 3
    #             for col3 in range(9):
    #                 if colOffset1 <= col3 < colOffset1 + 3 or colOffset2 <= col3 < colOffset2 + 3:
    #                     continue
    #                 tempSet5 = set(self.layout[a][col3].note) - {0}
    #                 tempSet6 = set(self.layout[x][col3].note) - {0}
    #                 if tempSet5 != tempSet6 or len(tempSet5 & tempSet6) != 4 or not (combo <= tempSet5 | tempSet6):
    #                     continue
    #                 eVal = (tempSet5 - combo).pop()
    #                 ignoreCells = [(a, col3), (x, col3)]
    #                 self.subUpdateNotes('box', ignoreCells, {eVal})
    #                 self.subUpdateNotes('row', ignoreCells, {eVal})
    #                 if not self.stuck(tempCopy):
    #                     goodGroup = [(a, b), (x, y), (a, col2), (x, col2), (a, col3), (x, col3)]
    #                     print(goodGroup)
    #                     print(f"Extended Rectangles Col Type 2 removed {eVal} from box and col with {ignoreCells}")
    #                     return

    #     for ((a, b), (x, y)) in rowSets:
    #         # print(f"{combo}: {((a, b), (x, y))}")
    #         tempSet1 = set(self.layout[a][b].note) - {0}
    #         tempSet2 = set(self.layout[x][y].note) - {0}
    #         if len(tempSet1 & tempSet2 & combo) != 2 or tempSet1 != tempSet2 or len(tempSet1) != 2:
    #             continue
    #         rowOffset1 = (a//3) * 3 
    #         for row2 in range(9):
    #             if rowOffset1 <= row2 < rowOffset1 + 3:
    #                 continue
    #             tempSet3 = set(self.layout[row2][b].note) - {0}
    #             tempSet4 = set(self.layout[row2][y].note) - {0}
    #             if len(tempSet3 & tempSet4 & combo) != 2 or tempSet3 != tempSet4 or len(tempSet3) != 2 or not (combo <= tempSet1 | tempSet2 | tempSet3 | tempSet4):
    #                 continue
    #             goalSet = combo - (tempSet1 & tempSet3)
    #             rowOffset2 = (row2//3) * 3
    #             for row3 in range(9):
    #                 if rowOffset1 <= row3 < rowOffset1 + 3 or rowOffset2 <= row3 < rowOffset2 + 3:
    #                     continue
    #                 tempSet5 = set(self.layout[row3][b].note) - {0}
    #                 tempSet6 = set(self.layout[row3][y].note) - {0}
    #                 if not (goalSet <= tempSet5) or not (goalSet <= tempSet6):
    #                     continue
    #                 eVal = 0
    #                 for val in goalSet:
    #                     if self.singleColCheck([(a, b), (row2, b), (row3, b)], {val}) and self.singleColCheck([(x, y), (row2, y), (row3, y)], {val}):
    #                         continue
    #                     eVal = val
    #                 if eVal == 0:
    #                     continue
    #                 self.layout[row3][b].note[eVal-1] = 0
    #                 self.layout[row3][x].note[eVal-1] = 0
    #                 if not self.stuck(tempCopy):
    #                     goodGroup = [(a, b), (x, y), (row2, b), (row2, y), (row3, b), (row3, y)]
    #                     print(goodGroup)
    #                     print(f"Extended Rectangles Row Type 4 removed {eVal} from box and row with {(row3, b), (row3, y)}")
    #                     return
                        
    #     for ((a, b), (x, y)) in colSets:
    #         # print(f"{combo}: {((a, b), (x, y))}")
    #         tempSet1 = set(self.layout[a][b].note) - {0}
    #         tempSet2 = set(self.layout[x][y].note) - {0}
    #         if len(tempSet1 & tempSet2 & combo) != 2 or tempSet1 != tempSet2 or len(tempSet1) != 2:
    #             continue
    #         colOffset1 = (b//3) * 3 
    #         for col2 in range(9):
    #             if colOffset1 <= col2 < colOffset1 + 3:
    #                 continue
    #             tempSet3 = set(self.layout[a][col2].note) - {0}
    #             tempSet4 = set(self.layout[x][col2].note) - {0}
    #             if len(tempSet3 & tempSet4 & combo) != 2 or tempSet3 != tempSet4 or len(tempSet3) != 2 or not (combo <= tempSet1 | tempSet2 | tempSet3 | tempSet4):
    #                 continue
    #             goalSet = combo - (tempSet1 & tempSet3)
    #             colOffset2 = (col2//3) * 3
    #             for col3 in range(9):
    #                 if colOffset1 <= col3 < colOffset1 + 3 or colOffset2 <= col3 < colOffset2 + 3:
    #                     continue
    #                 tempSet5 = set(self.layout[a][col3].note) - {0}
    #                 tempSet6 = set(self.layout[x][col3].note) - {0}
    #                 if not (goalSet <= tempSet5) or not (goalSet <= tempSet6):
    #                     continue
    #                 eVal = 0
    #                 for val in goalSet:
    #                     if self.singleRowCheck([(a, b), (a, col2), (a, col3)], {val}) and self.singleRowCheck([(x, y), (x, col2), (x, col3)], {val}):
    #                         continue
    #                     eVal = val
    #                 if eVal == 0:
    #                     continue
    #                 self.layout[a][col3].note[eVal-1] = 0
    #                 self.layout[x][col3].note[eVal-1] = 0
    #                 if not self.stuck(tempCopy):
    #                     goodGroup = [(a, b), (x, y), (a, col2), (x, col2), (a, col3), (x, col3)]
    #                     print(goodGroup)
    #                     print(f"Extended Rectangles Col Type 4 removed {eVal} from box and row with {(a, col3), (x, col3)}")
    #                     return
    # ********************************************************************************************************************
    def hiddenUniqueRectangles(self, baseCopy, current_node):
        newPuzzles = []
        rowSets, colSets = defaultdict(list), defaultdict(list)
        noteGrid = [[self.getSet((r, c)) for c in range(9)] for r in range(9)]
        for combo in itertools.combinations(self.getRemaining(), 2):
            comboSet = set(combo)
            for row in range(9):
                allCols = [c for c in range(9) if comboSet <= noteGrid[row][c] and not self.locked[row][c]]
                for c1, c2 in itertools.combinations(allCols, 2):
                    if self.inBox([(row, c1), (row, c2)]):
                        rowSets[combo].append((row, c1, c2))
            for col in range(9):
                allRows = [r for r in range(9) if comboSet <= noteGrid[r][col] and not self.locked[r][col]]
                for r1, r2 in itertools.combinations(allRows, 2):
                    if self.inBox([(r1, col), (r2, col)]):
                        colSets[combo].append((col, r1, r2))

        # ---- Row orientation ----
        for combo, entries in rowSets.items():
            if len(entries) < 2: continue
            comboSet = set(combo)
            for (rowA, c1A, c2A), (rowB, c1B, c2B) in itertools.combinations(entries, 2):
                n1a, n1b = (rowA, c1A), (rowA, c2A)
                n2a, n2b = (rowB, c1B), (rowB, c2B)

                if self.inBox([n1a, n2a]):
                    continue
                if not self.inCol([n1a, n2a]) or not self.inCol([n1b, n2b]):
                    continue

                nodeList = [n1a, n1b, n2a, n2b]
                if not any(noteGrid[r][c] == comboSet for r, c in nodeList): continue 
                    
                diagonal = {n1a: n2b, n1b: n2a, n2a: n1b, n2b: n1a}
                vertical = {n1a: n2a, n1b: n2b, n2a: n1a, n2b: n1b}
                horizontal = {n1a: n1b, n1b: n1a, n2a: n2b, n2b: n2a}

                # Type 1
                checkVal = None
                for val in combo:
                    if self.getAnyColIdxs(n1a, {val}) == {n1a, n2a} and self.getAnyColIdxs(n1b, {val}) == {n1b, n2b}:
                        checkVal = val
                if checkVal is not None:
                    keyNodes = {node for node in nodeList if noteGrid[node[0]][node[1]] == comboSet}
                    if len(keyNodes) == 1:
                        keyNode = keyNodes.pop()
                        eVal = (comboSet - {checkVal}).pop()
                        eNodes = {(eVal, diagonal[keyNode])}
                        if eNodes and not uberPrune(current_node, ("Hidden UR Row T1", nodeList, eNodes, None)):
                            baseCopy.updateNotesGX(eNodes)
                            if not self.stuck(baseCopy):
                                note = f"Hidden Unique Rectangles Row Type 1 removed {eVal} from {diagonal[keyNode]}"
                                baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Hidden UR Row T1", current_node, nodeList)
                                newPuzzles.append(tempPuzzle)

                # Type 2A
                gSet = None
                if comboSet == noteGrid[n1a[0]][n1a[1]] | noteGrid[n1b[0]][n1b[1]] and comboSet != noteGrid[n2a[0]][n2a[1]] and comboSet != noteGrid[n2b[0]][n2b[1]]:
                    gSet = {n1a, n1b}
                elif comboSet == noteGrid[n2a[0]][n2a[1]] | noteGrid[n2b[0]][n2b[1]] and comboSet != noteGrid[n1a[0]][n1a[1]] and comboSet != noteGrid[n1b[0]][n1b[1]]:
                    gSet = {n2a, n2b}
                if gSet is not None:
                    eNodes = set()
                    for val in combo:
                        for gNode in gSet:
                            if self.getAnyColIdxs(gNode, {val}) == {gNode, vertical[gNode]}:
                                eVal = (comboSet - {val}).pop()
                                eNodes |= {(eVal, diagonal[gNode])}
                    if eNodes and not uberPrune(current_node, ("Hidden UR Row T2A", nodeList, eNodes, None)):
                        baseCopy.updateNotesGX(eNodes)
                        if not self.stuck(baseCopy):
                            note = f"Hidden Unique Rectangles Row Type 2A removed {eNodes}"
                            baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Hidden UR Row T2A", current_node, nodeList)
                            newPuzzles.append(tempPuzzle)

                # Type 2B
                gSet = None
                if comboSet == noteGrid[n1a[0]][n1a[1]] | noteGrid[n2a[0]][n2a[1]] and comboSet != noteGrid[n1b[0]][n1b[1]] and comboSet != noteGrid[n2b[0]][n2b[1]]:
                    gSet = {n1a, n2a}
                elif comboSet == noteGrid[n1b[0]][n1b[1]] | noteGrid[n2b[0]][n2b[1]] and comboSet != noteGrid[n1a[0]][n1a[1]] and comboSet != noteGrid[n2a[0]][n2a[1]]:
                    gSet = {n1b, n2b}
                if gSet is not None:
                    eNodes = set()
                    for val in combo:
                        for gNode in gSet:
                            if self.getAnyRowIdxs(gNode, {val}) == {gNode, horizontal[gNode]}:
                                eVal = (comboSet - {val}).pop()
                                eNodes |= {(eVal, diagonal[gNode])}
                    if eNodes and not uberPrune(current_node, ("Hidden UR Row T2B", nodeList, eNodes, None)):
                        baseCopy.updateNotesGX(eNodes)
                        if not self.stuck(baseCopy):
                            note = f"Hidden Unique Rectangles Row Type 2B removed {eNodes}"
                            baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Hidden UR Row T2B", current_node, nodeList)
                            newPuzzles.append(tempPuzzle)

        # ---- Column orientation ----
        for combo, entries in colSets.items():
            if len(entries) < 2: continue
            comboSet = set(combo)
            for (colA, r1A, r2A), (colB, r1B, r2B) in itertools.combinations(entries, 2):
                n1a, n1b = (r1A, colA), (r2A, colA)
                n2a, n2b = (r1B, colB), (r2B, colB)

                if self.inBox([n1a, n2a]):
                    continue
                if not self.inRow([n1a, n2a]) or not self.inRow([n1b, n2b]):
                    continue

                nodeList = [n1a, n1b, n2a, n2b]
                if not any(noteGrid[r][c] == comboSet for r, c in nodeList): continue 
                
                diagonal = {n1a: n2b, n1b: n2a, n2a: n1b, n2b: n1a}
                vertical = {n1a: n1b, n1b: n1a, n2a: n2b, n2b: n2a}
                horizontal = {n1a: n2a, n1b: n2b, n2a: n1a, n2b: n1b}

                # Type 1
                checkVal = None
                for val in combo:
                    if self.getAnyRowIdxs(n1a, {val}) == {n1a, n2a} and self.getAnyRowIdxs(n1b, {val}) == {n1b, n2b}:
                        checkVal = val
                if checkVal is not None:
                    keyNodes = {node for node in nodeList if noteGrid[node[0]][node[1]] == comboSet}
                    if len(keyNodes) == 1:
                        keyNode = keyNodes.pop()
                        eVal = (comboSet - {checkVal}).pop()
                        eNodes = {(eVal, diagonal[keyNode])}
                        if eNodes and not uberPrune(current_node, ("Hidden UR Col T1", nodeList, eNodes, None)):
                            baseCopy.updateNotesGX(eNodes)
                            if not self.stuck(baseCopy):
                                note = f"Hidden Unique Rectangles Col Type 1 removed {eVal} from {diagonal[keyNode]}"
                                baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Hidden UR Col T1", current_node, nodeList)
                                newPuzzles.append(tempPuzzle)

                # Type 2A
                gSet = None
                if comboSet == noteGrid[n1a[0]][n1a[1]] | noteGrid[n1b[0]][n1b[1]] and comboSet != noteGrid[n2a[0]][n2a[1]] and comboSet != noteGrid[n2b[0]][n2b[1]]:
                    gSet = {n1a, n1b}
                elif comboSet == noteGrid[n2a[0]][n2a[1]] | noteGrid[n2b[0]][n2b[1]] and comboSet != noteGrid[n1a[0]][n1a[1]] and comboSet != noteGrid[n1b[0]][n1b[1]]:
                    gSet = {n2a, n2b}
                if gSet is not None:
                    eNodes = set()
                    for val in combo:
                        for gNode in gSet:
                            if self.getAnyRowIdxs(gNode, {val}) == {gNode, horizontal[gNode]}:
                                eVal = (comboSet - {val}).pop()
                                eNodes |= {(eVal, diagonal[gNode])}
                    if eNodes and not uberPrune(current_node, ("Hidden UR Col T2A", nodeList, eNodes, None)):
                        baseCopy.updateNotesGX(eNodes)
                        if not self.stuck(baseCopy):
                            note = f"Hidden Unique Rectangles Col Type 2A removed {eNodes}"
                            baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Hidden UR Col T2A", current_node, nodeList)
                            newPuzzles.append(tempPuzzle)

                # Type 2B
                gSet = None
                if comboSet == noteGrid[n1a[0]][n1a[1]] | noteGrid[n2a[0]][n2a[1]] and comboSet != noteGrid[n1b[0]][n1b[1]] and comboSet != noteGrid[n2b[0]][n2b[1]]:
                    gSet = {n1a, n2a}
                elif comboSet == noteGrid[n1b[0]][n1b[1]] | noteGrid[n2b[0]][n2b[1]] and comboSet != noteGrid[n1a[0]][n1a[1]] and comboSet != noteGrid[n2a[0]][n2a[1]]:
                    gSet = {n1b, n2b}
                if gSet is not None:
                    eNodes = set()
                    for val in combo:
                        for gNode in gSet:
                            if self.getAnyColIdxs(gNode, {val}) == {gNode, vertical[gNode]}:
                                eVal = (comboSet - {val}).pop()
                                eNodes |= {(eVal, diagonal[gNode])}
                    if eNodes and not uberPrune(current_node, ("Hidden UR Col T2B", nodeList, eNodes, None)):
                        baseCopy.updateNotesGX(eNodes)
                        if not self.stuck(baseCopy):
                            note = f"Hidden Unique Rectangles Col Type 2B removed {eNodes}"
                            baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "Hidden UR Col T2B", current_node, nodeList)
                            newPuzzles.append(tempPuzzle)

        return baseCopy, newPuzzles


    # def hiddenUniqueRectanglesUtil(self):
    #     tempCopy = copy.deepcopy(self)
    #     remaining = self.getRemaining()
    #     for combo in itertools.combinations(remaining, 2):
    #         self.hiddenUniqueRectangles(set(combo), tempCopy)
    #         if not self.stuck(tempCopy):
    #             return
    # def hiddenUniqueRectangles(self, combo, tempCopy):
    #     rowSets = set()
    #     colSets = set()
    #     for row in range(9):
    #         matchingCols = [c for c in range(9) if combo <= set(self.layout[row][c].note) - {0}]
    #         for c1, c2 in itertools.combinations(matchingCols, 2):
    #             pair = frozenset(((row, c1), (row, c2)))
    #             rowSets.add(pair)
    #     for col in range(9):
    #         matchingRows = [r for r in range(9) if combo <= set(self.layout[r][col].note) - {0}]
    #         for r1, r2 in itertools.combinations(matchingRows, 2):
    #             pair = frozenset(((r1, col), (r2, col)))
    #             colSets.add(pair)
    #     # type 1 Row
    #     for ((a, b), (c, d)) in rowSets:
    #         tempSet1 = set(self.layout[a][b].note) - {0}
    #         tempSet2 = set(self.layout[c][d].note) - {0}
    #         if not(len(tempSet1) != 2 ^ len(tempSet2) != 2) or not self.inBox([(a, b), (c, d)]) or len(tempSet1) == 0 or len(tempSet2) == 0:
    #             continue
    #         rowOffset = (a//3) * 3
    #         for row in range(9):
    #             if rowOffset <= row < rowOffset + 3 or frozenset(((row, b), (row, d))) not in rowSets:
    #                 continue
    #             vals = []
    #             if len(tempSet1) == 2:
    #                 for val in tempSet1:
    #                     if self.singleRowCheck([(row, d), (row, b)], {val}) and self.singleColCheck([(row, d), (c, d)], {val}):
    #                         vals.append(val)
    #                 if len(vals) == 1:
    #                     eVal = (combo - set(vals)).pop()
    #                     self.layout[row][d].note[eVal-1] = 0
    #             elif len(tempSet2) == 2:
    #                 for val in tempSet2:
    #                     if self.singleRowCheck([(row, b), (row, d)], {val}) and self.singleColCheck([(row, b), (a, b)], {val}):
    #                         vals.append(val)
    #                 if len(vals) == 1:
    #                     eVal = (combo - set(vals)).pop()
    #                     self.layout[row][b].note[eVal-1] = 0
    #             if not self.stuck(tempCopy):
    #                 print(f"Hidden Unique Rectangles Row Type 1 removed {eVal} at either {(row, b)} or {(row, d)}")
    #                 return
    #     # type 1 Col
    #     for ((a, b), (c, d)) in colSets:
    #         tempSet1 = set(self.layout[a][b].note) - {0}
    #         tempSet2 = set(self.layout[c][d].note) - {0}
    #         if not(len(tempSet1) != 2 ^ len(tempSet2) != 2) or not self.inBox([(a, b), (c, d)]) or len(tempSet1) == 0 or len(tempSet2) == 0:
    #             continue
    #         colOffset = (b//3) * 3
    #         for col in range(9):
    #             if colOffset <= col < colOffset + 3 or frozenset(((a, col), (c, col))) not in rowSets:
    #                 continue
    #             vals = []
    #             if len(tempSet1) == 2:
    #                 for val in tempSet1:
    #                     if self.singleColCheck([(c, col), (a, col)], {val}) and self.singleRowCheck([(c, col), (c, d)], {val}):
    #                         vals.append(val)
    #                 if len(vals) == 1:
    #                     eVal = (combo - set(vals)).pop()
    #                     self.layout[c][col].note[eVal-1] = 0
    #             elif len(tempSet2) == 2:
    #                 for val in tempSet2:
    #                     if self.singleColCheck([(a, col), (c, col)], {val}) and self.singleRowCheck([(a, col), (a, b)], {val}):
    #                         vals.append(val)
    #                 if len(vals) == 1:
    #                     eVal = (combo - set(vals)).pop()
    #                     self.layout[a][col].note[eVal-1] = 0
    #             if not self.stuck(tempCopy):
    #                 print(f"Hidden Unique Rectangles Col Type 1 removed {eVal} at either {(a, col)} or {(c, col)}")
    #                 return
    #     # Type 2a Row
    #     for ((a, b), (c, d)) in rowSets:
    #         tempSet1 = set(self.layout[a][b].note) - {0}
    #         tempSet2 = set(self.layout[c][d].note) - {0}
    #         if not (len(tempSet1) == 2 and len(tempSet2) == 2) or tempSet1 != tempSet2 or not self.inBox([(a, b), (c, d)]):
    #             continue
    #         rowOffset = (a//3) * 3
    #         for row in range(9):
    #             if rowOffset <= row < rowOffset + 3 or frozenset(((row, b), (row, d))) not in rowSets:
    #                 continue
    #             for val in tempSet1:
    #                 eVal = (combo - {val}).pop()
    #                 if self.singleColCheck([(a, b), (row, b)], {val}):
    #                     self.layout[row][d].note[eVal-1] = 0
    #                 if self.singleColCheck([(c, d), (row, d)], {val}):
    #                     self.layout[row][b].note[eVal-1] = 0
    #             if not self.stuck(tempCopy):
    #                 print(f"Hidden Unique Rectangles Row Type 2a removed some of {combo} from either {(row, b)} or {(row, d)}")
    #                 return
    #     # Type 2a Col
    #     for ((a, b), (c, d)) in colSets:
    #         tempSet1 = set(self.layout[a][b].note) - {0}
    #         tempSet2 = set(self.layout[c][d].note) - {0}
    #         if not (len(tempSet1) == 2 and len(tempSet2) == 2) or tempSet1 != tempSet2  or not self.inBox([(a, b), (c, d)]):
    #             continue
    #         colOffset = (b//3) * 3
    #         for col in range(9):
    #             if colOffset <= col < colOffset + 3 or frozenset(((a, col), (c, col))) not in colSets:
    #                 continue
    #             for val in tempSet1:
    #                 eVal = (combo - {val}).pop()
    #                 if self.singleRowCheck([(a, b), (a, col)], {val}):
    #                     self.layout[c][col].note[eVal-1] = 0
    #                 if self.singleRowCheck([(c, d), (c, col)], {val}):
    #                     self.layout[a][col].note[eVal-1] = 0
    #             if not self.stuck(tempCopy):
    #                 print(f"Hidden Unique Rectangles Col Type 2a removed some of {combo} from either {(a, col)} or {(c, col)}")
    #                 return
    #     # Type 2b Row
    #     for ((a, b), (c, d)) in rowSets:
    #         tempSet1 = set(self.layout[a][b].note) - {0}
    #         tempSet2 = set(self.layout[c][d].note) - {0}
    #         if not (len(tempSet1) == 2 and len(tempSet2) == 2) or tempSet1 != tempSet2 or self.inBox([(a, b), (c, d)]):
    #             continue
    #         rowOffset = (a//3) * 3
    #         for row in range(rowOffset, rowOffset + 3):
    #             if row == a or frozenset(((row, b), (row, d))) not in rowSets:
    #                 continue
    #             print(f"BasePair: {(a, b), (c, d)}. Comparing to: {(row, b), (row, d)}")
    #             for val in tempSet1:
    #                 eVal = (combo - {val}).pop()
    #                 if self.singleColCheck([(a, b), (row, b)], {val}) and self.singleBoxCheck([(a, b), (row, b)], {val}):
    #                     self.layout[row][d].note[eVal-1] = 0
    #                 if self.singleColCheck([(c, d), (row, d)], {val}) and self.singleBoxCheck([(c, d), (row, d)], {val}):
    #                     self.layout[row][b].note[eVal-1] = 0
    #             if not self.stuck(tempCopy):
    #                 print(f"Hidden Unique Rectangles Row Type 2b removed some of {combo} from either {(row, b)} or {(row, d)}")
    #                 return
    #     # Type 2b Col
    #     for ((a, b), (c, d)) in colSets:
    #         tempSet1 = set(self.layout[a][b].note) - {0}
    #         tempSet2 = set(self.layout[c][d].note) - {0}
    #         if not (len(tempSet1) == 2 and len(tempSet2) == 2) or tempSet1 != tempSet2  or self.inBox([(a, b), (c, d)]):
    #             continue
    #         colOffset = (b//3) * 3
    #         for col in range(colOffset, colOffset + 3):
    #             if b == col or frozenset(((a, col), (c, col))) not in colSets:
    #                 continue
    #             for val in tempSet1:
    #                 eVal = (combo - {val}).pop()
    #                 if self.singleRowCheck([(a, b), (a, col)], {val}) and self.singleBoxCheck([(a, b), (a, col)], {val}):
    #                     self.layout[c][col].note[eVal-1] = 0
    #                 if self.singleRowCheck([(c, d), (c, col)], {val}) and self.singleBoxCheck([(c, d), (c, col)], {val}):
    #                     self.layout[a][col].note[eVal-1] = 0
    #             if not self.stuck(tempCopy):
    #                 print(f"Hidden Unique Rectangles Col Type 2b removed some of {combo} from either {(a, col)} or {(c, col)}")
    #                 return
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

    def wxyzWing(self, baseCopy, current_node):
        # WORKS UNDER ASSUMPTION THAT ROW/COL NODES DON'T HAVE TO BE IN THE SAME SQUARE
        newPuzzles = []
        noteGrid = [[self.getSet((r, c)) for c in range(9)] for r in range(9)]
        remaining = self.getRemaining()
    
        rootCandidates = [(r, c) for r in range(9) for c in range(9) if not self.locked[r][c] and 3 <= len(noteGrid[r][c]) <= 4]
    
        # Type 1
        for rr, rc in rootCandidates:
            rro, rco = [x for x in range(self.getOffset(rr), self.getOffset(rr) + 3)], [x for x in range(self.getOffset(rc), self.getOffset(rc) + 3)]
            boxCandidates, rowCandidates, rowBoxCandidates, colCandidates, colBoxCandidates = {}, {}, {}, {}, {}
            rootSet = noteGrid[rr][rc]
            # box search
            for tempr in rro:
                if tempr == rr: continue
                for tempc in rco:
                    if tempc == rc: continue
                    if 2 == len(noteGrid[tempr][tempc]) and len(noteGrid[tempr][tempc] & rootSet) >= 1:
                        boxCandidates[(tempr, tempc)] = noteGrid[tempr][tempc]
            # row search
            for tempc in range(9):
                if tempc == rc or self.locked[rr][tempc]: continue
                if not tempc in rco and len(noteGrid[rr][tempc]) <= 3 and noteGrid[rr][tempc] != rootSet and 1 <= len(noteGrid[rr][tempc] & rootSet) <= 3:
                    rowCandidates[(rr, tempc)] = noteGrid[rr][tempc]
                if tempc in rco and len(noteGrid[rr][tempc] & rootSet) == 2:
                    rowBoxCandidates[(rr, tempc)] = noteGrid[rr][tempc]
    
            # col search
            for tempr in range(9):
                if tempr == rr or self.locked[tempr][rc]: continue
                if not tempr in rro and len(noteGrid[tempr][rc]) <= 3 and noteGrid[tempr][rc] != rootSet and 1 <= len(noteGrid[tempr][rc] & rootSet) <= 3:
                    colCandidates[(tempr, rc)] = noteGrid[tempr][rc]
                if tempr in rro and len(noteGrid[tempr][rc] & rootSet) == 2:
                    colBoxCandidates[(tempr, rc)] = noteGrid[tempr][rc]
    
            for boxNode in boxCandidates:
                if len(rootSet | boxCandidates[boxNode]) != 4: continue
                # row Candidates if one root
                for n1, n2 in itertools.combinations(rowCandidates, 2):
                    if not self.inBox([n1, n2]) or boxCandidates[boxNode] == rowCandidates[n1] or boxCandidates[boxNode] == rowCandidates[n2]: continue 
                    if len(rootSet | boxCandidates[boxNode] | rowCandidates[n1] | rowCandidates[n2]) == 4:
                        eVal = boxCandidates[boxNode] & rowCandidates[n1] & rowCandidates[n2]
                        if len(eVal) != 1: continue
                        eVal = eVal.pop()
                        if eVal in rootSet:
                            eNodes = {(eVal, (rr, c)) for c in rco if c != rc and eVal in noteGrid[rr][c]}
                        if eVal not in rootSet:
                            group = [boxNode, n1, n2]
                            if not all(len(noteGrid[r][c]) == 2 for r, c in group):
                                continue 
                            eNodes = {(eVal, (r, c)) for r, c in self.getSeenByAtLeastTwo(group, eVal)}
                        group = [(rr, rc), boxNode, n1, n2]
                        if eNodes and not uberPrune(current_node, ("WXYZ Wing Row Type 1", group, eNodes, None)):
                            baseCopy.updateNotesGX(eNodes)
                            if self.stuck(baseCopy): continue
                            diffNodes = self.puzzleDifference(baseCopy)
                            note = f"WXYZ Wing Row Type 1a found root {(rr, rc)}\nBoxNode: {boxNode}\nRowNodes: {n1, n2}\nRemoving {eNodes}"
                            baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "WXYZ Wing Row Type 1", current_node, group)
                            newPuzzles.append(tempPuzzle)
                # row candidates if 2 roots
                for root2 in rowBoxCandidates:
                    if len(rootSet | boxCandidates[boxNode] | rowBoxCandidates[root2]) != 4 or self.inCol([boxNode, root2]):
                        continue
                    for n1 in rowCandidates:
                        if len(rootSet | boxCandidates[boxNode] | rowBoxCandidates[root2] | rowCandidates[n1]) != 4: continue 
                        if len((rootSet | rowBoxCandidates[root2]) & rowCandidates[n1]) < 2 or rowCandidates[n1] == boxCandidates[boxNode]: continue
                        eVal = (boxCandidates[boxNode] & rowCandidates[n1]) - (rootSet | rowBoxCandidates[root2])
                        if len(eVal) != 1: continue
                        eVal = eVal.pop()
                        group = [boxNode, n1]
                        eNodes = {(eVal, (r, c)) for r, c in self.getSeenByAtLeastTwo(group, eVal)}
                        # **********************************************************
                        if any(noteGrid[r][c] == boxCandidates[boxNode] for _, (r, c) in eNodes): continue
                        if eNodes and not uberPrune(current_node, ("WXYZ Wing Row Type 1", group, eNodes, None)):
                            baseCopy.updateNotesGX(eNodes)
                            if self.stuck(baseCopy): continue
                            diffNodes = self.puzzleDifference(baseCopy)
                            note = f"WXYZ Wing Row Type 1b found roots {(rr, rc), root2}\nBoxNode: {boxNode}\nRowNodes: {n1}\nRemoving {eNodes}"
                            baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "WXYZ Wing Row Type 1", current_node, group)
                            newPuzzles.append(tempPuzzle)
                # col candidates if one root 
                for n1, n2 in itertools.combinations(colCandidates, 2):
                    if not self.inBox([n1, n2]) or boxCandidates[boxNode] == colCandidates[n1] or boxCandidates[boxNode] == colCandidates[n2]: continue 
                    if len(rootSet | boxCandidates[boxNode] | colCandidates[n1] | colCandidates[n2]) == 4:
                        eVal = boxCandidates[boxNode] & colCandidates[n1] & colCandidates[n2]
                        if len(eVal) != 1: continue
                        eVal = eVal.pop()
                        if eVal in rootSet:
                            eNodes = {(eVal, (r, rc)) for r in rro if r != rr and eVal in noteGrid[r][rc]}
                        if eVal not in rootSet:
                            group = [boxNode, n1, n2]
                            if not all(len(noteGrid[r][c]) == 2 for r, c in group):
                                continue 
                            eNodes = {(eVal, (r, c)) for r, c in self.getSeenByAtLeastTwo(group, eVal)}
                        group = [(rr, rc), boxNode, n1, n2]
                        if eNodes and not uberPrune(current_node, ("WXYZ Wing Col Type 1", group, eNodes, None)):
                            baseCopy.updateNotesGX(eNodes)
                            if self.stuck(baseCopy): continue
                            diffNodes = self.puzzleDifference(baseCopy)
                            note = f"WXYZ Wing Col Type 1a found root {(rr, rc)}\nBoxNode: {boxNode}\nColNodes: {n1, n2}\nRemoving {eNodes}"
                            baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "WXYZ Wing Col Type 1", current_node, group)
                            newPuzzles.append(tempPuzzle)
                # col candidates if 2 roots
                for root2 in colBoxCandidates:
                    if len(rootSet | boxCandidates[boxNode] | colBoxCandidates[root2]) != 4 or self.inRow([boxNode, root2]): continue
                    for n1 in colCandidates:
                        if len(rootSet | boxCandidates[boxNode] | colBoxCandidates[root2] | colCandidates[n1]) != 4: continue
                        if len((rootSet | colBoxCandidates[root2]) & colCandidates[n1]) < 2 or colCandidates[n1] == boxCandidates[boxNode]: continue
                        eVal = (boxCandidates[boxNode] & colCandidates[n1]) - (rootSet | colBoxCandidates[root2])
                        if len(eVal) != 1: continue
                        eVal = eVal.pop()
                        group = [boxNode, n1]
                        eNodes = {(eVal, (r, c)) for r, c in self.getSeenByAtLeastTwo(group, eVal)}
                        # ************************************************
                        if any(noteGrid[r][c] == boxCandidates[boxNode] for _, (r, c) in eNodes): continue
                        if eNodes and not uberPrune(current_node, ("WXYZ Wing Col Type 1", group, eNodes, None)):
                            baseCopy.updateNotesGX(eNodes)
                            if self.stuck(baseCopy): continue
                            diffNodes = self.puzzleDifference(baseCopy)
                            note = f"WXYZ Wing Col Type 1b found roots {(rr, rc), root2}\nBoxNode: {boxNode}\nColNodes: {n1}\nRemoving {eNodes}"
                            baseCopy, tempPuzzle = self.puzzleFlip(baseCopy, note, "WXYZ Wing Col Type 1", current_node, group)
                            newPuzzles.append(tempPuzzle)
    
        return baseCopy, newPuzzles
        
    def getSeenByAtLeastTwo(self, nodes, val=None):
        nodeSet = set(nodes)
        seenSets = [self.getAnyCoords(n) - nodeSet for n in nodes]
        result = []
        for r in range(9):
            for c in range(9):
                coord = (r, c)
                if sum(coord in s for s in seenSets) >= 2:
                    result.append(coord)
        if val is not None:
            result = [coord for coord in result if val in self.getSet(coord)]
        return result      






















