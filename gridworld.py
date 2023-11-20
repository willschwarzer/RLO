import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import numpy as np
from model.grid import Grid
from matplotlib import pyplot as plt
import os
import datetime
from tqdm import tqdm

# Constants for grid dimensions and cell size
GRID_WIDTH = 10
GRID_HEIGHT = 10
CELL_SIZE = 40

# Create the main window
root = tk.Tk()
root.title("Gridworld Generator")

# Create a canvas for the grid
canvas = tk.Canvas(root, width=GRID_WIDTH * CELL_SIZE, height=GRID_HEIGHT * CELL_SIZE)

# Variables to store settings
colorblind_mode = tk.BooleanVar(value=False)
grid_size = tk.IntVar(value=20)

# Create menu bar
menubar = tk.Menu(root)
root.config(menu=menubar)

# Create a "Settings" dropdown menu
settings_menu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label="Settings", menu=settings_menu)

# Add options to the "Settings" dropdown
settings_menu.add_checkbutton(label="Enable Red-Green Colorblind Mode", variable=colorblind_mode)
'''settings_menu.add_separator()
settings_menu.add_radiobutton(label="Small Grid Size", variable=grid_size, value=5)
settings_menu.add_radiobutton(label="Medium Grid Size", variable=grid_size, value=10)
settings_menu.add_radiobutton(label="Large Grid Size", variable=grid_size, value=20)'''

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
                         show_solve_stuff=False):
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
    solve_button.pack_forget()
    solver_menu.pack_forget()
    show_value_function_button.pack_forget()
    show_optimal_policy_button.pack_forget()
    # gamma_entry.pack_forget()
    # gamma_label.pack_forget()
    alg_hyperparams_button.pack_forget()
    
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
    if show_solve_stuff:
        solver_menu.pack()
        # gamma_entry.pack()
        # pack gamma label to the left of the entry
        alg_hyperparams_button.pack()
        # gamma_label.grid(row=1, column=0)
        # gamma_entry.grid(row=1, column=1)
        solve_button.pack()
        # also show buttons for showing value and policy
        # show_value_function_button.grid(row=2, column=0, columnspan=1)
        # show_optimal_policy_button.grid(row=2, column=1, columnspan=1)
        show_value_function_button.pack()
        show_optimal_policy_button.pack()

# Determine the color based on reward value
def get_color_by_reward(reward):
    global max_abs_reward
    # Calculate saturation based on the magnitude of the reward
    saturation = abs(reward) / (max_abs_reward + 1e-6)
    base_color = good_color() if reward > 0 else (bad_color() if reward < 0 else 'white')
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


def good_color():
    return 'green' if not colorblind_mode.get() else 'blue'


def bad_color():
    return 'red' if not colorblind_mode.get() else 'yellow'


def get_color_by_value(value, max_abs_value):
    # Calculate saturation based on the magnitude of the value
    saturation = abs(value) / (max_abs_value + 1e-6)
    base_color = good_color() if value > 0 else (bad_color() if value < 0 else 'white')
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
    elif base_color == "yellow":
        # Full yellow, adjust blue
        r = 255
        g = 255
        additional_value = int(255 * (1 - saturation))
        b = additional_value
    else:
        return '#FFFFFF'  # Fallback to white if an unrecognized color is passed
    return f'#{r:02x}{g:02x}{b:02x}'  # Return the hex color code


# Initialize the grid with colors based on reward values
grid = [[{'color': get_color_by_reward(0.0), 'reward': 0.0} for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

# Variables to track the drawing and reward modes
arrows_visible = False
current_reward = 0.0

# Modes setup
modes = ["Select Mode", "Transition Mode", "Reward Mode", "Start Prob Mode", "Solve Mode"]
mode_text = ["Add/remove states", "Specify transition probabilities", "Specify rewards", "Specify start probabilities", "Solve!"]

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

standard_transition_probs = np.array([0.8, 0.0, 0.05, 0.05, 0.0, 0.1])

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
    move_right_var = tk.DoubleVar(value=standard_transition_probs[1])
    move_left_var = tk.DoubleVar(value=standard_transition_probs[2])
    move_down_var = tk.DoubleVar(value=standard_transition_probs[3])
    terminate_var = tk.DoubleVar(value=standard_transition_probs[4])
    stay_still_var = tk.DoubleVar(value=standard_transition_probs[5])

    prob_vars = [move_up_var, move_right_var, move_left_var, move_down_var, terminate_var, stay_still_var]

    # Function to update probabilities dynamically
    def update_probs(name, *args):
        # Handle negative probabilities
        for var in prob_vars[:-1]:
            try:
                if var.get() < 0:
                    var.set(0)
            except:
                var.set(0)
        
        total_move_prob = sum(var.get() for var in prob_vars[:-1])
        if total_move_prob > 1:
            # Find the variable that was just updated and adjust it
            updated_var = next((var for var in prob_vars[:-1] if var._name == name), None)
            if updated_var:
                updated_var.set(updated_var.get() - (total_move_prob - 1))
            total_move_prob = 1  # Recalculate total move probability

        # Format stay probability to display up to 5 significant digits
        stay_still_var.set(f"{1 - total_move_prob:.5g}")

    # Attach update function to each move probability variable
    for var in prob_vars[:-1]:  # Exclude stay_still_var as it is calculated
        var.trace('w', update_probs)

    # Create and layout labels and entries for probabilities
    directions = ["Move Forward", "Slip Backward", "Slip Left", "Slip Right"]
    for i, (direction, var) in enumerate(zip(directions, prob_vars)):
        tk.Label(action_window, text=direction).grid(row=i, column=0)
        entry = tk.Entry(action_window, textvariable=var)
        entry.grid(row=i, column=1)
        # if direction == "Stay Still":
        #     entry.config(state='readonly')  # Disable editing for Stay Still probability
    # Do terminate and stay still manually
    tk.Label(action_window, text="Terminate").grid(row=len(directions), column=0)
    entry = tk.Entry(action_window, textvariable=terminate_var)
    entry.grid(row=len(directions), column=1)

    tk.Label(action_window, text="Stay Still").grid(row=len(directions)+1, column=0)
    entry = tk.Entry(action_window, textvariable=stay_still_var, state='readonly')
    entry.grid(row=len(directions)+1, column=1)

    def apply_to_all_states():
        if messagebox.askokcancel("Confirmation", "Create four actions with these transitions for all states?"):
            save_standard_actions(*prob_vars)
            # update_ui()
            trans_prob_frame.load_probabilities()
            action_window.destroy()

    # Save and Close buttons
    save_button = tk.Button(action_window, text="Apply to all states", command=apply_to_all_states)
    save_button.grid(row=len(directions)+2, columnspan=2)
    tk.Button(action_window, text="Close", command=action_window.destroy).grid(row=len(directions) + 3, columnspan=2)



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

    # Also make it just draw to the line between the two cells
    # Either the two x values are the same or the two y values are the same
    # so we get the value that's the same and then set the other second pixel to be half way between the two
    if x1_pixel == x2_pixel:
        y2_pixel = y1_pixel + (y2_pixel - y1_pixel) // 2
    else:
        x2_pixel = x1_pixel + (x2_pixel - x1_pixel) // 2
    # Draw the arrow
    arrow = canvas.create_line(x1_pixel, y1_pixel, x2_pixel, y2_pixel, arrow=tk.LAST, fill='#BF40BF') # purple
    # canvas.tag_bind(arrow, '<Button-1>', lambda event, a=arrow: select_arrow(event, a))
    arrows[(x1_pixel,y1_pixel,x2_pixel,y2_pixel)] = arrow

def delete_arrows():
    keys = list(arrows.keys())
    for arrow_key in keys:
        if arrow_key[1] == 'stay':
            canvas.delete(arrows[arrow_key][0])
            canvas.delete(arrows[arrow_key][1])
        elif arrow_key[1] == 'terminate':
            canvas.delete(arrows[arrow_key][0])
            canvas.delete(arrows[arrow_key][1])
        else:
            canvas.delete(arrows[arrow_key])
        del arrows[arrow_key]

def delete_arrow(start, end):
    x1, y1 = start
    x2, y2 = end

    # Calculate the coordinates for arrow positions
    x1_pixel = y1 * CELL_SIZE + CELL_SIZE // 2
    y1_pixel = x1 * CELL_SIZE + CELL_SIZE // 2
    x2_pixel = y2 * CELL_SIZE + CELL_SIZE // 2
    y2_pixel = x2 * CELL_SIZE + CELL_SIZE // 2
    arrow_key = (x1_pixel,y1_pixel,x2_pixel,y2_pixel)
    # Draw the arrow
    if arrow_key in arrows.keys():
        canvas.delete(arrows[arrow_key])
        del arrows[arrow_key]

def draw_stay_arrow(cell):
    row, col = cell
    # Calculate the center of the cell
    center_x = col * CELL_SIZE + CELL_SIZE // 2
    center_y = row * CELL_SIZE + CELL_SIZE // 2

    # Define the radius for the arc (making it smaller)
    radius = CELL_SIZE // 6  # Reduced radius for a smaller arrow

    # Calculate the bounding box for the arc
    arc_start_x = center_x - radius
    arc_start_y = center_y - radius
    arc_end_x = center_x + radius
    arc_end_y = center_y + radius

    # Draw the arc (a larger circular arc for a more complete circle)
    arc = canvas.create_arc(arc_start_x, arc_start_y, arc_end_x, arc_end_y, start=30, extent=300, style=tk.ARC, outline='#BF40BF')  # Increased extent for a fuller circle

    # Add an arrowhead at the end of the arc
    # Calculate the coordinates for the arrowhead
    arrow_angle = 30 + 300  # Adjust the angle to match the end of the arc
    arrow_x = center_x + radius * np.cos(np.radians(arrow_angle))
    arrow_y = center_y - radius * np.sin(np.radians(arrow_angle))

    # Draw the arrowhead (as a small triangle)
    arrowhead = canvas.create_polygon(
        arrow_x, arrow_y + 3,  # Adjusted for the smaller arrow
        arrow_x - 3, arrow_y, 
        arrow_x + 3, arrow_y, 
        fill='#BF40BF'
    )

    arrows[cell, 'stay'] = (arc, arrowhead)  # Store the arrow components

def draw_terminate_arrow(cell):
    row, col = cell
    # draw an X through the middle ninth of the cell
    x1 = col * CELL_SIZE + CELL_SIZE // 3
    y1 = row * CELL_SIZE + CELL_SIZE // 3
    x2 = col * CELL_SIZE + 2 * CELL_SIZE // 3
    y2 = row * CELL_SIZE + 2 * CELL_SIZE // 3
    line1 = canvas.create_line(x1, y1, x2, y2, fill='#BF40BF')
    line2 = canvas.create_line(x1, y2, x2, y1, fill='#BF40BF')
    arrows[cell, 'terminate'] = (line1, line2)


def delete_stay_arrow(cell):
    if (cell, 'stay') in arrows:
        arc, arrowhead_line = arrows[cell, 'stay']
        canvas.delete(arc)
        canvas.delete(arrowhead_line)
        del arrows[cell, 'stay']

def delete_terminate_arrow(cell):
    if (cell, 'terminate') in arrows:
        line1, line2 = arrows[cell, 'terminate']
        canvas.delete(line1)
        canvas.delete(line2)
        del arrows[cell, 'terminate']


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
        self.prob_vars = [tk.StringVar(name=str(_), value="0.0") for _ in range(5)]  # For North, South, East, West, Terminate
        self.stay_prob_var = tk.StringVar(value="1.0")  # Stay probability

        # Create and pack the direction labels and entries in a grid layout
        self.entries = []
        directions = ["North", "South", "East", "West", "Terminate"]
        for i, direction in enumerate(directions):
            tk.Label(self, text=direction).grid(row=i//2, column=i%2*2, sticky=tk.W)
            entry = tk.Entry(self, textvariable=self.prob_vars[i], state='disabled')
            entry.grid(row=i//2, column=i%2*2+1)
            self.entries.append(entry)

        # Stay probability entry (read-only and initially disabled)
        tk.Label(self, text="Stay").grid(row=len(directions)//2, column=2, sticky=tk.W)
        self.stay_entry = tk.Entry(self, textvariable=self.stay_prob_var, state='readonly', disabledbackground='light grey')
        self.stay_entry.grid(row=len(directions)//2, column=3)

        # Attach the update function to the probability variables
        for prob_var in self.prob_vars:
            prob_var.trace("w", self.update_probs)

        standard_actions_button = tk.Button(self, text="Use Slippery Gridworld Transitions", command=open_standard_actions_settings)
        standard_actions_button.grid(row=3, columnspan=4)  # Adjust row and columnspan according to your layout

        # self.use_standard_action_probs_button = tk.Button(self, 
        #     text="Use Standard Action Probabilities", command=self.use_standard_action_probs, state='disabled')
        # self.use_standard_action_probs_button.grid(row=4, columnspan=4)

        terminal_button = tk.Button(self, text="Set as Terminal State", command=self.set_terminal_state)
        terminal_button.grid(row=4, columnspan=4)

        def arrow_clicked():
            global arrows_visible
            arrows_visible = not arrows_visible
            self.draw_arrow_button.config(text="Draw Transition Arrows" if not arrows_visible else "Hide Transition Arrows")
            self.draw_arrows()

        self.draw_arrow_button = tk.Button(self, text="Draw Transition Arrows", command=arrow_clicked)
        self.draw_arrow_button.grid(row=5, columnspan=4)

        self.updating = True

    def draw_arrows(self):
        global grid_state, arrows_visible
        delete_arrows()
        if arrows_visible:
            action = int(action_var.get().split()[-1])
            for row in range(GRID_HEIGHT):
                for col in range(GRID_WIDTH):
                    if grid_state.isActive(row, col):
                        # import pdb;pdb.set_trace()
                        probs = grid_state.actions[row, col, action, :]
                        # draw up arrow if state above is active
                        if row > 0 and grid_state.isActive(row-1, col):
                            if probs[0] > 0:
                                draw_arrow((row, col), (row-1, col))
                        # draw down arrow if state below is active
                        if row < GRID_HEIGHT-1 and grid_state.isActive(row+1, col):
                            if probs[1] > 0:
                                draw_arrow((row, col), (row+1, col))
                        # draw right arrow if state to the right is active
                        if col < GRID_WIDTH-1 and grid_state.isActive(row, col+1):
                            if probs[2] > 0:
                                draw_arrow((row, col), (row, col+1))
                        # draw left arrow if state to the left is active
                        if col > 0 and grid_state.isActive(row, col-1):
                            if probs[3] > 0:
                                draw_arrow((row, col), (row, col-1))
                        if probs[4] > 0:
                            draw_terminate_arrow((row, col))
                        if probs[-1] > 0:
                            draw_stay_arrow((row, col))

                        # How do we handle stay arrow?

    def set_terminal_state(self):
        global selected_cell
        if selected_cell is None:
            return
        row, col = selected_cell
        # self.prob_vars[4] = 1.0
        # self.stay_prob_var = 0.0
        # for i in range(4):
        #     self.prob_vars[i] = 0.0
        # probs = self.get_probabilities()
        probs = [0.0, 0.0, 0.0, 0.0, 1.0, 0.0]
        for action in range(num_actions):
            save_transitions(grid_state, row, col, action, probs)
        self.draw_arrows()
        self.load_probabilities()
        

    def use_standard_action_probs(self):
        global selected_cell, action_var
        if selected_cell is None or action_var.get() is None:
            return
        row, col = selected_cell
        action = int(action_var.get().split()[-1])
        for ind, prob in enumerate(standard_transition_probs[:-1]):
            self.prob_vars[ind].set(str(prob))
        self.stay_prob_var.set(str(standard_transition_probs[-1]))
        self.load_probabilities()
    

    def update_probs(self, name, *args):
        if not self.updating:
            return

        global selected_cell, action_var
        if selected_cell is None or action_var.get() is None:
            return
        row, col = selected_cell
        action = int(action_var.get().split()[-1])

        last_updated = int(name)
        probs = []
        for prob_var in self.prob_vars:
            try:
                probs.append(float(prob_var.get()))
            except:
                probs.append(0.0)

        #Make sure probability to invalid state is 0
        if not grid_state.isActive(row-1, col) and last_updated == 0 and probs[0] != 0:
            self.prob_vars[0].set(str(0.0))
            probs[0] = 0.0
        if not grid_state.isActive(row+1, col) and last_updated == 1 and probs[1] != 0:
            self.prob_vars[1].set(str(0.0))
            probs[1] = 0.0
        if not grid_state.isActive(row, col+1) and last_updated == 2 and probs[2] != 0:
            self.prob_vars[2].set(str(0.0))
            probs[2] = 0.0
        if not grid_state.isActive(row, col-1) and last_updated == 3 and probs[3] != 0:
            self.prob_vars[3].set(str(0.0))
            probs[3] = 0.0

        total_prob = sum(prob for prob in probs)
        
        if total_prob > 1:
            self.prob_vars[last_updated].set(f'{1-(total_prob - probs[last_updated]):.5g}')
            probs[last_updated] = 1 - (total_prob - probs[last_updated])
        elif total_prob < 0:
            self.prob_vars[last_updated].set(str(0.0))
            probs[last_updated] = 0.0
        stay_prob = max(0, 1 - total_prob)  # Ensure it doesn't go below 0
        self.stay_prob_var.set(f"{stay_prob:.5g}")

        # sum_probs = sum(prob_values)
        # if sum_probs > 1:
            # raise ValueError("Sum of probabilities for North, South, East, West, and Stay must not exceed 1.")
            # we don't want to raise an error, instead we want to 
        save_transitions(grid_state, row, col, action, probs + [stay_prob])
        if arrows_visible:
            self.draw_arrows()

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

        # Update the probability variables with the retrieved values
        for i in range(5):  # For North, South, East, West
            self.prob_vars[i].set(f"{probs[i]:.5g}")
        

        # Update the stay probability
        # self.stay_prob_var.set(str(probs[5]))
        self.stay_prob_var.set(f"{probs[5]:.5g}")

        # Update the terminate probability
        # self.prob_vars[4].set(f"{probs[4]:.5g}")
        self.updating = True
        self.draw_arrows() # XXX why the fresh heck am I doing this here?

    def enable_entries(self):
        global selected_cell
        if selected_cell is None:
            self.disable_entries()
            return
        row, col = selected_cell
        self.entries[4].config(state='normal')
        if not grid_state.isActive(row-1, col):
            self.entries[0].config(state='readonly')
        else:
            self.entries[0].config(state='normal')
        if not grid_state.isActive(row+1, col):
            self.entries[1].config(state='readonly')
        else:
            self.entries[1].config(state='normal')
        if not grid_state.isActive(row, col+1):
            self.entries[2].config(state='readonly')
        else:
            self.entries[2].config(state='normal')
        if not grid_state.isActive(row, col-1):
            self.entries[3].config(state='readonly')
        else:
            self.entries[3].config(state='normal')
        self.stay_entry.config(state='readonly')  # Stay entry should remain read-only
        # self.use_standard_action_probs_button.config(state='normal')

    def disable_entries(self):
        for entry in self.entries:
            entry.config(state='disabled')
        self.stay_entry.config(state='disabled')
        # self.use_standard_action_probs_button.config(state='disabled')

trans_prob_frame = TransitionProbabilitiesFrame(root)

action_var.trace("w", lambda *_: trans_prob_frame.load_probabilities())

# standard_actions_button = tk.Button(root, text="Set Standard Actions", command=open_standard_actions_settings)

def cell_click(event, row, col):
    global selected_cell, highlighted_cell
    mode = modes[mode_var.get()]

    if mode == "Select Mode":
        global optimal_policy, optimal_value_function, learned_policy, learned_value_function, showing_policy, showing_value_function
        showing_policy = False
        showing_value_function = False
        optimal_policy = None
        optimal_value_function = None
        learned_policy = None
        learned_value_function = None
        grid_state.setActiveGridCoord(row, col, not eraser_active)
        if not grid_state.isActive(row, col): # if no longer active, set reward to 0
            grid_state.setReward(row, col, 0.0)
            grid_state.setStartingProb(row, col, 0.0)
        grid[row][col]['color'] = 'white' if grid_state.isActive(row, col) else 'black'
        update_grid()
    elif mode.lower() in ["start prob mode", "reward mode", "transition mode"]:
        # Unhighlight the previously selected cell
        selected_cell = (row, col)
        # Exit if cell is inactive
        if not grid_state.isActive(row, col):
            return
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
                label_start_prob.config(text=f"Start Probability: {grid_state.startingProbs[row, col]:.2f}")
            else:
                label_start_prob.config(text="Start Probability: 0.00")
        # For 'reward mode', update the reward label
        elif mode.lower() == "reward mode":
            if selected_cell:
                label_reward.config(text=f"Reward: {grid_state.rewards[row, col]:.2f}")
            else:
                label_reward.config(text="Reward: 0.00")
        elif mode.lower() == "transition mode":
            if selected_cell and grid_state.isActive(row, col):
                trans_prob_frame.enable_entries()
                trans_prob_frame.load_probabilities()
            else:
                trans_prob_frame.disable_entries()
    # elif mode.lower() == "transition mode":
    #     # global arrow_start_coord
    #     # # Check if there is an arrow at the specified row and col
    #     # if arrow_start_coord is None and grid_state.isActive(row, col] and not eraser_active:
    #     #     # Unhighlight the previously selected cell
    #     #     selected_cell = (row, col)
    #     #     if highlighted_cell:
    #     #         prev_row, prev_col = highlighted_cell
    #     #         canvas.itemconfig(cells[prev_row][prev_col], width=1)  # Unhighlight the previous cell
    #     #     highlighted_cell = selected_cell
    #     #     # Highlight the newly selected cell
    #     #     canvas.itemconfig(cells[row][col], width=3)
    #     #     arrow_start_coord = (row, col)
    #     # elif arrow_start_coord is not None and grid_state.isActive(row, col] and (row, col) != arrow_start_coord and not eraser_active:
    #     #     # Remove highlighted cell
    #     #     if highlighted_cell:
    #     #         canvas.itemconfig(cells[highlighted_cell[0]][highlighted_cell[1]], width=1)
    #     #         highlighted_cell = None
    #     #         selected_cell = None
    #     #     draw_arrow(arrow_start_coord, (row, col))
    #     #     arrow_start_coord = None
    #     # elif arrow_start_coord is not None and grid_state.isActive(row, col] and (row, col) == arrow_start_coord:
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
    - prob_values: list of float, the probabilities for [North, South, East, West, Terminate, Stay]
    """
    # Ensure the sum of the first five probabilities (excluding the terminate probability) is <= 1

    # Save probabilities in the transitions array
    # except right now 
    grid.addActionList((row, col), action_index, prob_values)

def save_standard_actions(move_up_var, move_down_var, move_left_var, move_right_var, terminate_var, stay_still_var):
    forward_prob = move_up_var.get()
    backward_prob = move_down_var.get()
    slip_left_prob = move_left_var.get()
    slip_right_prob = move_right_var.get()
    stay_prob = stay_still_var.get()
    terminate_prob = terminate_var.get()
    standard_transition_probs[0] = forward_prob
    standard_transition_probs[1] = backward_prob
    standard_transition_probs[2] = slip_left_prob
    standard_transition_probs[3] = slip_right_prob
    standard_transition_probs[4] = terminate_prob
    standard_transition_probs[5] = stay_prob
    for action_index in range(4):  # Assuming 4 actions
        apply_standard_probabilities_to_action(action_index, standard_transition_probs)
    # total_prob = up_prob + down_prob + left_prob + right_prob + stay_prob + terminate_prob
    # so we don't need to check that sum is > 1
    # normalized_prob = [up_prob / total_prob,
    #                    down_prob / total_prob,
    #                    left_prob / total_prob,
    #                    right_prob / total_prob,
    #                    stay_prob / total_prob,
    #                    terminate_prob / total_prob]
    # standard_transition_probs[0] = normalized_prob[0]
    # standard_transition_probs[1] = normalized_prob[1]
    # standard_transition_probs[2] = normalized_prob[2]
    # standard_transition_probs[3] = normalized_prob[3]
    # standard_transition_probs[4] = normalized_prob[4]
    # standard_transition_probs[5] = normalized_prob[5]
    # convert this into concrete probs for action 0, going right

def apply_standard_probabilities_to_action(action_index, standard_transition_probs):
    for row in range(GRID_HEIGHT):
        for col in range(GRID_WIDTH):
            # Initialize probabilities
            probs = [0.0, 0.0, 0.0, 0.0, standard_transition_probs[4], standard_transition_probs[5]]
            # Check and set probabilities based on the active state of neighboring cells
            if action_index == 0:  # Attempt to go east
                probs[2] = standard_transition_probs[0] if col < GRID_WIDTH-1 and grid_state.isActive(row, col+1) else 0 # East (successfully moved forward)
                probs[1] = standard_transition_probs[3] if row < GRID_HEIGHT-1 and grid_state.isActive(row+1, col) else 0 # South (slipped right)
                probs[3] = standard_transition_probs[1] if col > 0 and grid_state.isActive(row, col-1) else 0 # West (slipped backward)
                probs[0] = standard_transition_probs[2] if row > 0 and grid_state.isActive(row-1, col) else 0 # North (slipped left)
            # ... [similar logic for actions 1, 2, and 3]
            if action_index == 1: # Attempt to go south
                probs[1] = standard_transition_probs[0] if row < GRID_HEIGHT-1 and grid_state.isActive(row+1, col) else 0 # South (successfully moved forward)
                probs[3] = standard_transition_probs[3] if col > 0 and grid_state.isActive(row, col-1) else 0 # West (slipped right)
                probs[0] = standard_transition_probs[1] if row > 0 and grid_state.isActive(row-1, col) else 0 # North (slipped backward)
                probs[2] = standard_transition_probs[2] if col < GRID_WIDTH-1 and grid_state.isActive(row, col+1) else 0 # East (slipped left)
            if action_index == 2: # Attempt to go west
                probs[3] = standard_transition_probs[0] if col > 0 and grid_state.isActive(row, col-1) else 0 # West (successfully moved forward)
                probs[0] = standard_transition_probs[3] if row > 0 and grid_state.isActive(row-1, col) else 0 # North (slipped right)
                probs[2] = standard_transition_probs[1] if col < GRID_WIDTH-1 and grid_state.isActive(row, col+1) else 0 # East (slipped backward)
                probs[1] = standard_transition_probs[2] if row < GRID_HEIGHT-1 and grid_state.isActive(row+1, col) else 0 # South (slipped left)
            if action_index == 3: # Attempt to go north
                probs[0] = standard_transition_probs[0] if row > 0 and grid_state.isActive(row-1, col) else 0 # North (successfully moved forward)
                probs[2] = standard_transition_probs[3] if col < GRID_WIDTH-1 and grid_state.isActive(row, col+1) else 0 # East (slipped right)
                probs[1] = standard_transition_probs[1] if row < GRID_HEIGHT-1 and grid_state.isActive(row+1, col) else 0 # South (slipped backward)
                probs[3] = standard_transition_probs[2] if col > 0 and grid_state.isActive(row, col-1) else 0 # West (slipped left)

            # Calculate the total move probability and adjust the stay probability
            total_move_prob = sum(probs[:5])  # Sum of the first four probabilities (excluding stay)
            remaining_prob = 1 - total_move_prob # Remaining probability for stay
            probs[5] = remaining_prob

            # Save the adjusted probabilities for the action
            grid_state.addActionList((row, col), action_index, probs)

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
        if not grid_state.isActive(row, col):
            return
        try:
            update_status("")
            prob = float(entry_start_prob.get())
            if not 0 <= prob <= 1:
                update_status("Probability must be between 0 and 1")
                return
            grid_state.setStartingProb(row, col, prob)
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
    prob_sum = np.sum(grid_state.startingProbs)
    if prob_sum > 0 and normalize:
        np.divide(grid_state.startingProbs, prob_sum, out=grid_state.startingProbs)
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
            if not grid_state.isActive(row, col): # if no longer active, set reward to 0
                grid_state.setReward(row, col, 0.0)
                grid_state.setStartingProb(row, col, 0.0)
            last_toggled_cell = current_cell
            update_grid()

                

def set_reward(event):
    global selected_cell
    mode = modes[mode_var.get()]
    if mode.lower() == "reward mode" and selected_cell:
        row, col = selected_cell
        if not grid_state.isActive(row, col):
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
    # show optimal value function if in solve mode and using Value Iteration
    if mode == "Solve Mode":
            if solver_menu.get() == 'Value Iteration':
                value_function = optimal_value_function
                policy = optimal_policy
            else:
                value_function = learned_value_function
                policy = learned_policy
            if value_function is not None:
                max_abs_value = np.abs(value_function).max()
    else:
        value_function = None

        #     max_abs_value = np.abs(optimal_value_function).max()
        # else:
        #     max_abs_value = np.abs(learned_value_function).max()
    for row in range(GRID_HEIGHT):
        for col in range(GRID_WIDTH):
            if grid_state.isActive(row, col):
                if mode == "Start Prob Mode":
                    # Normalize the start probability to [0, 1] for color saturation
                    saturation = grid_state.startingProbs[row, col] / max(grid_state.startingProbs.max(), 1)
                    cell_color = get_saturated_color("blue", saturation)
                elif mode == "Solve Mode" and showing_value_function and value_function is not None:
                    # Normalize the value function to [0, 1] for color saturation
                    cell_color = get_color_by_value(value_function[row, col], max_abs_value)
                else:
                    cell_color = get_color_by_reward(grid_state.rewards[row, col])
            else:
                cell_color = 'black'  # Set the color to black if the cell is unselected
            canvas.itemconfig(cells[row][col], fill=cell_color)
    if mode == "Solve Mode" and showing_policy:
        delete_arrows()
        draw_policy(policy)

            
def update_ui():
    global selected_cell, highlighted_cell, eraser_active, arrows_visible, showing_value_function
    update_grid()
    update_status("")
    mode = modes[mode_var.get()]
    delete_arrows()
    arrows_visible = False

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
        value = grid_state.startingProbs[selected_cell[0], selected_cell[1]] if selected_cell is not None else 0.0
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
        trans_prob_frame.enable_entries()
        # first clear existing arrows
        # clear_arrows()
        trans_prob_frame.load_probabilities() # note that this draws arrows
        # make sure that trans_prob_frame.dra
        trans_prob_frame.draw_arrow_button.config(text="Draw Transition Arrows" if not arrows_visible else "Hide Transition Arrows")
    elif mode.lower() == "solve mode":
        pack_things_in_order(show_solve_stuff=True)
        # button text
        show_optimal_policy_button.config(text="Hide Optimal Policy" if showing_policy else "Show Optimal Policy")
        # show policy if we're showing policy
        if showing_policy:
            show_policy()
    else:
        raise ValueError(f"Invalid mode: {mode}")

def clear():
    if messagebox.askokcancel("Confirmation", "Are you sure you want to clear?"):
        mode = modes[mode_var.get()]
        if mode.lower() == "start prob mode":
            grid_state.startingProbs.fill(0.0)
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

optimal_policy = None
optimal_value_function = None
learned_policy = None
learned_value_function = None

colorblind_mode.trace("w", lambda *_: update_grid())


def update_size(*args):
    canvas.config(width=grid_size.get() * CELL_SIZE, height=grid_size.get() * CELL_SIZE)
    global GRID_WIDTH, GRID_HEIGHT, optimal_policy, optimal_value_function, learned_policy, learned_value_function, showing_policy, showing_value_function
    showing_policy = False
    showing_value_function = False
    optimal_policy = None
    optimal_value_function = None
    learned_policy = None
    learned_value_function = None
    for row in range(grid_size.get()-1, GRID_HEIGHT):
        for col in range(grid_size.get()-1, GRID_WIDTH):
            grid_state.setActiveGridCoord(row, col, False)
            grid_state.setReward(row, col, 0.0)
            grid_state.setStartingProb(row, col, 0.0)
            grid[row][col]['color'] = 'black'
            print(grid_state.isActive(row, col))
    update_grid()
    print('huuh')


grid_size.trace("w", update_size)

def solve():
    global optimal_policy, optimal_value_function, learned_policy, learned_value_function
    update_status("")
    status_label.pack_forget()
    if solver_menu.get() == 'Value Iteration':
        optimal_policy, optimal_value_function, its = value_iteration(grid_state, discount_factor=gamma)
        if showing_value_function:
            update_grid()
        # also display the number of iterations
        update_status(f"Value iteration converged in {its} iterations", color="green")
        # pack the status label
        status_label.pack()
    else:
        # check if starting probs sum to 1
        if np.sum(grid_state.startingProbs) != 1.0:
            update_status(f"Illegal MDP: sum of starting probs is {np.sum(grid_state.startingProbs)}", color="red")
            # pack the status label
            status_label.pack()
            return
        # these imports take absolutely forever otherwise
        if 'Environment' not in globals():
            import_mushroom_globally()
        
        MushroomGridworld = define_gridworld()
        gridworld = MushroomGridworld(grid_state, gamma, horizon)
        # epsilon = Parameter(value=0.1)
        epsilon_param = Parameter(epsilon)
        policy = EpsGreedy(epsilon=epsilon_param)
        # learning_rate = Parameter(value=0.1)
        learning_rate_param = Parameter(learning_rate)
        if solver_menu.get() == 'Q-Learning':
            agent = QLearning(mdp_info=gridworld.info, 
                                policy=policy,
                                learning_rate=learning_rate_param,)
        elif solver_menu.get() == 'SARSA':
            agent = SARSA(mdp_info=gridworld.info, 
                                policy=policy,
                                learning_rate=learning_rate_param,)
        else:
            update_status(f"Invalid algorithm: {solver_menu.get()}", color="red")
            # pack the status label
            status_label.pack()
            return
        # agent.Q = Table(gridworld.info.size, initial_q)
        # this apparently doesn't work, so we'll go and set the Q table manually
        for row in range(GRID_HEIGHT):
            for col in range(GRID_WIDTH):
                agent.Q.table[GRID_WIDTH * row + col] = initial_q
        core = Core(agent, gridworld)
        # for epoch in range(num_epochs):
        # num_epochs = 1000  # Total number of epochs
        episodes_per_epoch = 1  # Number of episodes per epoch

        rets = []
        durations = []
        for epoch in tqdm(range(num_epochs)):
            core.learn(n_episodes=episodes_per_epoch, n_steps_per_fit=1, quiet=True)  # Learn from specified number of episodes
            evaluation_results = core.evaluate(n_episodes=1)  # Evaluate the agent's performance
            ave_ret, ave_duration = calculate_episode_stats(evaluation_results, gamma)  # Calculate the average return
            rets.append(ave_ret)  # Append the average return to the learning curve
            durations.append(ave_duration)  # Append the average duration to the learning curve

        # Plot the learning curve
        plot_learning_curves(rets, durations, solver_menu.get())
        # core.learn(n_episodes=1000, n_steps_per_fit=1)  # Learn from 1 episode at a time
        # histories = core.evaluate(n_episodes=10)
        # # breakpoint()
        # # ave_ret = np.mean([step[2] for step in histories])
        # ave_ret = calculate_average_episode_return(histories, gamma)
        # update_status(f"Agent's average return: {ave_ret:.5g}", color="green")
        # status_label.pack()
        # # breakpoint()

        # save the policy and value function
        # we need to unflatten the agent's Q table first
        flat_q_table = agent.Q.table
        q_table = np.zeros((GRID_HEIGHT, GRID_WIDTH, 4))
        for row in range(GRID_HEIGHT):
            for col in range(GRID_WIDTH):
                    q_table[row, col] = flat_q_table[GRID_WIDTH * row + col]
                    # take the max over actions
        v_table = np.max(q_table, axis=2)
        learned_value_function = v_table
        # because of the way we visualize the policy, it can actually just be the Q function
        learned_policy = q_table

def plot_learning_curves(learning_curve, durations, algorithm):
    # Ensure the 'experiments' folder exists
    folder_name = "experiments"
    os.makedirs(folder_name, exist_ok=True)
    # Generate a filename based on the current time
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    ret_filename = f"{folder_name}/{algorithm}_learning_curve_{timestamp}.png"
    dur_filename = f"{folder_name}/{algorithm}_durations_{timestamp}.png"

    # Create and save the plot
    plt.figure()
    plt.plot(durations)
    plt.xlabel('Episodes')
    plt.ylabel('Duration')
    # plt.title('Duration Curve for ' + algorithm)
    # add hyperparameters to title
    plt.title(f"Duration Curve for {algorithm} (gamma={gamma}, epsilon={epsilon}, learning_rate={learning_rate})")
    plt.savefig(dur_filename)

    # Create and save the plot
    plt.figure()
    plt.plot(learning_curve)
    plt.xlabel('Episodes')
    plt.ylabel('Return')
    # plt.title('Learning Curve for ' + algorithm)
    # add hyperparameters to title
    plt.title(f"Learning Curve for {algorithm} (gamma={gamma}, epsilon={epsilon}, learning_rate={learning_rate})")
    plt.savefig(ret_filename)

    # Update the status to indicate where the file was saved
    update_status(f"Saved learning curve to {ret_filename}", color="green")
    status_label.pack()

    # try to show the plot
    try:
        plt.show()
    except:
        return

def calculate_episode_stats(evaluation_history, gamma):
    episode_returns = []
    episode_durations = []
    episode_return = 0
    timestep = 0

    for step in evaluation_history:
        reward = step[2]  # Assuming the reward is the third element in the step tuple
        episode_return += (gamma ** timestep) * reward
        timestep += 1

        if step[-1]:  # Assuming "done" is the last element in the step tuple
            episode_returns.append(episode_return)
            episode_return = 0  # Reset for the next episode
            episode_durations.append(timestep)
            timestep = 0  # Reset timestep for the next episode

    average_return = sum(episode_returns) / len(episode_returns) if episode_returns else 0
    average_duration = sum(episode_durations) / len(episode_durations) if episode_durations else 0
    return average_return, average_duration

def import_mushroom_globally():
    # Importing the necessary modules
    # Doing it here because it takes a long time to import
    # and it will give a bad impression of the program if
    # it takes a long time to start up
    print("Running first-time import of MushroomRL (this may take a while)")
    from mushroom_rl.core import Environment, MDPInfo
    from mushroom_rl.core.agent import Agent
    from mushroom_rl.algorithms.value import QLearning, SARSA
    from mushroom_rl.policy import EpsGreedy
    from mushroom_rl.utils.parameters import Parameter
    from mushroom_rl.core import Core
    from mushroom_rl.utils.spaces import Discrete
    from mushroom_rl.utils.table import Table
    print("Done importing MushroomRL")

    # Adding them to the global namespace
    globals()['Environment'] = Environment
    globals()['MDPInfo'] = MDPInfo
    globals()['Agent'] = Agent
    globals()['QLearning'] = QLearning
    globals()['SARSA'] = SARSA
    globals()['EpsGreedy'] = EpsGreedy
    globals()['Parameter'] = Parameter
    globals()['Core'] = Core
    globals()['Discrete'] = Discrete
    globals()['Table'] = Table

def define_gridworld():
    class MushroomGridworld(Environment):
        def __init__(self, grid_state, gamma, horizon):
            self.gridworld = grid_state
            n_states = 100
            n_actions = 4

            # Define the state and action spaces
            self._state_space = Discrete(n_states)
            self._action_space = Discrete(n_actions)

            # Define the reward range and discount factor
            # reward_range = (-1, 1)  # Example: rewards range between -1 and 1
            # calculate actual reward range
            min_rew = np.min(self.gridworld.rewards)
            max_rew = np.max(self.gridworld.rewards)
            # reward_range = (min_rew, max_rew)
            horizon = horizon # It seems that we don't need to store this except for the MDPInfo

            # Set the MDP information
            self._mdp_info = MDPInfo(self._state_space, 
                                     self._action_space, 
                                     gamma, 
                                     horizon,)
                                    #  reward_range,)

            self.reset()

        def reset(self, state=None):
            """
            Reset the environment to an initial state.

            The state is chosen randomly based on the starting probabilities.
            If a specific state is provided, the environment is reset to that state.
            """
            if state is not None:
                # Reset to the specified state
                initial_state = state
            else:
                # Choose a random initial state based on starting probabilities
                flattened_probs = self.gridworld.startingProbs.flatten()
                initial_state = np.random.choice(len(flattened_probs), p=flattened_probs)

            self.current_state = self._unflatten_state(initial_state)

            return np.array([initial_state])

        def step(self, action):
            """
            Execute the given action and update the environment's state.

            Parameters:
            action - the action to be executed in the environment

            Returns:
            next_state, reward, done, info - where next_state is the new state after the action,
                                            reward is the reward received from the action,
                                            done is a boolean indicating whether the episode is finished,
                                            and info is an optional dictionary with debug information.
            """
            current_row, current_col = self.current_state

            # MushroomRL gives actions as np arrays :P
            if isinstance(action, np.ndarray):
                action = action.item()

            # Choose the direction based on the action and the transition probabilities
            direction = np.random.choice(6, p=self.gridworld.actions[current_row, current_col, action])

            done = (direction == 4)

            # Get the next state based on the chosen direction
            next_row, next_col = self.gridworld.getNextState(current_row, current_col, direction)

            # Check if the next state is active, if not, stay in the current state
            if not self.gridworld.isActive(next_row, next_col):
                next_row, next_col = current_row, current_col

            # Calculate the reward
            if done:
                reward = 0
            else:
                reward = self.gridworld.getReward(next_row, next_col)

            # Update the current state
            self.current_state = (next_row, next_col)
            flattened_state = self._flatten_state(self.current_state)

            # Optional additional information
            info = {}  # You can add any additional debug info here

            return np.array([flattened_state]), reward, done, info

        def _flatten_state(self, state):
            """
            Convert a 2D state (row, col) to a 1D state.

            Parameters:
            state - a tuple (row, col) representing the state in 2D

            Returns:
            An integer representing the flattened state
            """
            row, col = state
            return row * self.gridworld.cols + col

        def _unflatten_state(self, state):
            """
            Convert a 1D state to a 2D state (row, col).

            Parameters:
            state - an integer representing the flattened state

            Returns:
            A tuple (row, col) representing the state in 2D
            """
            row = state // self.gridworld.cols
            col = state % self.gridworld.cols
            return row, col

        @property
        def info(self):
            # Return an MDPInfo object describing the environment
            return self._mdp_info
        
    return MushroomGridworld

num_epochs = 1000
learning_rate = 0.1
epsilon = 0.1
gamma = 0.9
initial_q = 0.0
horizon = 100

def show_alg_hyperparams_menu():
    global num_epochs, learning_rate, epsilon, gamma, initial_q, horizon
    # Create a new top-level window
    hyperparams_window = tk.Toplevel(root)
    hyperparams_window.title("Algorithm Hyperparameters")

    # Hyperparameters to be set
    # num_epochs_var = tk.IntVar(value=1000)  # Default number of epochs
    # learning_rate_var = tk.DoubleVar(value=0.1)  # Default learning rate
    # epsilon_var = tk.DoubleVar(value=0.1)  # Default epsilon for EpsGreedy
    # gamma_var = tk.DoubleVar(value=0.9)  # Default gamma
    num_epochs_var = tk.IntVar(value=num_epochs)  # Default number of epochs
    learning_rate_var = tk.DoubleVar(value=learning_rate)  # Default learning rate
    epsilon_var = tk.DoubleVar(value=epsilon)  # Default epsilon for EpsGreedy
    gamma_var = tk.DoubleVar(value=gamma)  # Default gamma
    initial_q_var = tk.DoubleVar(value=initial_q)  # Default initial Q value
    horizon_var = tk.IntVar(value=horizon)  # Default horizon

    # Function to update hyperparameters
    def update_hyperparams():
        global num_epochs, learning_rate, epsilon, gamma, initial_q, horizon
        num_epochs = num_epochs_var.get()
        learning_rate = learning_rate_var.get()
        epsilon = epsilon_var.get()
        gamma = gamma_var.get()
        initial_q = initial_q_var.get()
        horizon = horizon_var.get()
        hyperparams_window.destroy()

    # Validation functions
    def validate_num_epochs(*args):
        try:
            if num_epochs_var.get() < 1:
                num_epochs_var.set(1)
        except:
            # num_epochs_var.set(1000)  # Reset to default if invalid input
            pass

    def validate_learning_rate(*args):
        try:
            value = learning_rate_var.get()
            # if not 0 < value < 1:
            #     learning_rate_var.set(0.1)
            if value > 1:
                learning_rate_var.set(1.0)
            elif value < 0:
                learning_rate_var.set(0.0)
        except:
            # learning_rate_var.set(0.1)  # Reset to default if invalid input
            pass

    def validate_epsilon(*args):
        try:
            value = epsilon_var.get()
            # if not 0 < value < 1:
            #     epsilon_var.set(0.1)
            if value > 1:
                epsilon_var.set(1.0)
            elif value < 0:
                epsilon_var.set(0.0)
        except:
            # epsilon_var.set(0.1)  # Reset to default if invalid input
            pass

    def validate_gamma(*args):
        try:
            value = gamma_var.get()
            if value > 1:
                gamma_var.set(1.0)
            elif value < 0:
                gamma_var.set(0.0)
        except:
            # gamma_var.set(0.9)  # Reset to default if invalid input
            pass

    def validate_initial_q(*args):
        try:
            initial_q_var.get()
        except:
            pass

    def validate_horizon(*args):
        try:
            value = horizon_var.get()
            if value < 1:
                horizon_var.set(1)
        except:
            pass

    # Attaching the validation function to the trace method of variables
    num_epochs_var.trace('w', validate_num_epochs)
    learning_rate_var.trace('w', validate_learning_rate)
    epsilon_var.trace('w', validate_epsilon)
    gamma_var.trace('w', validate_gamma)
    initial_q_var.trace('w', validate_initial_q)
    horizon_var.trace('w', validate_horizon)

    # Creating labels and entry widgets for each hyperparameter
    tk.Label(hyperparams_window, text="Number of Episodes:").grid(row=0, column=0)
    tk.Entry(hyperparams_window, textvariable=num_epochs_var).grid(row=0, column=1)

    tk.Label(hyperparams_window, text="Horizon length").grid(row=1, column=0)
    tk.Entry(hyperparams_window, textvariable=horizon_var).grid(row=1, column=1)

    tk.Label(hyperparams_window, text="Learning Rate:").grid(row=2, column=0)
    tk.Entry(hyperparams_window, textvariable=learning_rate_var).grid(row=2, column=1)

    tk.Label(hyperparams_window, text="Epsilon:").grid(row=3, column=0)
    tk.Entry(hyperparams_window, textvariable=epsilon_var).grid(row=3, column=1)

    tk.Label(hyperparams_window, text="Initial Q Values:").grid(row=4, column=0)
    tk.Entry(hyperparams_window, textvariable=initial_q_var).grid(row=4, column=1)

    tk.Label(hyperparams_window, text="Gamma:").grid(row=5, column=0)
    tk.Entry(hyperparams_window, textvariable=gamma_var).grid(row=5, column=1)

    # Button to update hyperparameters
    update_button = tk.Button(hyperparams_window, text="Update Hyperparameters", command=update_hyperparams)
    update_button.grid(row=6, columnspan=2)


def value_iteration(grid_state, discount_factor=0.9, theta=0.0001):
    """
    Perform value iteration algorithm.

    Parameters:
    - grid_state: Grid object containing rewards and transition probabilities
    - discount_factor: Gamma, the discount factor for future rewards
    - theta: A threshold for determining the accuracy of the estimation

    Returns:
    - policy: The optimal policy
    - V: The value function
    """
    V = np.zeros((GRID_HEIGHT, GRID_WIDTH))  # Initialize value function
    its = 0
    while True and its < 10000:
        delta = 0
        for row in range(GRID_HEIGHT):
            for col in range(GRID_WIDTH):
                if not grid_state.isActive(row, col):
                    continue
                v = V[row, col]
                # precompute the value for each direction
                # to avoid recomputing it for each action
                direction_values = []
                for direction in range(6):
                    # (terminate transition has no reward/value)
                    new_row, new_col = grid_state.getNextState(row, col, direction)
                    if not grid_state.isActive(new_row, new_col):
                        direction_values.append(None)
                        continue
                    direction_value = grid_state.getReward(new_row, new_col) + discount_factor * V[new_row, new_col]
                    direction_values.append(direction_value)
                # just manually set the terminate transition value to 0
                direction_values[4] = 0
                action_values = []
                for action in range(grid_state.numActions):
                    # actually do a direction loop here
                    # that way we can continue if the direction is invalid
                    action_value = 0
                    for direction in range(6):
                        new_row, new_col = grid_state.getNextState(row, col, direction)
                        if not grid_state.isActive(new_row, new_col):
                            continue
                        action_value += grid_state.getTransitionProb(row, col, action, direction) * direction_values[direction]
                    action_values.append(action_value)
                V[row, col] = max(action_values)
                delta = max(delta, abs(v - V[row, col]))
        its += 1
        if delta < theta:
            break

    # Derive policy from value function
    policy = np.zeros((GRID_HEIGHT, GRID_WIDTH, grid_state.numActions))
    for row in range(GRID_HEIGHT):
        for col in range(GRID_WIDTH):
            if not grid_state.isActive(row, col):
                continue
            direction_values = []
            for direction in range(6):
                # (terminate transition has no reward/value)
                new_row, new_col = grid_state.getNextState(row, col, direction)
                if not grid_state.isActive(new_row, new_col):
                    direction_values.append(None)
                    continue
                direction_value = grid_state.getReward(new_row, new_col) + discount_factor * V[new_row, new_col]
                direction_values.append(direction_value)
            # just manually set the terminate transition value to 0
            direction_values[4] = 0
            action_values = []
            for action in range(grid_state.numActions):
                # actually do a direction loop here
                # that way we can continue if the direction is invalid
                action_value = 0
                for direction in range(5):
                    new_row, new_col = grid_state.getNextState(row, col, direction)
                    if not grid_state.isActive(new_row, new_col):
                        continue
                    action_value += grid_state.getTransitionProb(row, col, action, direction) * direction_values[direction]
                action_values.append(action_value)
            # terminate transition has no reward/value
            action_values.append(action_value)
            best_action = np.argmax(action_values)
            policy[row, col, best_action] = 1

    return policy, V, its

showing_policy = False

def draw_policy(policy):
    for row in range(GRID_HEIGHT):
        for col in range(GRID_WIDTH):
            if grid_state.isActive(row, col):
                best_action = np.argmax(policy[row, col, :])
                # figure out which direction is most likely after taking the best action
                transition_probs = grid_state.actions[row, col, best_action, :]
                direction = np.argmax(transition_probs)
                draw_policy_arrow(row, col, direction)

def show_policy():
    global arrows_visible, showing_policy
    if solver_menu.get() == 'Value Iteration':
        policy = optimal_policy
    else:
        policy = learned_policy
    if policy is None:
        messagebox.showinfo("Info", "Please solve the gridworld first!")
        return

    # first clear previous policy arrows and transition arrows
    delete_arrows()
    # also change the arrow button in transition mode to say "Draw Transition Arrows"

    # trans_prob_frame.draw_arrow_button.config(text="Draw Transition Arrows")
    # config(text="Draw Transition Arrows")
    # arrows not visible
    arrows_visible = True

    showing_policy = not showing_policy

    if showing_policy:
        draw_policy(policy)
        # change the button text
        show_optimal_policy_button.config(text="Hide Policy")
    else:
        # change the button text
        show_optimal_policy_button.config(text="Show Policy")
    arrows_visible = False

showing_value_function = False

def show_value_function():
    global showing_value_function
    showing_value_function = not showing_value_function
    # change the button text
    if showing_value_function:
        show_value_function_button.config(text="Hide Value Function")

        if solver_menu.get() == 'Value Iteration':
            d_0 = grid_state.startingProbs
            if not np.any(d_0):
                update_status("Please set starting probabilities to see J*", color="green")
                status_label.pack()
            else:
                J_star = np.sum(d_0 * optimal_value_function)
                update_status(f"J* = {J_star}", color="green")
                status_label.pack()
    else:
        show_value_function_button.config(text="Show Value Function")
        # if the status label is showing J*, hide it
        if "J*" in status_label.cget("text"):
            update_status("")
            status_label.pack_forget()
    update_grid()

def draw_policy_arrow(row, col, action):
    # assuming 0 = east, 1 = south, 2 = west, 3 = north
    # if action == 0:
    #     draw_arrow((row, col), (row, col+1))
    # elif action == 1:
    #     draw_arrow((row, col), (row+1, col))
    # elif action == 2:
    #     draw_arrow((row, col), (row, col-1))
    # elif action == 3:
    #     draw_arrow((row, col), (row-1, col))
    # assuming 0 = north, 1 = south, 2 = east, 3 = west
    if action == 0:
        draw_arrow((row, col), (row-1, col))
    elif action == 1:
        draw_arrow((row, col), (row+1, col))
    elif action == 2:
        draw_arrow((row, col), (row, col+1))
    elif action == 3:
        draw_arrow((row, col), (row, col-1))
    elif action == 4:
        draw_terminate_arrow((row, col))
    elif action == 5:
        draw_stay_arrow((row, col))

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

solve_button = tk.Button(root, text="Solve!", command=solve)

solver_menu = ttk.Combobox(root, values=['Value Iteration', 'SARSA', 'Q-Learning'])
solver_menu.current(0)

# text field for setting gamma/discount factor

# gamma = 0.9
# gamma_var = tk.StringVar(value=f"{gamma:.5g}")
# def update_gamma(name, *args):
#     global gamma
#     # Handle negative probabilities
#     try:
#         gamma = float(gamma_var.get())
#         if gamma < 0:
#             gamma = 0.0
#             gamma_var.set(f"{gamma:.5g}")
#         if gamma > 1:
#             gamma = 1.0
#             gamma_var.set(f"{gamma:.5g}")
#     except:
#         pass
# # just use a trace
# gamma_entry = tk.Entry(root, textvariable=gamma_var)
# gamma_var.trace("w", update_gamma)

# label for gamma text field
# gamma_label = tk.Label(root, text="Discount Factor (Gamma):")

show_optimal_policy_button = tk.Button(root, text="Show Policy", command=show_policy)
show_value_function_button = tk.Button(root, text="Show Value Function", command=show_value_function)

alg_hyperparams_button = tk.Button(root, text="Modify Algorithm Hyperparameters", command=show_alg_hyperparams_menu)

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
