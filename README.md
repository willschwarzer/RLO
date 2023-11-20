# Interactive Gridworld Specification Tool
## Introduction
This is a prototype GUI to allow you to make gridworld MDPs and test various algorithms on them more easily than through code alone. First of all, it is a prototype, and there will be bugs! When you find any bugs that hinder your ability to use or install the program, please email Will the TA.

It currently supports the following features:
* Creating a gridworld with arbitrary dimensions by clicking or dragging on the grid to select open spaces
* Defining $R(s')$ reward functions
* Defining $d_0$
* Defining four actions to have any probability of transitioning to an adjacent state, staying still, or terminating. This can be done either manually or using slippery (East, South, West, North) actions with user-defined probabilities of slipping in each direction (or staying still or terminating)
* Defining $\gamma$
* Running value iteration on the MDP to determine $V^*$ and $\pi^*$
* Running Q-learning and SARSA with user-defined number of episodes, learning rate and exploration rate epsilon, outputting graphs
* 

## Installation
Start off by running `pip install -r requirements.txt` or `python -m pip install -r requirements.txt` to install the required packages. (It takes a while; sorry about that. We're using the `mushroom_rl` package for the Q-learning and SARSA algorithms, and it has way too many dependencies.) If you get an import error in opencv-python (cv2), please run `sudo apt install libgl1-mesa-glx` and try again - if that doesn't work or you're on Windows or Mac and still get this error, please email Will the TA.

## Usage
Run `python gridworld.py` to start the program. 
### Creating a Gridworld
You will be presented with a black screen; this represents every cell in the gridworld being a "wall" at the moment. To activate some cells and turn them into navigable spaces, simply click and drag. Note that agents can only transition to orthogonally adjacent cells, not diagonally adjacent ones. If you want to unselect cells (i.e., turn them back into walls), click the "unselect squares" button at the bottom.
### Defining the Reward Function
Click "specify rewards", then click on a cell, click on the text box at the bottom, enter a number (positive or negative), and press enter.
### Defining the Initial State Distribution
Click "specify start probabilities". Then the process is the same as for specifying rewards, except that the sum of the probabilities must be 1.0 - a message at the bottom tells you the current sum of the probabilities.
### Defining the Transition Function
Click "specify transition probabilities". To start, we recommend clicking the "Use slippery gridworld transitions" button, at which point you will be asked to input each of the slipping probabilities; you can just use the default values, which correspond to the 687-Gridworld values from the homework and lecture. This applies the given probabilities to action 0 as if it were "attempt right", action 1 as if it were "attempt down", and so on. Second, importantly, click on a cell that you want to be terminal, then click on the "set as terminal state" button on the bottom. (You can also set a certain probability of terminating either manually for each action in each state using the provided grid of text boxes or for all actions in all states by using the "slippery gridworld transitions" menu.) You don't need a terminal state, though; you can instead set a horizon in the algorithm hyperparameters menu, discussed next.
#### Visualizing the Transition Function
Click "Draw Transition Arrows" to visualize your defined transition function. Every arrow represents one of the possible transitions that the chosen action can produce in each state, with circles representing staying and crosses representing termination. If this looks messy, it's because the transitions are stochastic, so a lot of transitions are possible in each state with each action.
### Running algorithms
Click "Solve!". This menu is pretty self-explanatory! Note that after running SARSA/Q-learning, a return learning curve and an episode duration learning curve are automatically saved to `experiments/{date and time}`. A progress bar will also be shown in the terminal while SARSA/Q-learning are running; if they're taking too long, try decreasing the number of episodes or decreasing thhe horizon.
#### Visualizing the Policy
Note that the value function and policy shown will be the learned ones if you choose SARSA/Q-learning, or the optimal ones if you choose value iteration. Also, because the transition function may be user-defined, the shown arrows are the most likely transition given the agent's action.

## Accessibility
(TBD - we're working on this!)