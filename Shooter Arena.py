from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math, random

# Camera-related variables
camera_radius = 800
cam_theta = math.radians(90)   # horizontal angle around z‑axis
cam_phi   = math.radians(35)   # elevation above the XY plane

follow_gun   = False
enemy_speed = 0.05

auto_follow = False
cheat_mode = False
cheat_rot_speed = 2.0           # degrees per idle‐frame
cheat_fire_angle_tol = 5.0      # tolerance in degrees

life    = 5
score   = 0
misses  = 0
game_over = False

player_pos = [0, 0, 0]  # Player position (x, y, z)
gun_angle = 0  # Angle of the gun in degrees
bullets = []  # List to store active bullets
bullet_speed = 15  # Speed of bullets
player_direction = [0, 1, 0]  # Direction player is facing (initially forward)

fovY = 120  # Field of view
GRID_LENGTH = 600  # Length of grid lines
rand_var = 423

MIN_SPAWN_DISTANCE = 200
ENEMY_COUNT = 5
enemy_positions = []
for i in range(ENEMY_COUNT):
    while True:
        rx = random.uniform(-GRID_LENGTH + 50, GRID_LENGTH - 50)
        ry = random.uniform(-GRID_LENGTH + 50, GRID_LENGTH - 50)
        if math.hypot(rx - player_pos[0], ry - player_pos[1]) >= MIN_SPAWN_DISTANCE:
            enemy_positions.append((rx, ry, 0))
            break



def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1,1,1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    
    # Set up an orthographic projection that matches window coordinates
    gluOrtho2D(0, 1000, 0, 800)  # left, right, bottom, top

    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Draw text at (x, y) in screen coordinates
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    
    # Restore original projection and modelview matrices
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_player():
    glPushMatrix()
    
    # Position the player according to global position
    glTranslatef(player_pos[0], player_pos[1], player_pos[2])

    # Rotate the player to face the current direction
    #angle = math.degrees(math.atan2(player_direction[1], player_direction[0]))
    glRotatef(gun_angle, 0, 0, 1)  # Rotate the player to face the direction

    # Draw the torso (cuboid)
    glPushMatrix()
    glColor3f(0.0, 1.0, 0.0)  # Green color for the torso
    glScalef(30, 20, 60)  # Scale to make a cuboid
    glutSolidCube(1)
    glPopMatrix()

    # Draw the head (sphere)
    glPushMatrix()
    glColor3f(0.0, 0.0, 0.0)  # Black color for the head
    glTranslatef(0, 0, 50)  # Position the head on top of the torso
    glutSolidSphere(15, 16, 16)  # Radius 15
    glPopMatrix()

    # Draw the left arm (cylinder)
    glPushMatrix()
    glColor3f(1.0, 1.0, 0.0)  # Yellow color for the arms
    glTranslatef(-25, 30, 30)  # Position the left arm
    glRotatef(90, 1, 0, 0)  # Rotate to align horizontally
    gluCylinder(gluNewQuadric(), 5, 5, 30, 16, 16)  # Cylinder with radius 5 and height 30
    glPopMatrix()

    # Draw the right arm (cylinder)
    glPushMatrix()
    glColor3f(1.0, 1.0, 0.0)  # Yellow color for the arms
    glTranslatef(25, 30, 30)  # Position the right arm
    glRotatef(90, 1, 0, 0)  # Rotate to align horizontally
    gluCylinder(gluNewQuadric(), 5, 5, 30, 16, 16)  # Cylinder with radius 5 and height 30
    glPopMatrix()

    # Draw the left leg (cuboid)
    glPushMatrix()
    glColor3f(0.0, 0.0, 1.0)  # Blue color for the legs
    glTranslatef(-10, 0, -40)  # Position the left leg
    glScalef(10, 10, 40)  # Scale to make a cuboid
    glutSolidCube(1)
    glPopMatrix()

    # Draw the right leg (cuboid)
    glPushMatrix()
    glColor3f(0.0, 0.0, 1.0)  # Blue color for the legs
    glTranslatef(10, 0, -40)  # Position the right leg
    glScalef(10, 10, 40)  # Scale to make a cuboid
    glutSolidCube(1)
    glPopMatrix()

    # Draw the gun (cylinder) - now with rotation
    glPushMatrix()
    glColor3f(1.0, 0.0, 0.0)  # Red color for the gun
    glTranslatef(0, 60, 30)  # Position the gun
    glRotatef(90, 1, 0, 0)  # Base rotation to align horizontally
    gluCylinder(gluNewQuadric(), 3, 3, 40, 16, 16)  # Cylinder with radius 3 and height 40
    glPopMatrix()

    glPopMatrix()

def draw_player_lie():
    glPushMatrix()
    # Position at player location with slight elevation
    glTranslatef(player_pos[0], player_pos[1], player_pos[2] + 15)
    # Keep the facing direction
    glRotatef(gun_angle, 0, 0, 1)
    
    # Rotate to lie horizontally on the X-Z plane
    glRotatef(90, 0, 1, 0)
    
    # Draw the torso (cuboid) - now horizontally oriented
    glPushMatrix()
    glColor3f(0.0, 1.0, 0.0)  # Green torso
    glScalef(20, 30, 60)      # Make it long along z-axis (forward)
    glutSolidCube(1)
    glPopMatrix()

    # Draw the head (sphere) - at one end of the torso
    glPushMatrix()
    glColor3f(0.0, 0.0, 0.0)  # Black head
    glTranslatef(0, 0, 50)    # At the "front" end when lying down
    glutSolidSphere(15, 16, 16)
    glPopMatrix()

    # Draw arms spread out to the sides
    # Left arm
    glPushMatrix()
    glColor3f(1.0, 1.0, 0.0)  # Yellow arms
    glTranslatef(0, -35, 10)  # Coming out from side of torso
    glRotatef(90, 0, 0, 1)    # Pointing out sideways
    gluCylinder(gluNewQuadric(), 5, 5, 30, 16, 16)
    glPopMatrix()

    # Right arm
    glPushMatrix()
    glColor3f(1.0, 1.0, 0.0)  # Yellow arms
    glTranslatef(0, 35, 10)   # Coming out from other side of torso
    glRotatef(-90, 0, 0, 1)   # Pointing out sideways (opposite)
    gluCylinder(gluNewQuadric(), 5, 5, 30, 16, 16)
    glPopMatrix()

    # Legs extending backward
    # Left leg
    glPushMatrix()
    glColor3f(0.0, 0.0, 1.0)  # Blue legs
    glTranslatef(0, -15, -40) # Extending backward from torso
    glScalef(10, 10, 40)      # Long backward
    glutSolidCube(1)
    glPopMatrix()

    # Right leg
    glPushMatrix()
    glColor3f(0.0, 0.0, 1.0)  # Blue legs
    glTranslatef(0, 15, -40)  # Extending backward from torso
    glScalef(10, 10, 40)      # Long backward
    glutSolidCube(1)
    glPopMatrix()

    # Gun dropped nearby - positioned realistically
    glPushMatrix()
    glColor3f(1.0, 0.0, 0.0)  # Red gun
    glTranslatef(10, 40, 5)   # Near the player's hand
    glRotatef(45, 0, 1, 0)    # Angled on ground
    gluCylinder(gluNewQuadric(), 3, 3, 40, 16, 16)
    glPopMatrix()

    glPopMatrix()

def draw_weapon():
    glPushMatrix()
    # 1) move into the player/eye position so the gun follows the player
    glTranslatef(player_pos[0], player_pos[1], player_pos[2])
    # 2) rotate into gun direction
    glRotatef(gun_angle, 0, 0, 1)

    # left forearm
    glPushMatrix()
    glColor3f(1,1,0)
    glTranslatef(-5, 20, -5)
    glRotatef(90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 3, 3, 20, 12, 4)
    glPopMatrix()

    # right forearm
    glPushMatrix()
    glColor3f(1,1,0)
    glTranslatef(5, 20, -5)
    glRotatef(90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 3, 3, 20, 12, 4)
    glPopMatrix()

    # gun barrel
    glPushMatrix()
    glColor3f(1,0,0)
    glTranslatef(0, 30, 0)
    glRotatef(90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 2, 2, 30, 12, 4)
    glPopMatrix()

    glPopMatrix()

def draw_enemy(x=0, y=0, z=0):
    import math
    from OpenGL.GLUT import glutGet, GLUT_ELAPSED_TIME

    # compute a pulsating scale factor based on elapsed time
    t = glutGet(GLUT_ELAPSED_TIME) / 500.0           # adjust divisor for speed
    scale = 1.0 + 0.3 * math.sin(2 * math.pi * t)       # amplitude .3

    glPushMatrix()
    glTranslatef(x, y, z)
    glScalef(scale, scale, scale)

    # Draw the body (larger red sphere)
    glPushMatrix()
    glColor3f(1.0, 0.0, 0.0)
    glutSolidSphere(25, 20, 20)
    glPopMatrix()

    # Draw the head (smaller black sphere)
    glPushMatrix()
    glColor3f(0.0, 0.0, 0.0)
    glTranslatef(0, 0, 30)
    glutSolidSphere(12, 16, 16)
    glPopMatrix()

    glPopMatrix()

# Add this function to draw bullets
def draw_bullets():
    for bullet in bullets:
        x, y, z, dx, dy, dz, lifetime = bullet
        
        glPushMatrix()
        glTranslatef(x, y, z)
        glColor3f(1.0, 0.8, 0.0)  # Yellow/gold bullet
        glutSolidSphere(5, 10, 10)  # Small sphere for bullet
        glPopMatrix()

def draw_shapes():
    if game_over:
        draw_player_lie()
    elif not follow_gun:
        draw_player()
    else:
        draw_weapon()

    for pos in enemy_positions:
        x, y, z = pos
        draw_enemy(x, y, z)
    
    draw_bullets()


def draw_grid_with_boundaries():
    cell_size = GRID_LENGTH / 6.5  # Size of each cell (grid divided into 13 cells)
    
    # Draw the checkerboard pattern
    glBegin(GL_QUADS)
    for i in range(13):
        for j in range(13):
            # Alternate colors for checkerboard pattern
            if (i + j) % 2 == 0:
                glColor3f(1, 1, 1)  # White squares
            else:
                glColor3f(0.7, 0.5, 0.95)  # Purple squares
            
            # Calculate the position of each square
            x1 = -GRID_LENGTH + i * cell_size
            x2 = -GRID_LENGTH + (i + 1) * cell_size
            y1 = -GRID_LENGTH + j * cell_size
            y2 = -GRID_LENGTH + (j + 1) * cell_size
            
            # Draw the square
            glVertex3f(x1, y1, 0)
            glVertex3f(x2, y1, 0)
            glVertex3f(x2, y2, 0)
            glVertex3f(x1, y2, 0)
    glEnd()
    
    # Draw the vertical boundaries/walls
    glBegin(GL_QUADS)
    
    # Blue wall (back)
    glColor3f(0.0, 0.0, 1.0)  # Blue
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, 100)  # Height of 100
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, 100)
    
    # Cyan wall (right)
    glColor3f(0.0, 1.0, 1.0)  # Cyan
    glVertex3f(GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, 100)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, 100)
    
    # Green wall (front)
    glColor3f(0.0, 1.0, 0.0)  # Green
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, 100)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, 100)
    
    # Red/Purple wall (left) - looks more purple in the image
    glColor3f(1.0, 0.0, 1.0)  # Magenta
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, 100)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, 100)
    
    glEnd()

def keyboardListener(key, x, y):
    global player_pos, gun_angle, player_direction, cheat_mode, auto_follow, life, score, misses, game_over
    speed = 10.0

    # if game over, only R key works
    if game_over:
        if key in (b'r', b'R'):
            life = 5; score = 0; misses = 0
            bullets.clear()
            game_over = False
        return

    # normal controls
    if key in (b'c', b'C'):
        cheat_mode = not cheat_mode; return
    elif key in (b'v', b'V'):
        auto_follow = not auto_follow; return

    # movement keys
    if key == b'w':
        player_pos[0] += player_direction[0] * speed
        player_pos[1] += player_direction[1] * speed
    elif key == b's':
        player_pos[0] -= player_direction[0] * speed
        player_pos[1] -= player_direction[1] * speed
    elif key == b'a':
        gun_angle = (gun_angle + 5) % 360
    elif key == b'd':
        gun_angle = (gun_angle - 5) % 360

    # update facing vector
    rad = math.radians(gun_angle)
    player_direction[0] = math.sin(-rad)
    player_direction[1] = math.cos(rad)

    # clamp player inside the square boundary
    player_pos[0] = max(-GRID_LENGTH, min(GRID_LENGTH, player_pos[0]))
    player_pos[1] = max(-GRID_LENGTH, min(GRID_LENGTH, player_pos[1]))


def specialKeyListener(key, x, y):
    global cam_theta, cam_phi
    delta = math.radians(5)

    if key == GLUT_KEY_LEFT:
        cam_theta += delta
    elif key == GLUT_KEY_RIGHT:
        cam_theta -= delta
    elif key == GLUT_KEY_UP:
        cam_phi = min(cam_phi + delta, math.radians(89))
    elif key == GLUT_KEY_DOWN:
        cam_phi = max(cam_phi - delta, math.radians(-89))

    glutPostRedisplay()


def mouseListener(button, state, x, y):
    global bullets, follow_gun
    
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        # Fire along the player's current facing direction
        dx, dy = player_direction[0], player_direction[1]
        
        # Gun muzzle position
        gun_x = player_pos[0] + 60 * dx
        gun_y = player_pos[1] + 60 * dy
        gun_z = player_pos[2] + 30
        
        # Create bullet with same direction vector
        bullet = [gun_x, gun_y, gun_z, dx, dy, 0, 100]
        bullets.append(bullet)
    elif button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        follow_gun = not follow_gun
        glutPostRedisplay()


def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.25, 0.1, 1500)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    if follow_gun:
        # first‑person camera
        rad = math.radians(gun_angle)
        dx = math.sin(-rad)
        dy = math.cos(rad)
        eye_x = player_pos[0] + dx * 10
        eye_y = player_pos[1] + dy * 10
        eye_z = player_pos[2] + 30

        # decide look‑at direction
        if cheat_mode and auto_follow:
            # follow rotating gun
            center_x = player_pos[0] + dx * 100
            center_y = player_pos[1] + dy * 100
        else:
            # always look straight ahead using player_direction
            pdx, pdy = player_direction[0], player_direction[1]
            center_x = player_pos[0] + pdx * 100
            center_y = player_pos[1] + pdy * 100

        center_z = player_pos[2]
        gluLookAt(eye_x, eye_y, eye_z,
                  center_x, center_y, center_z,
                  0, 0, 1)
    else:
        # third‑person spherical camera
        x = camera_radius * math.cos(cam_phi) * math.cos(cam_theta)
        y = camera_radius * math.cos(cam_phi) * math.sin(cam_theta)
        z = camera_radius * math.sin(cam_phi)
        gluLookAt(x, y, z, 0, 0, 0, 0, 0, 1)


def idle():
    global bullets, gun_angle, life, misses, score, game_over, enemy_positions

    if game_over:
        return

    # only fire a new volley when there are no active bullets
    if cheat_mode and not bullets:
        px, py, pz = player_pos
        for ex, ey, ez in enemy_positions:
            vx, vy = ex - px, ey - py
            dist = math.hypot(vx, vy)
            if dist <= 0: 
                continue
            dx, dy = vx/dist, vy/dist
            gun_angle = math.degrees(math.atan2(vy, vx))
            gun_x = px + dx * 60
            gun_y = py + dy * 60
            gun_z = pz + 30
            bullets.append([gun_x, gun_y, gun_z, dx, dy, 0, 100])

    # move bullets, detect hits or misses
    new_bullets = []
    for bx, by, bz, dx, dy, dz, life_b in bullets:
        bx += dx * bullet_speed
        by += dy * bullet_speed
        life_b -= 1

        # check hit
        hit_idx = None
        for ei, (ex, ey, ez) in enumerate(enemy_positions):
            if math.hypot(bx - ex, by - ey) < 25:
                score += 1
                hit_idx = ei
                break

        if hit_idx is not None:
            # respawn hit enemy at a safe distance
            while True:
                rx = random.uniform(-GRID_LENGTH + 50, GRID_LENGTH - 50)
                ry = random.uniform(-GRID_LENGTH + 50, GRID_LENGTH - 50)
                if math.hypot(rx - player_pos[0], ry - player_pos[1]) >= MIN_SPAWN_DISTANCE:
                    enemy_positions[hit_idx] = (rx, ry, 0)
                    break
            continue    

        # keep bullet alive
        if life_b > 0 and abs(bx) < GRID_LENGTH and abs(by) < GRID_LENGTH:
            new_bullets.append([bx, by, bz, dx, dy, dz, life_b])
        else:
            # only count misses in normal mode
            if not cheat_mode:
                misses += 1

    bullets[:] = new_bullets

    updated_enemies = []
    px, py, pz = player_pos
    for ex, ey, ez in enemy_positions:
        vx = px - ex
        vy = py - ey
        dist = math.hypot(vx, vy)
        if dist > 0:
            ex += (vx/dist) * enemy_speed
            ey += (vy/dist) * enemy_speed
        updated_enemies.append((ex, ey, ez))
    enemy_positions[:] = updated_enemies

    # enemy‑touch‑player collision
    for idx, (ex, ey, ez) in enumerate(enemy_positions):
        if math.hypot(ex - player_pos[0], ey - player_pos[1]) < 50:
            life -= 1
            # immediately respawn that enemy so it can't repeatedly collide
            rx = random.uniform(-GRID_LENGTH + 50, GRID_LENGTH - 50)
            ry = random.uniform(-GRID_LENGTH + 50, GRID_LENGTH - 50)
            enemy_positions[idx] = (rx, ry, 0)
            break

    # check Game Over
    if life <= 0 or misses >= 10:
        game_over = True

    glutPostRedisplay()

def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()  # Reset modelview matrix
    glViewport(0, 0, 1000, 800)  # Set viewport size

    setupCamera()  # Configure camera perspective

    # Draw a random points
    glPointSize(20)
    glBegin(GL_POINTS)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, 0)
    glEnd()

    # Draw the grid floor with vertical boundaries
    draw_grid_with_boundaries()

    # Display game info text at a fixed screen position
    draw_text(10, 770, f"Player Life Remaining: {life}")
    draw_text(10, 740, f"Game Score: {score}")
    draw_text(10, 710, f"Player Bullet Missed: {misses}")

    draw_shapes()

    # Swap buffers for smooth rendering (double buffering)
    glutSwapBuffers()


# Main function to set up OpenGL window and loop
def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)  # Double buffering, RGB color, depth test
    glutInitWindowSize(1000, 800)  # Window size
    glutInitWindowPosition(0, 0)  # Window position
    wind = glutCreateWindow(b"3D OpenGL Intro")  # Create the window

    glutDisplayFunc(showScreen)  # Register display function
    glutKeyboardFunc(keyboardListener)  # Register keyboard listener
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)  # Register the idle function to move the bullet automatically

    glutMainLoop()  # Enter the GLUT main loop

if __name__ == "__main__":
    main()