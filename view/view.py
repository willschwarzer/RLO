import tkinter as tk
import numpy as np
from model.grid import Grid

# Constants for grid dimensions and cell size
GRID_WIDTH = 10
GRID_HEIGHT = 10
CELL_SIZE = 40

# Create the main window
root = tk.Tk()
root.title("Gridworld Game")

max_abs_reward = 1.0

# Determine the color based on reward value
def get_color_by_reward(reward):
    global max_abs_reward
    # Calculate saturation based on the magnitude of the reward
    saturation = abs(reward) / max_abs_reward
    base_color = 'green' if reward > 0 else ('red' if reward < 0 else 'white')
    if base_color == 'white':
        return base_color
    return get_saturated_color(base_color, saturation)

# Helper function to get saturated color
def get_saturated_color(base_color, saturation):
    if base_color == "green":
        return f'#{int(255 - (255 - 0) * saturation):02x}FF{int(255 - (255 - 0) * saturation):02x}'
    elif base_color == "red":
        return f'#FF{int(255 - (255 * saturation)):02x}00'


# Initialize the grid with colors based on reward values
grid = [[{'color': get_color_by_reward(0.0), 'reward': 0.0} for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

# Variables to track the drawing and reward modes
drawing = False
reward_mode = False
current_reward = 0.0

# Modes setup
modes = ["Select Mode", "Transition Mode", "Reward Mode"]

eraser_active = False
# eraser_active.set(False)  # Default to not erasing

mode_var = tk.IntVar()
mode_var.set(0)  # Default to Select Mode

last_toggled_cell = None  # Keep track of the last toggled cell to prevent flickering

selected_cell = None  # Variable to keep track of the selected cell

# Initialize the grid state to handle internal logic
num_actions = 1
grid_state = Grid(GRID_HEIGHT, GRID_WIDTH, num_actions)

# Create labels for rewards and mode display
label_reward = tk.Label(root, text="Reward: 0.0")
label_reward.pack()

# Entry for setting rewards (only in reward mode)
entry_reward = tk.Entry(root)
entry_reward.pack()

def cell_click(event, row, col):
    global selected_cell
    mode = modes[mode_var.get()]

    if mode == "Select Mode":
        grid_state.setActiveGridCoord(row, col, not grid_state.activeGrid[row, col])
        grid[row][col]['color'] = 'white' if grid_state.activeGrid[row, col] else 'black'
        update_grid()
    elif mode.lower() == "reward mode":
        # Unhighlight the previously selected cell
        if selected_cell:
            r, c = selected_cell
            canvas.itemconfig(cells[r][c], width=1)
        # Highlight the newly selected cell
        selected_cell = (row, col)
        canvas.itemconfig(cells[row][col], width=3)
        # Update the reward label
        label_reward.config(text=f"Reward: {grid_state.rewards[row, col]:.2f}")

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
            last_toggled_cell = current_cell
            update_grid()

def set_reward(event):
    global selected_cell
    mode = modes[mode_var.get()]
    if mode.lower() == "reward mode" and selected_cell:
        row, col = selected_cell
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
    eraser_button.config(text="Unselect squares" if eraser_active else "Select squares")

# Function to update the grid display
def update_grid():
    for row in range(GRID_HEIGHT):
        for col in range(GRID_WIDTH):
            if grid_state.activeGrid[row, col]:
                cell_color = get_color_by_reward(grid_state.rewards[row, col])
            else:
                cell_color = 'black'  # Set the color to black if the cell is unselected
            canvas.itemconfig(cells[row][col], fill=cell_color)
            
def update_ui():
    mode = modes[mode_var.get()]
    if mode.lower() == "reward mode":
        label_reward.pack()
        entry_reward.pack()
        eraser_button.pack_forget()  # Hide the eraser button in reward mode
    else:
        label_reward.pack_forget()
        entry_reward.pack_forget()
        if mode == "Select Mode":
            eraser_button.pack()  # Show the eraser button only in select mode
        else:
            eraser_button.pack_forget()
    
    # If mode is "Select Mode", default to selecting squares
    if mode == "Select Mode":
        global eraser_active
        eraser_active = False
        eraser_button.config(text="Unselect squares")

def update_reward_ui():
    mode = modes[mode_var.get()]
    if mode.lower() == "reward mode":
        label_reward.pack()
        entry_reward.pack()
    else:
        label_reward.pack_forget()
        entry_reward.pack_forget()

for idx, m in enumerate(modes):
    r = tk.Radiobutton(root, text=m, variable=mode_var, value=idx, command=update_ui)
    r.pack(anchor='w')

eraser_button = tk.Button(root, text="Unselect squares", command=toggle_eraser)
eraser_button.pack()

# Hide reward-related UI at the start
update_ui()

# Create a canvas for the grid
canvas = tk.Canvas(root, width=GRID_WIDTH * CELL_SIZE, height=GRID_HEIGHT * CELL_SIZE)
canvas.pack()

# Bind the Enter key to the reward entry
entry_reward.bind('<Return>', set_reward)

# Create a 2D list to store the cell items
cells = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

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
