import tkinter as tk
from tkinter import messagebox
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

def pack_things_in_order(show_reward=False, show_start_prob=False, show_mode_label=False, show_eraser=False, show_status=False, show_clear=False):
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
num_actions = 1
grid_state = Grid(GRID_HEIGHT, GRID_WIDTH, num_actions)

# Create labels for rewards and mode display
label_reward = tk.Label(root, text="Reward: 0.0")

label_start_prob = tk.Label(root, text="Start Probability: 0.0")
entry_start_prob = tk.Entry(root)

start_probs = np.zeros((GRID_HEIGHT, GRID_WIDTH))
start_weights = np.zeros((GRID_HEIGHT, GRID_WIDTH))

# Entry for setting rewards (only in reward mode)
entry_reward = tk.Entry(root)

# Create Arrows list to hold every arrow drawn
arrows = []

def cell_click(event, row, col):
    global selected_cell, highlighted_cell
    mode = modes[mode_var.get()]

    if mode == "Select Mode":
        grid_state.setActiveGridCoord(row, col, not eraser_active)
        if not grid_state.activeGrid[row, col]: # if no longer active, set reward to 0
            grid_state.setReward(row, col, 0.0)
        grid[row][col]['color'] = 'white' if grid_state.activeGrid[row, col] else 'black'
        update_grid()
    elif mode.lower() in ["start prob mode", "reward mode"]:
        # Unhighlight the previously selected cell
        selected_cell = (row, col)
        if highlighted_cell and (row, col) != highlighted_cell:
            prev_row, prev_col = highlighted_cell
            canvas.itemconfig(cells[prev_row][prev_col], width=1)  # Unhighlight the previous cell
        highlighted_cell = selected_cell
        # Highlight the newly selected cell
        canvas.itemconfig(cells[row][col], width=3)
        # For 'start prob mode', update the start probability label
        if mode.lower() == "start prob mode":
            label_start_prob.config(text=f"Start Probability: {start_probs[row, col]:.2f}")
        # For 'reward mode', update the reward label
        elif mode.lower() == "reward mode":
            label_reward.config(text=f"Reward: {grid_state.rewards[row, col]:.2f}")

# Transition Arrow Drawing
arrow_start_coord = None

def draw_arrow(start, end):
    x1, y1 = start
    x2, y2 = end

    # Calculate the coordinates for arrow positions
    x1_pixel = y1 * CELL_SIZE + CELL_SIZE // 2
    y1_pixel = x1 * CELL_SIZE + CELL_SIZE // 2
    x2_pixel = y2 * CELL_SIZE + CELL_SIZE // 2
    y2_pixel = x2 * CELL_SIZE + CELL_SIZE // 2

    # Draw the arrow
    arrow = canvas.create_line(x1_pixel, y1_pixel, x2_pixel, y2_pixel, arrow=tk.LAST)
    arrows.append(arrow)

def clear_arrows():
    for arrow in arrows:
        canvas.delete(arrow)
    arrows.clear()

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
        elif mode.lower() == "transition mode":
            global arrow_start_coord
            if arrow_start_coord is None:
                arrow_start_coord = (row, col)
            else:
                draw_arrow(arrow_start_coord, (row, col))
                arrow_start_coord = None
                

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
    if eraser_active:
        eraser_button.config(text="Select squares")
        mode_label.config(text="Currently erasing squares")
    else:
        eraser_button.config(text="Unselect squares")
        mode_label.config(text="Currently selecting squares")

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
        mode_label.config(text="Currently drawing arrows")
        pack_things_in_order(show_mode_label=True, show_eraser=True, show_clear=True)
        eraser_active = False
        eraser_button.config(text="Unselect Arrows")

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
            label_reward.config(text="Reward: 0.0")
            # Recalculate the maximum absolute reward
            global max_abs_reward
            max_abs_reward = np.abs(grid_state.rewards).max()
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
