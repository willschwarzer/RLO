# Interactive Gridworld Specification Tool
## Introduction
This is a prototype GUI to allow you to make gridworld MDPs and test various algorithms on them more easily than through code alone. First of all, it is a prototype, and there will be bugs! When you find any bugs that hinder your ability to use or install the program, please email Will the TA.

It currently supports the following features:
* Creating a gridworld with up to 100 squares by clicking or dragging on the grid to select open spaces
* Defining $R(s')$ reward functions
* Defining $d_0$
* Defining four actions to have any probability of transitioning to an adjacent state, staying still, or terminating. This can be done either manually or using default slippery actions in every state (see below for details).
* Defining $\gamma$
* Running value iteration on the MDP to determine $V^\*$ and $\pi^\*$
* Running Q-learning and SARSA with user-defined number of episodes, learning rate, exploration rate epsilon, episode horizon, and initial Q values, outputting graphs at the end

## Installation
Start off by running `pip install -r requirements.txt` or `python -m pip install -r requirements.txt` to install the required packages. (It takes a while; sorry about that. We're using the `mushroom_rl` package for the Q-learning and SARSA algorithms, and it has way too many dependencies.) 

If you get an import error in opencv-python (cv2), please run `sudo apt install libgl1-mesa-glx` and try again - if that doesn't work or you're on Windows or Mac and still get this error, please email Will the TA.

## Usage
Run `python gridworld.py` to start the program. **IMPORTANT**: there is currently no saving functionality, so try to do all of your work with a single MDP in one sitting, or don't close the program. Sorry.
### Creating a Gridworld
You will be presented with a black screen; this represents every cell in the gridworld being a "wall" at the moment. To activate some cells and turn them into navigable spaces, simply click and drag. Note that agents can only transition to orthogonally adjacent cells, not diagonally adjacent ones. If you want to unselect cells (i.e., turn them back into walls), click the "unselect squares" button at the bottom.
### Defining the Reward Function
Click "specify rewards", then click on a cell, click on the text box at the bottom, enter a number (positive or negative), and press enter.
### Defining the Initial State Distribution
Click "specify start probabilities". Then the process is the same as for specifying rewards, except that the sum of the probabilities must be 1.0 - a message at the bottom tells you the current sum of the probabilities.
### Defining the Transition Function
Click "specify transition probabilities". To start, we recommend clicking the "Set Default Transition Probabilities" button, at which point you will be asked to input each of the slipping probabilities; you can just use the default values, which correspond to the 687-Gridworld values from the homework and lecture. This applies the given probabilities to action 0 as if it were "attempt right", action 1 as if it were "attempt down", and so on. Second, importantly, click on a cell that you want to be terminal, then click on the "set as terminal state" button on the bottom. (You can also set a certain probability of terminating either manually for each action in each state using the provided grid of text boxes or for all actions in all states by using the "Set Default Transition Probabilities" menu.) You don't need a terminal state, though; you can instead set a horizon in the algorithm hyperparameters menu, discussed next.

**Important**: every time you use the "Set Default Transition Probabilities" button, all transition probabilities are reset to their default values, *including* termination probabilities. You will have to reset the terminal states each time you use this button. Sorry.

#### An example of how the default transition probabilities menu works
Let's say you want to set the default transition probabilities to be the 687-Gridworld values from the homework and lecture. You would click the "Set Default Transition Probabilities" button, then enter the following values:
* Forward: 0.8. This means that the agent has an 80% chance of moving in the direction it attempts to move in. Thus, action 0, attempt right, will move it to the right with 80% probability when it is possible to do so, and so on.
* Slip right: 0.05. This means that the agent has a 5% chance of moving one direction clockwise from the direction it attempts to move in. Thus, action 0, attempt right, will move it down with 5% probability when it is possible to do so, and so on.
* Slip left: 0.05. Similar to slip right, but counterclockwise.
* Slip backwards: 0. This is not used in the 687-Gridworld, but the idea is similar: the agent has a 0% chance of moving in the opposite direction from the direction it attempts to move in.
* Stay: 0.1. This means that the agent has a 10% chance of staying in the same place, added to the probabilities of transitions that hit a wall or go out of bounds.
* Terminate: 0. This allows a constant probability of terminating at every time step. You can actually prove that you only need either this probability or $\gamma$: you never need to set both. Do you see why?
#### Visualizing the Transition Function
Click "Draw Transition Arrows" to visualize your defined transition function. Every arrow represents one of the possible transitions that the chosen action can produce in each state, with circles representing staying and crosses representing termination. If this looks messy, it's because the transitions are stochastic, so a lot of transitions are possible in each state with each action.
### Running algorithms
Click "Solve!". This menu is pretty self-explanatory! Note that after running SARSA/Q-learning, a return learning curve and an episode duration learning curve are automatically saved to `experiments/{date and time}`. A progress bar will also be shown in the terminal while SARSA/Q-learning are running; if they're taking too long, try decreasing the number of episodes or decreasing thhe horizon.
#### Visualizing the Policy
Note that the value function and policy shown will be the learned ones if you choose SARSA/Q-learning, or the optimal ones if you choose value iteration. Also, because the transition function may be user-defined, the shown arrows are the most likely transition given the agent's action.

## Accessibility
Click on settings --> Enable Red-Green Colorblind Mode to replace red and green with blue and yellow.
