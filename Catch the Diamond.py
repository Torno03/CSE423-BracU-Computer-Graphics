import numpy as np
import time
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random

# Initialize window dimensions and game variables
width, height = 800, 600
basket_x, basket_y = 400, 30
basket_width, basket_height = 100, 20
diamond_speed = 100  # Initial falling speed of the diamond
diamond_color = [random.uniform(0.3,1), random.uniform(0.3,1), random.uniform(0.3,1)]  # Initial color of the diamond
score = 0
paused = False
game_over = False
game_over_displayed = False

# For collision detection
class AABB:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

def has_collided(box1, box2):
    return box1.x < box2.x + box2.width and \
           box1.x + box1.width > box2.x and \
           box1.y < box2.y + box2.height and \
           box1.y + box1.height > box2.y

# Function for finding Zone
def findzone(dx, dy):
    if dx == 0:  # Vertical line (dy != 0)
        if dy > 0:
            return "zone1"
        else:
            return "zone2"
    elif dy == 0:  # Horizontal line (dx != 0)
        if dx > 0:
            return "zone0"
        else:
            return "zone7"
    elif abs(dx) >= abs(dy):
        if dx > 0 and dy > 0:  # zone 0
            return "zone0"
        elif dx < 0 and dy > 0:  # zone 3
            return "zone3"
        elif dx < 0 and dy < 0:  # zone 4
            return "zone4"
        elif dx > 0 and dy < 0:  # zone 7
            return "zone7"
    else:
        if dx > 0 and dy > 0:  # zone 1
            return "zone1"
        elif dx < 0 and dy > 0:  # zone 2
            return "zone2"
        elif dx < 0 and dy < 0:  # zone 5
            return "zone5"
        elif dx > 0 and dy < 0:  # zone 6
            return "zone6"

# Function to convert back from Zone 0 to the original zone
def convert_from_zone_0(x, y, zone):
    if zone == "zone0":  # zone 0
        return x, y
    elif zone == "zone1":  # zone 1
        return y, x
    elif zone == "zone2":  # zone 2
        return -y, x
    elif zone == "zone3":  # zone 3
        return -x, y
    elif zone == "zone4":  # zone 4
        return -x, -y
    elif zone == "zone5":  # zone 5
        return -y, -x
    elif zone == "zone6":  # zone 6
        return y, -x
    elif zone == "zone7":  # zone 7
        return x, -y

# Function to convert from Zone 0 to any other zone (reflection of coordinates)
def convert_to_zone_0(x, y, zone):
    if zone == "zone0":  # zone 0
        return x, y
    elif zone == "zone1":  # zone 1
        return y, x
    elif zone == "zone2":  # zone 2
        return y, -x
    elif zone == "zone3":  # zone 3
        return -x, y
    elif zone == "zone4":  # zone 4
        return -x, -y
    elif zone == "zone5":  # zone 5
        return -y, -x
    elif zone == "zone6":  # zone 6
        return -y, x
    elif zone == "zone7":  # zone 7
        return x, -y

# Midpoint Line Drawing Algorithm to draw a line from (x1, y1) to (x2, y2)
def midpoint_line(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    
    # Handle vertical lines (dx == 0) and horizontal lines (dy == 0)
    if dx == 0:  # Vertical line case
        points = []
        for y in range(min(y1, y2), max(y1, y2) + 1):  # Only y changes
            points.append((x1, y))
        return points
    
    if dy == 0:  # Horizontal line case
        points = []
        for x in range(min(x1, x2), max(x1, x2) + 1):  # Only x changes
            points.append((x, y1))
        return points
    
    # Find the zone for non-horizontal and non-vertical lines
    zone = findzone(dx, dy)
    
    # Convert coordinates to Zone 0
    x1, y1 = convert_to_zone_0(x1, y1, zone)
    x2, y2 = convert_to_zone_0(x2, y2, zone)

    # Calculate the midpoint algorithm
    dx = x2 - x1
    dy = y2 - y1

    d = 2 * dy - dx
    incrE = 2 * dy
    incrNE = 2 * (dy - dx)

    x = x1
    y = y1
    points = [(x, y)]

    while x < x2:
        if d <= 0:
            d += incrE
            x += 1
        else:
            d += incrNE
            x += 1
            y += 1
        points.append((x, y))

    # Convert points back from Zone 0 to the original zone
    converted_points = [convert_from_zone_0(px, py, zone) for px, py in points]
    return converted_points

# Function to draw the basket
def draw_basket(x, y, width, height, color):
    glColor3f(*color)
    points = []
    points += midpoint_line(x + 15, y, x + width - 15, y)  # Bottom edge
    points += midpoint_line(x + 15, y, x, y + height)  # Left edge
    points += midpoint_line(x + width - 15, y, x + width, y + height)  # Right edge
    points += midpoint_line(x, y + height, x + width, y + height)  # Top edge
    for point in points:
        glVertex2f(point[0], point[1])
    glColor3f(1, 1, 1)

#Draw Left Arrow button
def draw_left_arrow(width, height):
    glColor3f(0, 0.98, 0.78)
    points = []
    points += midpoint_line(20, height - 40, 40, height - 40)
    points += midpoint_line(20, height - 40, 25, height - 35)
    points += midpoint_line(20, height - 40, 25, height - 45)
    for point in points:
        glVertex2f(point[0], point[1])
    glColor3f(1, 1, 1)

#Draw Cross Button
def draw_cross(width, height):
    glColor3f(1, 0, 0)
    points = []
    points += midpoint_line(width-40, height-40, width-20, height-60)
    points += midpoint_line(width-40, height-60, width-20, height-40)
    for point in points:
        glVertex2f(point[0], point[1])
    glColor3f(1, 1, 1)

#Draw Play Button
def draw_play_button(width, height):
    glColor3f(1, 0.749, 0)
    points = []
    points += midpoint_line(width//2-10, height-40, width//2+10, height-50)
    points += midpoint_line(width//2-10, height-40, width//2-10, height-60)
    points += midpoint_line(width//2-10, height-60, width//2+10, height-50)
    for point in points:
        glVertex2f(point[0], point[1])
    glColor3f(1, 1, 1)

#Draw Pause Button
def draw_pause_button(width, height):
    glColor3f(1, 0.749, 0)
    points = []
    points += midpoint_line(width//2-15, height-40, width//2-15, height-60)
    points += midpoint_line(width//2-15, height-40, width//2-5, height-40)
    points += midpoint_line(width//2-5, height-40, width//2-5, height-60)
    points += midpoint_line(width//2-5, height-60, width//2-15, height-60)
    points += midpoint_line(width//2+5, height-40, width//2+5, height-60)
    points += midpoint_line(width//2+5, height-40, width//2+15, height-40)
    points += midpoint_line(width//2+15, height-40, width//2+15, height-60)
    points += midpoint_line(width//2+15, height-60, width//2+5, height-60)
    for point in points:
        glVertex2f(point[0], point[1])
    glColor3f(1, 1, 1)

# Function to draw a diamond
def draw_diamond(x, y, size, color):
    glColor3f(*color)
    points = []
    points += midpoint_line(x, y + size, x - size + 3, y)  # Top-left edge
    points += midpoint_line(x - size + 3, y, x, y - size)  # Bottom-left edge
    points += midpoint_line(x, y - size, x + size - 3, y)  # Bottom-right edge
    points += midpoint_line(x + size - 3, y, x, y + size)  # Top-right edge
    for point in points:
        glVertex2f(point[0], point[1])
    glColor3f(1, 1, 1)

# Falling diamond class
class FallingDiamond:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius

    def reset_position(self):
        self.x = random.uniform(self.radius, width - self.radius)
        self.y = height

    def move(self, delta_time):
        self.y -= diamond_speed * delta_time

# Game loop
def game_loop():
    global basket_x, basket_y, last_time, diamond, diamond_speed, diamond_color, score, paused, game_over, game_over_displayed

    current_time = time.time()
    delta_time = current_time - last_time
    last_time = current_time

    if game_over:
        if not game_over_displayed:
            print(f"Game Over!\nFinal Score: {score}")
            game_over_displayed = True
    elif not paused:
        # Move the diamond
        diamond.move(delta_time)
        if diamond.y < 0:  # Diamond missed
            game_over = True

        # Check if the basket catches the diamond
        basket_box = AABB(basket_x, basket_y, basket_width, basket_height)
        diamond_box = AABB(diamond.x - diamond.radius, diamond.y - diamond.radius, 2 * diamond.radius, 2 * diamond.radius)
        if has_collided(basket_box, diamond_box):
            score += 1
            print(f"Score: {score}")
            diamond.reset_position()
            diamond_color = [random.uniform(0.3,1), random.uniform(0.3,1), random.uniform(0.3,1)]  # Randomize diamond color
            diamond_speed += 10  # Increase falling speed

    # Clear the screen
    glClear(GL_COLOR_BUFFER_BIT)

    # Draw basket and diamond
    glPointSize(5)
    glBegin(GL_POINTS)
    draw_basket(basket_x, basket_y, basket_width, basket_height, [1, 0, 0] if game_over else [1, 1, 1])
    if not game_over:
        draw_diamond(diamond.x, diamond.y, diamond.radius, diamond_color)
    draw_left_arrow(width, height)
    if paused:
        draw_play_button(width, height)
    else:
        draw_pause_button(width, height)
    draw_cross(width, height)
    glEnd()

    # Swap buffers
    glutSwapBuffers()

# Initialize OpenGL
def init():
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glPointSize(2)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, width, 0, height)

# Function to handle user input (move basket)
def keyboard(key, x, y):
    global basket_x

    if game_over:
        return

    if not paused:
        if key == b'a':  # Move left
            basket_x -= 10
        elif key == b'd':  # Move right
            basket_x += 10

    if basket_x < 0:
        basket_x = 0
    elif basket_x + basket_width > width:
        basket_x = width - basket_width

# Add special keys callback for moving the basket with arrow keys
def keyboard_special(key, x, y):
    global basket_x
    if game_over:
        return
    if not paused:
        if key == GLUT_KEY_LEFT:
            basket_x -= 10
        elif key == GLUT_KEY_RIGHT:
            basket_x += 10
    # Ensure basket stays within bounds
    if basket_x < 0:
        basket_x = 0
    elif basket_x + basket_width > width:
        basket_x = width - basket_width

def mouse_click(button, state, x, y):
    global game_over, paused, game_over_displayed

    restart_button_box = AABB(20, height - 40, 20, 20)
    play_pause_button_box = AABB(width // 2 - 10, height - 60, 20, 20)
    exit_button_box = AABB(width - 40, height - 50, 40, 40)

    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        # Convert y coordinate to match OpenGL's coordinate system
        y = height - y

        if has_collided(AABB(x, y, 1, 1), restart_button_box):  # Restart button
            print("Starting Over")
            restart_game()
        elif has_collided(AABB(x, y, 1, 1), play_pause_button_box):  # Play/Pause button
            paused = not paused
            if paused:
                print("Game Paused")
            else:
                print("Game Resumed")
        elif has_collided(AABB(x, y, 1, 1), exit_button_box):  # Exit button
            print(f"Goodbye!\nFinal Score: {score}")
            game_over = True
            game_over_displayed = True
            glutLeaveMainLoop()

def restart_game():
    global score, diamond_speed, diamond_color, game_over_displayed, diamond, paused, game_over, last_time
    score = 0
    diamond_speed = 100
    diamond_color = [random.uniform(0.3,1), random.uniform(0.3,1), random.uniform(0.3,1)]
    game_over = False
    game_over_displayed = False
    diamond.reset_position()
    last_time = time.time()
    paused = False

# Initialize the last time variable for delta time
last_time = time.time()

# Initialize diamond
diamond = FallingDiamond(random.uniform(50, width - 50), height, 15)

# Set up OpenGL, window, and main loop
glutInit()
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
glutInitWindowSize(width, height)
glutCreateWindow(b"Catch the Diamond")
init()
glutDisplayFunc(game_loop)
glutIdleFunc(game_loop)
glutKeyboardFunc(keyboard)
glutSpecialFunc(keyboard_special)
glutMouseFunc(mouse_click)

# Start the main loop
glutMainLoop()
