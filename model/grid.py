import numpy as np

class Grid:
    def __init__(self, rows, cols, numActions):
        self.rows = rows
        self.cols = cols
        self.activeGrid = np.zeros((rows, cols), dtype=bool)
        self.rewards = np.zeros((rows, cols), dtype=float)
        self.actions = np.zeros((rows, cols, numActions, 6), dtype=int)
        self.startingProbs = np.zeros((rows, cols), dtype=float)


