import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import numpy as np
from model.grid import Grid

# Constants for grid dimensions and cell size
GRID_WIDTH = 10
GRID_HEIGHT = 10
CELL_SIZE = 40

# Create the main window
root = tk.Tk()
root.title("Gridworld Game")

# Create a canvas for the grid
canvas = tk.Canvas(root, width=GRID_WIDTH * CELL_SIZE, height=GRID_HEIGHT * CELL_SIZE)

# Create a 2D list to store the cell items
cells = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

max_abs_reward = 1.0

def pack_things_in_order(show_reward=False, 
                         show_start_prob=False, 
                         show_mode_label=False, 
                         show_eraser=False, 
                         show_status=False, 
                         show_clear=False, 
                         show_action_menu=False,
                         show_transition_table=False,
                         show_standard_actions=False):
    for r in radio_buttons:
        r.pack(anchor='w')
    canvas.pack()

    # first forget everything
    mode_label.pack_forget()
    label_reward.pack_forget()
    entry_reward.pack_forget()
    label_start_prob.pack_forget()
    entry_start_prob.pack_forget()
    eraser_button.pack_forget()
    clear_button.pack_forget()
    status_label.pack_forget()
    action_menu.pack_forget()
    trans_prob_frame.pack_forget()

    
    if show_action_menu:
        action_menu.pack()
    if show_mode_label:
        mode_label.pack()
    if show_reward:
        label_reward.pack()
        entry_reward.pack()
    if show_start_prob:
        label_start_prob.pack()
        entry_start_prob.pack()
    if show_eraser:
        eraser_button.pack()
    if show_status:
        status_label.pack()
    if show_clear:
        clear_button.pack()
    if show_transition_table:
        trans_prob_frame.pack()

# Determine the color based on reward value
def get_color_by_reward(reward):
    global max_abs_reward
    # Calculate saturation based on the magnitude of the reward
    saturation = abs(reward) / (max_abs_reward + 1e-6)
    base_color = 'green' if reward > 0 else ('red' if reward < 0 else 'white')
    if base_color == 'white':
        return base_color
    return get_saturated_color(base_color, saturation)

# Helper function to get saturated color
def get_saturated_color(base_color, saturation):
    # Ensure lightness is between 0 and 1
    saturation = max(0, min(saturation, 1))

    # Initialize RGB values
    r, g, b = 0, 0, 0

    if base_color == "green":
        # Full green, adjust red and blue
        g = 255
        additional_value = int(255 * (1 - saturation))
        r = additional_value
        b = additional_value
    elif base_color == "red":
        # Full red, adjust green and blue
        r = 255
        additional_value = int(255 * (1 - saturation))
        g = additional_value
        b = additional_value
    elif base_color == "blue":
        # Full blue, adjust red and green
        b = 255
        additional_value = int(255 * (1 - saturation))
        r = additional_value
        g = additional_value
    else:
        return '#FFFFFF'  # Fallback to white if an unrecognized color is passed
    return f'#{r:02x}{g:02x}{b:02x}'  # Return the hex color code


# Initialize the grid with colors based on reward values
grid = [[{'color': get_color_by_reward(0.0), 'reward': 0.0} for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

# Variables to track the drawing and reward modes
drawing = False
reward_mode = False

# Determine the color based on reward value
def get_color_by_reward(reward):
    global max_abs_reward
    # Calculate saturation based on the magnitude of the reward
    saturation = abs(reward) / (max_abs_reward + 1e-6)
    base_color = 'green' if reward > 0 else ('red' if reward < 0 else 'white')
    if base_color == 'white':
        return base_color
    return get_saturated_color(base_color, saturation)

# Helper function to get saturated color
def get_saturated_color(base_color, saturation):
    # Ensure lightness is between 0 and 1
    saturation = max(0, min(saturation, 1))

    # Initialize RGB values
    r, g, b = 0, 0, 0

    if base_color == "green":
        # Full green, adjust red and blue
        g = 255
        additional_value = int(255 * (1 - saturation))
        r = additional_value
        b = additional_value
    elif base_color == "red":
        # Full red, adjust green and blue
        r = 255
        additional_value = int(255 * (1 - saturation))
        g = additional_value
        b = additional_value
    elif base_color == "blue":
        # Full blue, adjust red and green
        b = 255
        additional_value = int(255 * (1 - saturation))
        r = additional_value
        g = additional_value
    else:
        return '#FFFFFF'  # Fallback to white if an unrecognized color is passed
    return f'#{r:02x}{g:02x}{b:02x}'  # Return the hex color code


# Initialize the grid with colors based on reward values
grid = [[{'color': get_color_by_reward(0.0), 'reward': 0.0} for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

# Variables to track the drawing and reward modes
drawing = False
reward_mode = False
current_reward = 0.0

# Modes setup
modes = ["Select Mode", "Transition Mode", "Reward Mode", "Start Prob Mode"]
mode_text = ["Add/remove states", "Specify transition probabilities", "Specify rewards", "Specify start probabilities"]

eraser_active = False
# eraser_active.set(False)  # Default to not erasing

mode_var = tk.IntVar()
mode_var.set(0)  # Default to Select Mode

last_toggled_cell = None  # Keep track of the last toggled cell to prevent flickering

selected_cell = None  # Variable to keep track of the selected cell
highlighted_cell = None  # Variable to keep track of the highlighted cell

# Initialize the grid state to handle internal logic
num_actions = 4
grid_state = Grid(GRID_HEIGHT, GRID_WIDTH, num_actions)

# Create labels for rewards and mode display
label_reward = tk.Label(root, text="Reward: 0.00")

label_start_prob = tk.Label(root, text="Start Probability: 0.00")
entry_start_prob = tk.Entry(root)

start_probs = np.zeros((GRID_HEIGHT, GRID_WIDTH))
start_weights = np.zeros((GRID_HEIGHT, GRID_WIDTH))

standard_transition_probs = np.array([0.2, 0.2, 0.2, 0.2, 0.2, 0.0])

# Entry for setting rewards (only in reward mode)
entry_reward = tk.Entry(root)

action_var = tk.StringVar()
action_menu = ttk.Combobox(root, textvariable=action_var, state='readonly')
action_menu['values'] = ['Action ' + str(i) for i in range(num_actions)]  # Assuming actions are indexed from 0
action_menu.current(0)  # Set the default action

def open_standard_actions_settings():
    action_window = tk.Toplevel(root)
    action_window.title("Standard Actions Settings")

    # Variables for action probabilities
    move_up_var = tk.DoubleVar(value=standard_transition_probs[0])
    move_right_var = tk.DoubleVar(value=standard_transition_probs[1])  # Default values can be adjusted
    move_left_var = tk.DoubleVar(value=standard_transition_probs[2])
    move_down_var = tk.DoubleVar(value=standard_transition_probs[3])
    stay_still_var = tk.DoubleVar(value=standard_transition_probs[4])
    terminate_var = tk.DoubleVar(value=standard_transition_probs[5])

    # Create and layout labels and entries for probabilities
    tk.Label(action_window, text="Move Up Probability").grid(row=0, column=0)
    tk.Entry(action_window, textvariable=move_up_var).grid(row=0, column=1)

    tk.Label(action_window, text="Move Backwards Probability").grid(row=1, column=0)
    tk.Entry(action_window, textvariable=move_down_var).grid(row=1, column=1)

    tk.Label(action_window, text="Move Left Probability").grid(row=2, column=0)
    tk.Entry(action_window, textvariable=move_left_var).grid(row=2, column=1)

    tk.Label(action_window, text="Move Right Probability").grid(row=3, column=0)
    tk.Entry(action_window, textvariable=move_right_var).grid(row=3, column=1)

    tk.Label(action_window, text="Stay Still Probability").grid(row=4, column=0)
    tk.Entry(action_window, textvariable=stay_still_var).grid(row=4, column=1)

    tk.Label(action_window, text="Terminate Probability").grid(row=5, column=0)
    tk.Entry(action_window, textvariable=terminate_var).grid(row=5, column=1)

    # Save button
    tk.Button(action_window, text="Save", command=lambda: save_standard_actions(
        move_up_var, move_down_var, move_left_var, move_right_var, stay_still_var, terminate_var
    )).grid(row=6, columnspan=2)

    # Close button
    tk.Button(action_window, text="Close", command=action_window.destroy).grid(row=7, columnspan=2)

# Create Arrows list to hold every arrow drawn
arrows = {}

# Transition Arrow Drawing
arrow_start_coord = None
selected_arrow = None

def draw_arrow(start, end):
    x1, y1 = start
    x2, y2 = end

    # Calculate the coordinates for arrow positions
    x1_pixel = y1 * CELL_SIZE + CELL_SIZE // 2
    y1_pixel = x1 * CELL_SIZE + CELL_SIZE // 2
    x2_pixel = y2 * CELL_SIZE + CELL_SIZE // 2
    y2_pixel = x2 * CELL_SIZE + CELL_SIZE // 2
    # Draw the arrow
    arrow = canvas.create_line(x1_pixel, y1_pixel, x2_pixel, y2_pixel, arrow=tk.LAST, fill='#BF40BF') # purple
    canvas.tag_bind(arrow, '<Button-1>', lambda event, a=arrow: select_arrow(event, a))
    arrows[[x1_pixel,y1_pixel,x2_pixel,y2_pixel]] = arrow

def delete_arrow(start, end):
    x1, y1 = start
    x2, y2 = end

    # Calculate the coordinates for arrow positions
    x1_pixel = y1 * CELL_SIZE + CELL_SIZE // 2
    y1_pixel = x1 * CELL_SIZE + CELL_SIZE // 2
    x2_pixel = y2 * CELL_SIZE + CELL_SIZE // 2
    y2_pixel = x2 * CELL_SIZE + CELL_SIZE // 2
    arrow_key = [x1_pixel,y1_pixel,x2_pixel,y2_pixel]
    # Draw the arrow
    if arrow_key in arrows.keys():
        canvas.delete(arrows[arrow_key])
        del arrows[arrow_key]

def select_arrow(event, arrow):
    global selected_arrow
    # Highlight the selected arrow (e.g., change its color)
    if selected_arrow:
        # Deselect the previously selected arrow (change its color back)
        canvas.itemconfig(selected_arrow, fill="#BF40BF")
    if eraser_active:
        # Find the key in arrow_dict corresponding to the arrow
        arrow_key = next((k for k, v in arrows.items() if v == arrow), None)
        if arrow_key:
            canvas.delete(arrow)
            # Remove the arrow from the tracking dictionary
            del arrows[arrow_key]
        return
    selected_arrow = arrow
    canvas.itemconfig(selected_arrow, fill="#FF0000")  # Highlight the selected arrow


def clear_arrows():
    global arrows
    global arrow_start_coord
    arrow_start_coord = None
    for arrow in arrows.keys():
        canvas.delete(arrows[arrow])
        del arrows[arrow]
    # arrows.clear()

class TransitionProbabilitiesFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        # Variables for probabilities
        # self.prob_vars = [tk.DoubleVar(value=0.0) for _ in range(5)]  # For North, South, East, West, Terminate
        # have it be a string var instead to avoid errors
        self.prob_vars = [tk.StringVar(name=str(_), value="0.0") for _ in range(5)] # For North, South, East, West, Terminate
        self.stay_prob_var = tk.StringVar(value="1.0")  # Stay probability

        # Create and pack the direction labels and entries
        self.entries = []

        for i, direction in enumerate(["North", "South", "East", "West", "Terminate"]):
            tk.Label(self, text=direction).pack()
            entry = tk.Entry(self, textvariable=self.prob_vars[i], state='disabled')  # Initially disabled
            entry.pack()
            self.entries.append(entry)

        # Stay probability entry (read-only and initially disabled)
        tk.Label(self, text="Stay").pack()
        self.stay_entry = tk.Entry(self, textvariable=self.stay_prob_var, state='readonly', disabledbackground='light grey')
        self.stay_entry.pack()

        # Attach the update function to the probability variables
        for prob_var in self.prob_vars:
            prob_var.trace("w", self.update_probs)

        standard_actions_button = tk.Button(self, text="Set Standard Action Probabilities", command=open_standard_actions_settings)
        standard_actions_button.pack()

        self.use_standard_action_probs_button = tk.Button(self, 
            text="Use Standard Action Probabilities", command=self.use_standard_action_probs, state='disabled')
        self.use_standard_action_probs_button.pack()

        draw_arrow_button = tk.Button(self, text="Draw Missing Transition Arrows", command=self.draw_arrows)
        draw_arrow_button.pack()

        self.updating = True

    def draw_arrows(self):
        global grid_state
        for row in range(GRID_HEIGHT):
            for col in range(GRID_WIDTH):
                if grid_state.activeGrid[row, col]:
                    action = int(action_var.get().split()[-1])
                    probs = grid_state.actions[row, col, action, :]
                    # draw up arrow if state above is active
                    if row > 0 and grid_state.activeGrid[row-1, col]:
                        if probs[0] > 0:
                            draw_arrow((row, col), (row-1, col))
                        else:
                            delete_arrow((row, col), (row-1, col))
                    # draw down arrow if state below is active
                    if row < GRID_HEIGHT-1 and grid_state.activeGrid[row+1, col]:
                        if probs[1] > 0:
                            draw_arrow((row, col), (row+1, col))
                        else:
                            delete_arrow((row, col), (row+1, col))
                    # draw right arrow if state to the right is active
                    if col < GRID_WIDTH-1 and grid_state.activeGrid[row, col+1]:
                        if probs[2] > 0:
                            draw_arrow((row, col), (row, col+1))
                        else:
                            delete_arrow((row, col), (row, col+1))
                    # draw left arrow if state to the left is active
                    if col > 0 and grid_state.activeGrid[row, col-1]:
                        if probs[3] > 0:
                            draw_arrow((row, col), (row, col-1))
                        else:
                            delete_arrow((row, col), (row, col-1))

                    # How do we handle stay arrow?


    def use_standard_action_probs(self):
        global selected_cell, action_var
        if selected_cell is None or action_var.get() is None:
            return
        row, col = selected_cell
        action = int(action_var.get().split()[-1])
        save_transitions(grid_state, row, col, action, standard_transition_probs)
        self.load_probabilities()
    

    def update_probs(self, name, *args):
        if not self.updating:
            return
        last_updated = int(name)
        probs = []
        for prob_var in self.prob_vars:
            try:
                probs.append(float(prob_var.get()))
            except:
                probs.append(0.0)
        total_prob = sum(prob for prob in probs)
        if total_prob > 1:
            self.prob_vars[last_updated].set(f'{1-(total_prob - probs[last_updated]):.5g}')
        elif total_prob < 0:
            self.prob_vars[last_updated].set(str(0.0))
        stay_prob = max(0, 1 - total_prob)  # Ensure it doesn't go below 0
        self.stay_prob_var.set(f"{stay_prob:.5g}")

        # modify the numpy array
        global selected_cell, action_var
        if selected_cell is None or action_var.get() is None:
            return
        row, col = selected_cell
        action = int(action_var.get().split()[-1])

        # sum_probs = sum(prob_values)
        # if sum_probs > 1:
            # raise ValueError("Sum of probabilities for North, South, East, West, and Stay must not exceed 1.")
            # we don't want to raise an error, instead we want to 

        save_transitions(grid_state, row, col, action, probs + [stay_prob])

    def get_probabilities(self):
        # Method to retrieve the probability values
        return [var.get() for var in self.prob_vars] + [float(self.stay_prob_var.get())]

    def load_probabilities(self):
        self.updating = False
        global selected_cell, action_var
        if selected_cell is None or action_var.get() is None:
            return  # Do nothing if no cell or action is selected

        row, col = selected_cell
        action = int(action_var.get().split()[-1])

        # Assuming you have a method in your model to get probabilities
        # Replace this with your actual method to retrieve probabilities
        probs = grid_state.actions[row, col, action, :]
        print(probs)

        # Update the probability variables with the retrieved values
        for i in range(5):  # For North, South, East, West, Terminate
            self.prob_vars[i].set(f"{probs[i]:.5g}")

        # Update the stay probability
        # self.stay_prob_var.set(str(probs[5]))
        self.stay_prob_var.set(f"{probs[5]:.5g}")
        self.updating = True

    def enable_entries(self):
        for entry in self.entries:
            entry.config(state='normal')
        self.stay_entry.config(state='readonly')  # Stay entry should remain read-only
        self.use_standard_action_probs_button.config(state='normal')

    def disable_entries(self):
        for entry in self.entries:
            entry.config(state='disabled')
        self.stay_entry.config(state='disabled')
        self.use_standard_action_probs_button.config(state='disabled')

trans_prob_frame = TransitionProbabilitiesFrame(root)

action_var.trace("w", lambda *_: trans_prob_frame.load_probabilities())

# standard_actions_button = tk.Button(root, text="Set Standard Actions", command=open_standard_actions_settings)

def cell_click(event, row, col):
    global selected_cell, highlighted_cell
    mode = modes[mode_var.get()]

    if mode == "Select Mode":
        grid_state.setActiveGridCoord(row, col, not eraser_active)
        if not grid_state.activeGrid[row, col]: # if no longer active, set reward to 0
            grid_state.setReward(row, col, 0.0)
        grid[row][col]['color'] = 'white' if grid_state.activeGrid[row, col] else 'black'
        update_grid()
    elif mode.lower() in ["start prob mode", "reward mode", "transition mode"]:
        # Unhighlight the previously selected cell
        selected_cell = (row, col)
        if highlighted_cell is not None:
            prev_row, prev_col = highlighted_cell
            canvas.itemconfig(cells[prev_row][prev_col], width=1)  # Unhighlight the previous cell
        if highlighted_cell is None or (row, col) != highlighted_cell:
            highlighted_cell = selected_cell
            # Highlight the newly selected cell
            canvas.itemconfig(cells[row][col], width=3)
        else:
            highlighted_cell = None
            selected_cell = None
        # For 'start prob mode', update the start probability label
        if mode.lower() == "start prob mode":
            if selected_cell:
                label_start_prob.config(text=f"Start Probability: {start_probs[row, col]:.2f}")
            else:
                label_start_prob.config(text="Start Probability: 0.00")
        # For 'reward mode', update the reward label
        elif mode.lower() == "reward mode":
            if selected_cell:
                label_reward.config(text=f"Reward: {grid_state.rewards[row, col]:.2f}")
            else:
                label_reward.config(text="Reward: 0.00")
        elif mode.lower() == "transition mode":
            if selected_cell and grid_state.activeGrid[row, col]:
                trans_prob_frame.enable_entries()
                trans_prob_frame.load_probabilities()
            else:
                trans_prob_frame.disable_entries()
    # elif mode.lower() == "transition mode":
    #     # global arrow_start_coord
    #     # # Check if there is an arrow at the specified row and col
    #     # if arrow_start_coord is None and grid_state.activeGrid[row, col] and not eraser_active:
    #     #     # Unhighlight the previously selected cell
    #     #     selected_cell = (row, col)
    #     #     if highlighted_cell:
    #     #         prev_row, prev_col = highlighted_cell
    #     #         canvas.itemconfig(cells[prev_row][prev_col], width=1)  # Unhighlight the previous cell
    #     #     highlighted_cell = selected_cell
    #     #     # Highlight the newly selected cell
    #     #     canvas.itemconfig(cells[row][col], width=3)
    #     #     arrow_start_coord = (row, col)
    #     # elif arrow_start_coord is not None and grid_state.activeGrid[row, col] and (row, col) != arrow_start_coord and not eraser_active:
    #     #     # Remove highlighted cell
    #     #     if highlighted_cell:
    #     #         canvas.itemconfig(cells[highlighted_cell[0]][highlighted_cell[1]], width=1)
    #     #         highlighted_cell = None
    #     #         selected_cell = None
    #     #     draw_arrow(arrow_start_coord, (row, col))
    #     #     arrow_start_coord = None
    #     # elif arrow_start_coord is not None and grid_state.activeGrid[row, col] and (row, col) == arrow_start_coord:
    #     #     # Remove highlighted cell
    #     #     if highlighted_cell:
    #     #         canvas.itemconfig(cells[highlighted_cell[0]][highlighted_cell[1]], width=1)
    #     #         highlighted_cell = None
    #     #         selected_cell = None

    #     #show_transition_table(row, col, action_var.get())
    #     selected_cell = (row, col)
    #     trans_prob_frame.load_probabilities()

def save_transitions(grid, row, col, action_index, prob_values):
    """
    Save the transition probabilities for a given cell and action.

    Parameters:
    - row: int, the row index of the cell
    - col: int, the column index of the cell
    - action_index: int, the index of the action
    - prob_values: list of float, the probabilities for [North, South, East, West, Stay, Terminate]
    """
    # Ensure the sum of the first five probabilities (excluding the terminate probability) is <= 1

    # Save probabilities in the transitions array
    grid.addActionList((row, col), action_index, prob_values)

def save_standard_actions(move_up_var, move_down_var, move_left_var, move_right_var, stay_still_var, terminate_var):
    total_prob = 0
    up_prob = move_up_var.get()
    down_prob = move_down_var.get()
    left_prob = move_left_var.get()
    right_prob = move_right_var.get()
    stay_prob = stay_still_var.get()
    terminate_prob = terminate_var.get()
    total_prob = up_prob + down_prob + left_prob + right_prob + stay_prob + terminate_prob
    # so we don't need to check that sum is > 1
    normalized_prob = [up_prob / total_prob,
                       down_prob / total_prob,
                       left_prob / total_prob,
                       right_prob / total_prob,
                       stay_prob / total_prob,
                       terminate_prob / total_prob]
    standard_transition_probs[0] = normalized_prob[0]
    standard_transition_probs[1] = normalized_prob[1]
    standard_transition_probs[2] = normalized_prob[2]
    standard_transition_probs[3] = normalized_prob[3]
    standard_transition_probs[4] = normalized_prob[4]
    standard_transition_probs[5] = normalized_prob[5]

#TODO delete
def show_transition_table_old(row, col, action):
    # Close any existing transition table windows
    # ... (code to handle closing of a previously opened window)

    trans_window = tk.Toplevel(root)
    trans_window.title(f"Transition Probabilities for State ({row}, {col}) and {action}")

    # Add an extra label for the stay probability
    stay_prob_var = tk.DoubleVar(value=1.0)
    tk.Label(trans_window, text="Stay").grid(row=5, column=0)
    tk.Entry(trans_window, textvariable=stay_prob_var, state='readonly').grid(row=5, column=1)

    def update_stay_prob(*args):
        # Update stay probability based on other probabilities
        total_prob = sum(prob.get() for prob in probs)
        stay_prob = max(0, 1 - total_prob)  # Ensure it doesn't go below 0
        stay_prob_var.set(stay_prob)

    # Assuming 6 possible outcomes as mentioned
    outcomes = ["North", "South", "East", "West", "Terminate"]
    probs = [tk.DoubleVar(value=0.0) for _ in outcomes]  # Example initialization
    for i, outcome in enumerate(outcomes):
        tk.Label(trans_window, text=outcome).grid(row=i, column=0)
        entry = tk.Entry(trans_window, textvariable=probs[i])
        entry.grid(row=i, column=1)
        probs[i].trace("w", update_stay_prob)  # Add trace to update stay probability

def set_start_prob(event):
    global selected_cell
    mode = modes[mode_var.get()]
    if mode.lower() == "start prob mode" and selected_cell:
        row, col = selected_cell
        if not grid_state.activeGrid[row, col]:
            return
        try:
            update_status("")
            prob = float(entry_start_prob.get())
            if not 0 <= prob <= 1:
                update_status("Probability must be between 0 and 1")
                return
            start_probs[row, col] = prob
            # normalize_start_probs()
            # not normalizing for now
            check_start_probs(normalize=False)
            
            label_start_prob.config(text=f"Start Probability: {prob:.2f}")
            entry_start_prob.delete(0, tk.END)
            selected_cell = None
            update_grid()
        except ValueError as e:
            # tk.messagebox.showerror("Invalid Input", str(e))
            update_status("Invalid input")

def check_start_probs(normalize=False):
    prob_sum = np.sum(start_probs)
    if prob_sum > 0 and normalize:
        np.divide(start_probs, prob_sum, out=start_probs)
        return
    if prob_sum > 1:
        update_status(f"Sum of start probabilities: {prob_sum:.2f}", color="orange")
    elif prob_sum < 1:
        update_status(f"Sum of start probabilities: {prob_sum:.2f}", color="blue")
    else:
        update_status(f"Sum of start probabilities: {prob_sum:.2f}", color="green")

# Function to draw while dragging (for coloring)
def draw(event):
    global last_toggled_cell
    col = event.x // CELL_SIZE
    row = event.y // CELL_SIZE

    if 0 <= col < GRID_WIDTH and 0 <= row < GRID_HEIGHT:
        mode = modes[mode_var.get()]
        current_cell = (row, col)
        if mode == "Select Mode" and current_cell != last_toggled_cell:
            grid_state.setActiveGridCoord(row, col, not eraser_active)
            if not grid_state.activeGrid[row, col]: # if no longer active, set reward to 0
                grid_state.setReward(row, col, 0.0)
            last_toggled_cell = current_cell
            update_grid()
                

def set_reward(event):
    global selected_cell
    mode = modes[mode_var.get()]
    if mode.lower() == "reward mode" and selected_cell:
        row, col = selected_cell
        if not grid_state.activeGrid[row, col]:
            return
        try:
            reward = float(entry_reward.get())
            grid_state.setReward(row, col, reward)

            # Recalculate the maximum absolute reward
            global max_abs_reward
            max_abs_reward = np.abs(grid_state.rewards).max()

            for r in range(GRID_HEIGHT):
                for c in range(GRID_WIDTH):
                    grid[r][c]['color'] = get_color_by_reward(grid_state.rewards[r, c])

            label_reward.config(text=f"Reward: {reward:.2f}")

            entry_reward.delete(0, tk.END)
            update_grid()
            canvas.itemconfig(cells[row][col], width=1)
            selected_cell = None
        except ValueError:
            pass


# Function to start drawing or setting rewards
def start_drawing(event):
    mode = modes[mode_var.get()]
    if mode == "Select Mode":
        global drawing
        drawing = True

def stop_drawing(event):
    mode = modes[mode_var.get()]
    if mode == "Select Mode":
        global drawing
        drawing = False

def toggle_eraser():
    global eraser_active
    eraser_active = not eraser_active
    # Update button and label texts based on the mode
    mode = modes[mode_var.get()]
    if mode.lower() == "select mode":
        if eraser_active:
            eraser_button.config(text="Select squares")
            mode_label.config(text="Currently erasing squares")
        else:
            eraser_button.config(text="Unselect squares")
            mode_label.config(text="Currently selecting squares")
    elif mode.lower() == "transition mode":
        if eraser_active:
            eraser_button.config(text="Create transition arrows")
            mode_label.config(text="Currently erasing arrows")
        else:
            eraser_button.config(text="Delete transition arrows")
            mode_label.config(text="Currently drawing arrows")

# Function to update the grid display
def update_grid():
    mode = modes[mode_var.get()]
    for row in range(GRID_HEIGHT):
        for col in range(GRID_WIDTH):
            if grid_state.activeGrid[row, col]:
                if mode == "Start Prob Mode":
                    # Normalize the start probability to [0, 1] for color saturation
                    saturation = start_probs[row, col] / max(start_probs.max(), 1)
                    cell_color = get_saturated_color("blue", saturation)
                else:
                    cell_color = get_color_by_reward(grid_state.rewards[row, col])
            else:
                cell_color = 'black'  # Set the color to black if the cell is unselected
            canvas.itemconfig(cells[row][col], fill=cell_color)
            
def update_ui():
    global selected_cell, highlighted_cell, eraser_active
    update_grid()
    update_status("")
    mode = modes[mode_var.get()]
    if mode.lower() == "reward mode":
        # label_reward.pack()
        # entry_reward.pack()
        # label_start_prob.pack_forget()
        # entry_start_prob.pack_forget()
        # eraser_button.pack_forget()
        value = grid_state.rewards[selected_cell[0], selected_cell[1]] if selected_cell is not None else 0.0
        label_reward.config(text=f"Reward: {value:.2f}")
        entry_reward.delete(0, tk.END)
        pack_things_in_order(show_reward=True, show_clear=True)
    elif mode.lower() == "start prob mode":
        # label_start_prob.pack()
        # entry_start_prob.pack()
        # label_reward.pack_forget()
        # entry_reward.pack_forget()
        # eraser_button.pack_forget()
        # check if start probs sum to 1
        value = start_probs[selected_cell[0], selected_cell[1]] if selected_cell is not None else 0.0
        label_start_prob.config(text=f"Start Probability: {value:.2f}")
        entry_start_prob.delete(0, tk.END)
        check_start_probs(normalize=False)
        pack_things_in_order(show_start_prob=True, show_clear=True, show_status=True)
    elif mode.lower() == "select mode":
        # label_reward.pack_forget()
        # entry_reward.pack_forget()
        # label_start_prob.pack_forget()
        # entry_start_prob.pack_forget()

        # if mode == "Select Mode":
        #     eraser_button.pack()
        # else:
        #     eraser_button.pack_forget()
        # update mode label to say "Currently selecting squares"
        mode_label.config(text="Currently selecting squares")
        pack_things_in_order(show_mode_label=True, show_eraser=True)
        eraser_active = False
        eraser_button.config(text="Unselect squares")

        if highlighted_cell:
            row, col = highlighted_cell
            canvas.itemconfig(cells[row][col], width=1)
            highlighted_cell = None
        selected_cell = None
    elif mode.lower() == "transition mode":
        # mode_label.config(text="Currently drawing arrows")
        # # pack_things_in_order(show_mode_label=True, show_eraser=True, show_clear=True)
        # eraser_active = False
        # eraser_button.config(text="Delete transition arrows")

        # pack_things_in_order(show_mode_label=True, show_eraser=True, show_clear=True, show_action_menu=True)
        pack_things_in_order(show_action_menu=True, show_transition_table=True)

def clear():
    if messagebox.askokcancel("Confirmation", "Are you sure you want to clear?"):
        mode = modes[mode_var.get()]
        if mode.lower() == "start prob mode":
            start_probs.fill(0.0)
            check_start_probs(normalize=False)
        elif mode.lower() == "reward mode":
            grid_state.rewards.fill(0.0)
            for r in range(GRID_HEIGHT):
                for c in range(GRID_WIDTH):
                    grid[r][c]['color'] = get_color_by_reward(grid_state.rewards[r, c])
            label_reward.config(text="Reward: 0.00")
            # Recalculate the maximum absolute reward
            global max_abs_reward
            max_abs_reward = np.abs(grid_state.rewards).max()
        elif mode.lower() == 'transition mode':
            clear_arrows()
        update_grid()

def update_status(message, color="red"):
    if message:
        status_label.config(text=message, fg=color)  # Set the message and color
        # status_label.pack()  # Show the label with the message
    # else:
    #     status_label.pack_forget()  # Hide the label if there's no message

radio_buttons = []

# for idx, m in enumerate(modes):
for idx, m in enumerate(mode_text):
    r = tk.Radiobutton(root, text=m, variable=mode_var, value=idx, command=update_ui)
    radio_buttons.append(r)
    # r.pack(anchor='w')

mode_label = tk.Label(root, text="Currently selecting squares")

eraser_button = tk.Button(root, text="Unselect squares", command=toggle_eraser)

clear_button = tk.Button(root, text="Clear all", command=clear)

status_label = tk.Label(root, text="", fg="red")

# Hide reward-related UI at the start
update_ui()

# Bind the Enter key to the reward entry
entry_reward.bind('<Return>', set_reward)

entry_start_prob.bind('<Return>', set_start_prob)

# Populate the grid and bind click events
for row in range(GRID_HEIGHT):
    for col in range(GRID_WIDTH):
        x1, y1 = col * CELL_SIZE, row * CELL_SIZE
        x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
        cell_color = 'black'
        cell = canvas.create_rectangle(x1, y1, x2, y2, fill=cell_color, outline='black')
        cells[row][col] = cell
        canvas.tag_bind(cell, '<Button-1>', lambda event, r=row, c=col: cell_click(event, r, c))

update_grid()

# Bind mouse events for drawing (coloring)
canvas.bind('<Button-1>', start_drawing)
canvas.bind('<ButtonRelease-1>', stop_drawing)
canvas.bind('<B1-Motion>', draw)

# Start the application
root.mainloop()
