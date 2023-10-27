import tkinter as tk

# Constants for grid dimensions and cell size
GRID_WIDTH = 10
GRID_HEIGHT = 10
CELL_SIZE = 40

# Initialize the grid with colors and rewards
grid = [[{'color': 'white', 'reward': 0.0} for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

# Variables to track the drawing and reward modes
drawing = False
reward_mode = False
current_color = 'red'
current_reward = 0.0

# Function to handle cell click
def cell_click(event, row, col):
    global current_color, current_reward
    if reward_mode:
        # In reward mode, set the reward for the clicked cell
        try:
            reward = float(entry_reward.get())
            grid[row][col]['reward'] = reward
            entry_reward.delete(0, tk.END)
        except ValueError:
            pass
    else:
        # In coloring mode, change the color of the clicked cell
        grid[row][col]['color'] = current_color

    update_grid()

# Function to start drawing or setting rewards
def start_drawing(event):
    global drawing
    drawing = True

# Function to stop drawing or setting rewards
def stop_drawing(event):
    global drawing
    drawing = False

# Function to draw while dragging (for coloring)
def draw(event):
    if drawing and not reward_mode:
        col = event.x // CELL_SIZE
        row = event.y // CELL_SIZE
        if 0 <= col < GRID_WIDTH and 0 <= row < GRID_HEIGHT:
            grid[row][col]['color'] = current_color
            update_grid()

# Function to change the current drawing color
def change_color(new_color):
    global current_color
    current_color = new_color

# Function to switch between coloring mode and reward mode
def switch_mode():
    global reward_mode
    reward_mode = not reward_mode
    if reward_mode:
        label_mode.config(text="Reward Mode")
    else:
        label_mode.config(text="Color Mode")

# Function to update the grid display
def update_grid():
    for row in range(GRID_HEIGHT):
        for col in range(GRID_WIDTH):
            x1, y1 = col * CELL_SIZE, row * CELL_SIZE
            x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
            cell_color = grid[row][col]['color']
            canvas.itemconfig(cells[row][col], fill=cell_color)
            label_reward.config(text=f"Reward: {grid[row][col]['reward']:.2f}")

# Create the main window
root = tk.Tk()
root.title("Gridworld Game")

# Create a canvas for the grid
canvas = tk.Canvas(root, width=GRID_WIDTH * CELL_SIZE, height=GRID_HEIGHT * CELL_SIZE)
canvas.pack()

# Create a 2D list to store the cell items
cells = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

# Populate the grid and bind click events
for row in range(GRID_HEIGHT):
    for col in range(GRID_WIDTH):
        x1, y1 = col * CELL_SIZE, row * CELL_SIZE
        x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
        cell = canvas.create_rectangle(x1, y1, x2, y2, fill=grid[row][col]['color'], outline='black')
        cells[row][col] = cell
        canvas.tag_bind(cell, '<Button-1>', lambda event, r=row, c=col: cell_click(event, r, c))

# Bind mouse events for drawing (coloring)
canvas.bind('<Button-1>', start_drawing)
canvas.bind('<ButtonRelease-1>', stop_drawing)
canvas.bind('<B1-Motion>', draw)

# Create a color palette
color_palette = tk.Frame(root)
color_palette.pack()

colors = ['white', 'red', 'green', 'blue', 'yellow', 'orange', 'purple', 'pink']

for color in colors:
    color_button = tk.Button(color_palette, bg=color, width=4, command=lambda c=color: change_color(c))
    color_button.pack(side='left')

# Create a mode switch button
mode_button = tk.Button(root, text="Switch Mode", command=switch_mode)
mode_button.pack()

# Create labels for rewards and mode display
label_reward = tk.Label(root, text="Reward: 0.0")
label_reward.pack()
label_mode = tk.Label(root, text="Color Mode")
label_mode.pack()

# Entry for setting rewards (only in reward mode)
entry_reward = tk.Entry(root)
entry_reward.pack()

# Start the application
root.mainloop()
