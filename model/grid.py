import numpy as np

class Grid:
    def __init__(self, rows, cols, numActions):
        self.rows = rows
        self.cols = cols
        self._activeGrid = np.zeros((rows, cols), dtype=bool)
        self.rewards = np.zeros((rows, cols), dtype=float)
        self.actions = np.zeros((rows, cols, numActions, 6), dtype=float)
        # always stay by default
        for row in range(rows):
            for col in range(cols):
                self.actions[row, col, :, 5] = 1.0
        self.startingProbs = np.zeros((rows, cols), dtype=float)
        self.numActions = numActions

    def isActive(self, row, col):
        if row < 0 or row >= self.rows or col < 0 or col >= self.cols:
            return False
        return self._activeGrid[row, col]

    def setActiveGridCoord(self, row, col, active):
        self._activeGrid[row, col] = active

    def setActiveGrid(self, coordList):
        for coord in coordList:
            self._activeGrid[coord[0], coord[1]] = not self._activeGrid[coord[0], coord[1]]

    def setStartingProb(self, row, col, prob):
        self.startingProbs[row, col] = prob

    def setStartingProbs(self, coordList, probList):
        for coord, prob in zip(coordList, probList):
            self.startingProbs[coord[0], coord[1]] = prob
    
    def setReward(self, row, col, reward):
        self.rewards[row, col] = reward

    def setRewards(self, coordList, rewardList):
        for coord, reward in zip(coordList, rewardList):
            self.rewards[coord[0], coord[1]] = reward
    
    def addAction(self, coord, actionNum, direction, prob):
        self.actions[coord[0], coord[1], actionNum, direction] = prob

    def addActionList(self, coord, actionNum, probList):
        for i in range(len(probList)):
            self.actions[coord[0], coord[1], actionNum, i] = probList[i]

    def getTransitionProb(self, row, col, actionNum, direction):
        # direction: 0=north, 1=south, 2=east, 3=west, 4=terminate, 5=stay
        return self.actions[row, col, actionNum, direction]

    def getNextState(self, row, col, direction):
        # direction: 0=north, 1=south, 2=east, 3=west, 4=terminate, 5=stay
        if direction == 0:
            return row - 1, col
        elif direction == 1:
            return row + 1, col
        elif direction == 2:
            return row, col + 1
        elif direction == 3:
            return row, col - 1
        elif direction == 4:
            return row, col
        elif direction == 5:
            return row, col
        else:
            raise Exception("Invalid direction: " + str(direction))
    
    def getReward(self, row, col):
        return self.rewards[row, col]