#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import time

from collections import namedtuple
Item = namedtuple("Item", ['index', 'value', 'weight', 'valuePerWeight'])

interrupted = False

class Solution:
    def __init__(self, valueSolution, takenSolution, sortedItems, interrupted):
        self.valueSolution = valueSolution
        self.takenSolution = takenSolution
        self.sortedItems = sortedItems
        self.interrupted = interrupted

class Node:
    def __init__(self, item, spaceLeft, bestExpectedValue, bestTakenItems, takenItems, currentValue, sortedIndex, partialItemIndex, partialItemValue, partialItemSpace, startTime, solution):
        self.item = item
        self.spaceLeft = spaceLeft
        self.bestExpectedValue = bestExpectedValue
        self.bestTakenItems = bestTakenItems
        self.takenItems = takenItems
        self.currentValue = currentValue
        self.sortedIndex = sortedIndex
        self.partialItemIndex = partialItemIndex
        self.partialItemValue = partialItemValue
        self.partialItemSpace = partialItemSpace
        self.startTime = startTime
        self.solution = solution

    def dfs(self):
        if time.time() - self.startTime > 5:
            self.solution.interrupted = True
            return
        if self.bestExpectedValue < self.solution.valueSolution:
            return
        addedValue = self.tryTakeItem()
        if addedValue == -1:
            self.leaveItem()
            return
        
        # first take the item (left side of tree)
        newCurrentValue = self.currentValue + addedValue
        newSpaceLeft = self.spaceLeft - self.item.weight
        self.takenItems[self.item.index] = 1
        if self.sortedIndex == len(self.solution.sortedItems) - 1:
            if newCurrentValue > self.solution.valueSolution:
                self.solution.valueSolution = newCurrentValue
                self.solution.takenSolution = list(self.takenItems)
        else:
            nextNode = Node(self.solution.sortedItems[self.sortedIndex + 1], newSpaceLeft, self.bestExpectedValue, self.bestTakenItems, self.takenItems, newCurrentValue, self.sortedIndex + 1, self.partialItemIndex, self.partialItemValue, self.partialItemSpace, self.startTime, self.solution)
            nextNode.dfs()

        self.takenItems[self.item.index] = 0

        # then try leaving the item (right side of tree)
        self.leaveItem()

    def tryTakeItem(self):
        if self.spaceLeft < self.item.weight:
            return -1
        else:
            return self.item.value

    def leaveItem(self):
        if self.sortedIndex == len(self.solution.sortedItems) - 1:
            if self.currentValue > self.solution.valueSolution:
                self.solution.valueSolution = self.currentValue
                self.solution.takenSolution = list(self.takenItems)
        else:
            self.recalculateBestExpectedSolution()
            nextNode = Node(self.solution.sortedItems[self.sortedIndex + 1], self.spaceLeft, self.bestExpectedValue, self.bestTakenItems, self.takenItems, self.currentValue, self.sortedIndex + 1, self.partialItemIndex, self.partialItemValue, self.partialItemSpace, self.startTime, self.solution)
            nextNode.dfs()

    def recalculateBestExpectedSolution(self):
        if self.bestTakenItems[self.item.index] == 0:
            return
        elif self.bestTakenItems[self.item.index] == 1:
            self.bestTakenItems[self.item.index] = 0
            self.bestExpectedValue -= self.item.value
            self.bestExpectedValue -= self.partialItemValue
            roomLeft = self.partialItemSpace + self.item.weight
            
            while(self.partialItemIndex < len(self.solution.sortedItems) and roomLeft >= self.solution.sortedItems[self.partialItemIndex].weight):
                self.bestExpectedValue += self.solution.sortedItems[self.partialItemIndex].value
                self.bestTakenItems[self.solution.sortedItems[self.partialItemIndex].index] = 1
                roomLeft -= self.solution.sortedItems[self.partialItemIndex].weight
                self.partialItemIndex += 1
            
            if self.partialItemIndex == len(self.solution.sortedItems):
                return

            self.bestTakenItems[self.solution.sortedItems[self.partialItemIndex].index] = 2
            self.partialItemValue = roomLeft * self.solution.sortedItems[self.partialItemIndex].valuePerWeight
            self.bestExpectedValue += self.partialItemValue
            self.partialItemSpace = roomLeft
            return
        else:
            self.bestTakenItems[self.item.index] = 0
            self.bestExpectedValue -= self.partialItemValue
            self.partialItemIndex += 1
            roomLeft = self.partialItemSpace
            
            while(self.partialItemIndex < len(self.solution.sortedItems) and roomLeft >= self.solution.sortedItems[self.partialItemIndex].weight):
                self.bestExpectedValue += self.solution.sortedItems[self.partialItemIndex].value
                self.bestTakenItems[self.solution.sortedItems[self.partialItemIndex].index] = 1
                roomLeft -= self.solution.sortedItems[self.partialItemIndex].weight
                self.partialItemIndex += 1

            if self.partialItemIndex == len(self.solution.sortedItems):
                return

            self.bestTakenItems[self.solution.sortedItems[self.partialItemIndex].index] = 2
            self.partialItemValue = roomLeft * self.solution.sortedItems[self.partialItemIndex].valuePerWeight
            self.bestExpectedValue += self.partialItemValue
            self.partialItemSpace = roomLeft
            return
			

	

def solve_it(input_data):
    # Modify this code to run your optimization algorithm
    sys.setrecursionlimit(20000)

    # parse the input
    lines = input_data.split('\n')

    firstLine = lines[0].split()
    item_count = int(firstLine[0])
    capacity = int(firstLine[1])

    items = []

    for i in range(1, item_count+1):
        line = lines[i]
        parts = line.split()
        items.append(Item(i-1, int(parts[0]), int(parts[1]), float(parts[0])/float(parts[1])))

    sortedItems = sorted(items, key=lambda item: (item.valuePerWeight, -item.weight), reverse=True)

    takenSolution = [0]*len(items)
    bestPossibleTaken = [0]*len(items)
    bestPossibleValue = 0
    taken = [0]*len(items)
    room = capacity
    i = 0
   
    while i < len(sortedItems) and room >= sortedItems[i].weight:
        bestPossibleTaken[sortedItems[i].index] = 1
        bestPossibleValue += sortedItems[i].value
        room -= sortedItems[i].weight
        i += 1

    partialItem = sortedItems[i]
    partialValue = partialItem.valuePerWeight * room
    bestPossibleTaken[partialItem.index] = 2
    bestPossibleValue += partialValue
    startTime = time.time()
    solution = Solution(0, takenSolution, sortedItems, False)

    rootNode = Node(sortedItems[0], capacity, bestPossibleValue, bestPossibleTaken, taken, 0, 0, i, partialValue, room, startTime, solution)
    rootNode.dfs()
    
    # prepare the solution in the specified output format
    if rootNode.solution.interrupted:
        output_data = str(rootNode.solution.valueSolution) + ' ' + str(0) + '\n'
        output_data += ' '.join(map(str, rootNode.solution.takenSolution))
    else:
        output_data = str(rootNode.solution.valueSolution) + ' ' + str(1) + '\n'
        output_data += ' '.join(map(str, rootNode.solution.takenSolution))
    return output_data


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
        print(solve_it(input_data))
    else:
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/ks_4_0)')

