import numpy as np

class Grid:
    def __init__(self, rows, cols, numActions):
        self.rows = rows
        self.cols = cols
        self.activeGrid = np.zeros((rows, cols), dtype=bool)
        self.rewards = np.zeros((rows, cols), dtype=float)
        self.actions = np.zeros((rows, cols, numActions, 6), dtype=float)
        self.startingProbs = np.zeros((rows, cols), dtype=float)

    def setActiveGrid(self, coordList):
        for coord in coordList:
            self.activeGrid[coord[0], coord[1]] = True

    def setStartingProbs(self, coordList, probList):
        for coord, prob in zip(coordList, probList):
            self.startingProbs[coord[0], coord[1]] = prob
    
    def setRewards(self, coordList, rewardList):
        for coord, reward in zip(coordList, rewardList):
            self.rewards[coord[0], coord[1]] = reward
    
    def addAction(self, coord, actionNum, direction, prob):
        self.actions[coord[0], coord[1], actionNum, direction] = prob
