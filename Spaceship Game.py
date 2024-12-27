import numpy as np
import time
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random

# Initialize window dimensions and game variables
width, height = 800, 600
spaceship_x, spaceship_y = 400, 30
spaceship_width, spaceship_height = 25, 90
spaceship_speed = 10  # in pixels per second
bullet_speed = 400  # in pixels per second
num_circles = 5  # Number of falling circles
score = 0
circle_speed = 100  # in pixels per second
circle_size = 20  # Circle radius 
game_over = False
counter = 0
missed_shots = 0
max_missed_shots = 3
paused = False
game_over_displayed = False

class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 2
        self.height = 5

    def move(self, delta_time):
        self.y += bullet_speed * delta_time

    def get_aabb(self):
        return AABB(self.x, self.y, self.width, self.height)

    def check_collision(self, circle_x, circle_y, circle_radius):
        # Create an AABB for the circle
        circle_aabb = AABB(circle_x - circle_radius, circle_y - circle_radius, 2 * circle_radius, 2 * circle_radius)
        # Create an AABB for the bullet
        bullet_aabb = self.get_aabb()
        # Use the has_collided function to check for collision
        return has_collided(bullet_aabb, circle_aabb)
        return distance < circle_radius

# For collision detection between spaceship and circles
class AABB:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

# Function to detect collision between two AABBs (spaceship and circle)
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




# Function to draw the spaceship using Midpoint Line Algorithm (triangle shape)
def draw_spaceship(x, y, width, height):
    glColor3f(0.5, 0.5, 0)
    points = []

    #Top Triangle
    points += midpoint_line(x, y+height-30, x + width // 2, y + height)  #Left edge
    points += midpoint_line(x + width // 2, y + height, x + width, y+height-30)  #Right edge
    points += midpoint_line(x + width, y+height-30, x, y+height-30)  #Bottom edge
    
    #Draw Bigger Rectangle
    points += midpoint_line(x, y+height-30, x, y+height-75) #Left edge
    points += midpoint_line(x, y+height-75, x+width, y+height-75) #Bottom edge
    points += midpoint_line(x+width, y+height-75, x + width, y+height-30) #Right edge
    
    #Left Triangle
    points += midpoint_line(x, y+height-75, x-width+5, y+height-75) #Bottom Edge
    points += midpoint_line(x-width+5, y+height-75, x, y+height-60) #Top Edge
    
    #Right Triangle
    points += midpoint_line(x+width, y+height-75, x+width+width-5, y+height-75) #Bottom edge
    points += midpoint_line(x+width+width-5, y+height-75, x+width, y+height-60) #Top edge

    #Bottom Left Rectangle
    points += midpoint_line(x-2, y+height-85, x-2, y+height-105) #Left edge
    points += midpoint_line(x+5, y+height-85, x+5, y+height-105) #Right edge
    points += midpoint_line(x-2, y+height-85, x+5, y+height-85) #Top edge
    points += midpoint_line(x-2, y+height-105, x+5, y+height-105) #Bottom egde

    #Bottom Middle Rectangle
    points += midpoint_line(x+9, y+height-85, x+9, y+height-105) #Left edge
    points += midpoint_line(x+16, y+height-85, x+16, y+height-105) #Right edge
    points += midpoint_line(x+9, y+height-85, x+16, y+height-85) #Top edge
    points += midpoint_line(x+9, y+height-105, x+16, y+height-105) #Bottom egde    

    #Bottom Right Rectangle
    points += midpoint_line(x+20, y+height-85, x+20, y+height-105) #Left edge
    points += midpoint_line(x+27, y+height-85, x+27, y+height-105) #Right edge
    points += midpoint_line(x+20, y+height-85, x+27, y+height-85) #Top edge
    points += midpoint_line(x+20, y+height-105, x+27, y+height-105) #Bottom egde   


    # Draw the points using glPoint
    for point in points:
        glVertex2f(point[0], point[1])
    glColor3f(1, 1, 1)

#Draw Left Arrow button
def draw_left_arrow(width, height):
    glColor3f(0, 1, 0)
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
    glColor3f(1, 0.5, 0)
    points = []
    points += midpoint_line(width//2-10, height-40, width//2+10, height-50)
    points += midpoint_line(width//2-10, height-40, width//2-10, height-60)
    points += midpoint_line(width//2-10, height-60, width//2+10, height-50)
    for point in points:
        glVertex2f(point[0], point[1])
    glColor3f(1, 1, 1)

#Draw Pause Button
def draw_pause_button(width, height):
    glColor3f(1, 0.5, 0)
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



# Circle class to represent each falling circle
class FallingCircle:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius

    def reset_position(self):
        self.x = random.randint(self.radius, width - self.radius)
        self.y = height + random.randint(0, height)  # Start above the window

    def move(self, delta_time):
        self.y -= circle_speed * delta_time

class SpecialCircle(FallingCircle):
    def __init__(self, x, y, radius, min_radius, max_radius, expansion_speed):
        super().__init__(x, y, radius)
        self.min_radius = min_radius
        self.max_radius = max_radius
        self.expansion_speed = expansion_speed
        self.expanding = True

    def move(self, delta_time):
        super().move(delta_time)
        if self.expanding:
            self.radius += self.expansion_speed * delta_time
            if self.radius >= self.max_radius:
                self.expanding = False
        else:
            self.radius -= self.expansion_speed * delta_time
            if self.radius <= self.min_radius:
                self.expanding = True

    def reset_position(self):
        self.x = random.randint(int(self.radius), width - int(self.radius))
        self.y = height + random.randint(0, height)



# Function to draw a circle (approximated by points)

# Midpoint Circle Algorithm to draw a circle with center (x, y) and radius
def midpoint_circle(x, y, radius):
    glColor3f(0.5, 0.5, 0)
    points = []
    # Start at the point on the top of the circle
    xc, yc = x, y
    r = radius
    x = r
    y = 0
    d = 1 - r  # Initial decision parameter

    # Plot points in all 8 octants
    while x > y:
        # Add the points for all 8 octants
        points.append((xc + x, yc + y))
        points.append((xc - x, yc + y))
        points.append((xc + x, yc - y))
        points.append((xc - x, yc  - y))
        points.append((xc + y, yc + x))
        points.append((xc - y, yc + x))
        points.append((xc + y, yc - x))
        points.append((xc - y, yc - x))

        y += 1

        if d <= 0:
            d = d + 2 * y + 3  # Move the point to the East
        else:
            x -= 1
            d = d + 2 * y - 2 * x + 5  # Move the point to the North-West

    # Draw the points using glPoint
    for point in points:
        glVertex2f(point[0], point[1])
    glColor3f(1, 1, 1)

# Function to draw a falling circle
def draw_falling_circle(circle):
    return midpoint_circle(circle.x, circle.y, circle.radius)

# Function to draw a bullet
def draw_bullet(bullet):
    return midpoint_circle(bullet.x, bullet.y, 2)

# Game loop
def game_loop():
    global spaceship_x, spaceship_y, last_time, bullets, game_over, falling_circles, score, counter, missed_shots, game_over_displayed

    current_time = time.time()
    delta_time = current_time - last_time
    last_time = current_time 

    # Move bullets
    if game_over:
        if not game_over_displayed:
            print(f"Game Over! Final Score: {score}")
            game_over_displayed = True
    elif not paused:
        for bullet in bullets:
            bullet.move(delta_time)
            if bullet.y > height:
                bullets.remove(bullet)
                missed_shots += 1
                print(f"Missed shot! Missed shots: {missed_shots}")

            if missed_shots >= max_missed_shots:
                    print("Game Over!")
                    game_over = True

            # Check if bullet hits any circle
            for circle in falling_circles:
                if bullet.check_collision(circle.x, circle.y, circle.radius):
                    bullets.remove(bullet)
                    if isinstance(circle, SpecialCircle):
                        score += 10  # Award more points for hitting the special circle
                        print(f"Bullet hit a special circle! Score: {score}")
                    else:
                        score += 1
                        print(f"Bullet hit a circle! Score: {score}")
                    circle.reset_position()

        # Check for collision between spaceship and any falling circle
        spaceship_box = AABB(spaceship_x, spaceship_y, spaceship_width, spaceship_height)
        for circle in falling_circles:
            circle.move(delta_time)
            circle_box = AABB(circle.x - circle.radius, circle.y - circle.radius, 2 * circle.radius, 2 * circle.radius)
            if has_collided(spaceship_box, circle_box):
                print("Game Over!")
                game_over = True
            elif circle.y < 0:  # Reset circle position when it goes off the screen
                counter += 1
                circle.reset_position()
                if counter == 3:
                    print("Game Over!")
                    game_over = True
                        
    if game_over:
        if not game_over_displayed:
            print(f"Final Score: {score}")
            game_over_displayed = True
        
    
    # Clear the screen
    glClear(GL_COLOR_BUFFER_BIT)

    # Draw spaceship, circles, and bullets
    glPointSize(2)
    glBegin(GL_POINTS)
    draw_spaceship(spaceship_x, spaceship_y, spaceship_width, spaceship_height)
    draw_left_arrow(width, height)
    draw_left_arrow(width, height)
    if paused:
        draw_play_button(width, height)
    else:
        draw_pause_button(width, height)
    draw_cross(width, height)
    if not game_over:
        for circle in falling_circles:
            draw_falling_circle(circle)
        for bullet in bullets:
            draw_bullet(bullet)
    glEnd()

    # Swap buffers (show the drawing on the screen)
    glutSwapBuffers()

# Initialize OpenGL
def init():
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glPointSize(2)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, width, 0, height)

# Function to handle user input (move spaceship and shoot bullets)
def keyboard(key, x, y):
    global spaceship_x, spaceship_y, bullets

    if game_over:
        return

    if key == b'w':
        spaceship_y += spaceship_speed
    elif key == b's':
        spaceship_y -= spaceship_speed
    elif key == b'a':
        spaceship_x -= spaceship_speed
    elif key == b'd':
        spaceship_x += spaceship_speed
    elif key == b' ':
        bullet = Bullet(spaceship_x + spaceship_width / 2, spaceship_y + spaceship_height)
        bullets.append(bullet)
    
    if spaceship_x < 0:
        spaceship_x = 0
    elif spaceship_x + spaceship_width > width:
        spaceship_x = width - spaceship_width

    if spaceship_y < 0:
        spaceship_y = 0
    elif spaceship_y + spaceship_height > height:
        spaceship_y = height - spaceship_height

def mouse_click(button, state, x, y):
    global game_over, paused, game_over_displayed

    restart_button_box = AABB(20, height - 40, 20, 20)
    play_pause_button_box = AABB(width // 2 - 10, height - 60, 20, 20)
    exit_button_box = AABB(width - 40, height - 50, 20, 20)

    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
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
    global score, circle_speed,counter, missed_shots, max_missed_shots, game_over_displayed, falling_circles, special_circle, bullets, game_over, paused, last_time
    score = 0
    circle_speed = 100  # in pixels per second
    circle_size = 20  # Circle radius 
    game_over = False
    counter = 0
    missed_shots = 0
    max_missed_shots = 3
    game_over_displayed = False
    bullets = []
    falling_circles = [FallingCircle(random.randint(50, width - 50), random.randint(height, height + 600), int(circle_size)) for _ in range(num_circles - 1)]
    special_circle = SpecialCircle(random.randint(50, width - 50), random.randint(height, height + 600), int(circle_size), min_radius=10, max_radius=30, expansion_speed=20)
    falling_circles.append(special_circle)
    game_over = False
    paused = False

# Initialize the last time variable for delta time
last_time = time.time()
bullets = []
falling_circles = [FallingCircle(random.randint(50, width - 50), random.randint(height, height + 600), int(circle_size)) for _ in range(num_circles - 1)]
special_circle = SpecialCircle(random.randint(50, width - 50), random.randint(height, height + 600), int(circle_size), min_radius=10, max_radius=20, expansion_speed=20)
falling_circles.append(special_circle)
game_over = False

# Set up OpenGL, window, and main loop
glutInit()
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
glutInitWindowSize(width, height)
glutCreateWindow(b"OpenGL Game with Midpoint Line Spaceship")
init()
glutDisplayFunc(game_loop)
glutIdleFunc(game_loop)
glutKeyboardFunc(keyboard)
glutMouseFunc(mouse_click)

# Start the main loop
glutMainLoop()
