from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import sys, math, random, time

# --- Configuration ---
WINDOW_WIDTH, WINDOW_HEIGHT = 1000, 800
TRACK_WIDTH = 6.0
BALL_RADIUS = 0.5
MARGIN_FROM_EDGE = 0.6
FIRE_DURATION = 5.0
BALL_SPEED_INCREMENT = 0.00001
MAX_BALL_SPEED = 0.2
POWERUP_MIN_DIST = 150.0
last_powerup_z = -POWERUP_MIN_DIST

# --- Game State ---
paused = False
pause_start_time = 0
pause_message_blink = 0
last_resume_time = 0
game_over = False
score = 0
high_score = 0
health = 3

ball_x, ball_y, ball_z = 0.0, 0.0, 0.0
ball_speed = 0.05
ball_vel_y = 0.0
jumping = False

track_points = []
obstacles = []
pitfalls = set()
used_obstacles = set()
used_pitfalls = set()

# Powerups (shield & fire from Rodu4)
powerups = []  # Each is (x, y, z, ptype)
shield_active = False
shield_hits_remaining = 0
fire_active = False
fire_end_time = 0.0

# Additional powerups (from baler_game‑chudi)
health_powerups = []         # (x, y, z, size)
double_score_powerups = []   # (x, y, z, size)
slowmo_powerups = []         # (x, y, z, size)
speed_powerups = []          # (x, y, z, size)
double_score_active = False
double_score_start_time = 0
slowmo_active = False
slowmo_start_time = 0
speed_boost_active = False
speed_boost_start_time = 0

colors = [(1, 0, 0), (1, 0.5, 0), (1, 1, 0),
          (0, 1, 0), (0, 1, 1), (0, 0, 1), (1, 0, 1)]

# --- Helper Functions ---
def generate_track():
    global last_powerup_z
    z = track_points[-1][2] + 1 if track_points else 0.0
    for _ in range(50):
        x = math.sin(z * 0.05) * 5
        y = math.cos(z * 0.03) * 1
        track_points.append((x, y, z))
        
        # Add pitfalls every 40 units
        if int(z) % 40 == 0:
            pitfalls.add(int(z))
            
        # Spawn obstacles (using Rodu4 style: cube or sphere)
        if random.random() < 0.1:
            ox = x + random.uniform(-TRACK_WIDTH/2 + BALL_RADIUS, TRACK_WIDTH/2 - BALL_RADIUS)
            shape = random.choice(['cube', 'sphere'])
            size = random.uniform(0.5, 1.0)
            color = random.choice(colors)
            obstacles.append((ox, y + size/2, z, size, shape, color))
        
        # Spawn shield/fire powerups if enough distance passed
        if z - last_powerup_z >= (POWERUP_MIN_DIST/4):
            if random.random() < 0.2:
                px = x + random.uniform(-TRACK_WIDTH/4, TRACK_WIDTH/4)
                ptype = random.choice(['shield', 'fire'])
                powerups.append((px, y + 0.5, z, ptype))
                last_powerup_z = z
        
        # Spawn extra powerups (from baler_game‑chudi)
        if int(z) % 75 == 0:
            dx = x + random.uniform(-TRACK_WIDTH/2 + BALL_RADIUS + 0.5, TRACK_WIDTH/2 - BALL_RADIUS - 0.5)
            size = 0.6
            double_score_powerups.append((dx, y + 0.3, z, size))
        if int(z) % 100 == 0:
            hx = x + random.uniform(-TRACK_WIDTH/2 + BALL_RADIUS + 0.5, TRACK_WIDTH/2 - BALL_RADIUS - 0.5)
            size = 0.6
            health_powerups.append((hx, y + 0.3, z, size))
        if int(z) % 60 == 0:
            sx = x + random.uniform(-TRACK_WIDTH/2 + BALL_RADIUS + 0.5, TRACK_WIDTH/2 - BALL_RADIUS - 0.5)
            size = 0.5
            speed_powerups.append((sx, y + 0.3, z, size))
        if int(z) % 90 == 0:
            mx = x + random.uniform(-TRACK_WIDTH/2 + BALL_RADIUS + 0.5, TRACK_WIDTH/2 - BALL_RADIUS - 0.5)
            size = 0.6
            slowmo_powerups.append((mx, y + 0.3, z, size))
        
        z += 1

def get_track_y(z):
    i = int(z)
    return track_points[i][1] if 0 <= i < len(track_points) else 0.0

# --- Drawing Functions ---
def draw_track():
    glBegin(GL_QUAD_STRIP)
    for i, (x, y, z) in enumerate(track_points):
        if i in pitfalls:
            continue
        glColor3f(*colors[i % len(colors)])
        glVertex3f(x - TRACK_WIDTH / 2, y, z)
        glVertex3f(x + TRACK_WIDTH / 2, y, z)
    glEnd()

def draw_ball():
    t = glutGet(GLUT_ELAPSED_TIME) / 1000.0
    glow = 0.5 + 0.5 * math.sin(t * 6)
    glPushMatrix()
    glTranslatef(ball_x, ball_y + BALL_RADIUS, ball_z)
    if fire_active:
        glColor3f(1.0, 0.5, 0.0)
    else:
        glColor3f(0.6 + glow * 0.4, 0.2 + glow * 0.2, 1.0)
    glutSolidSphere(BALL_RADIUS, 20, 20)
    glPopMatrix()
    
    # Draw shield overlay if active
    if shield_active:
        glPushMatrix()
        glTranslatef(ball_x, ball_y + BALL_RADIUS, ball_z)
        glColor4f(0.0, 1.0, 1.0, 0.4)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glutWireSphere(BALL_RADIUS + 0.2, 16, 16)
        glDisable(GL_BLEND)
        glPopMatrix()

def draw_obstacles():
    for x, y, z, size, shape, color in obstacles:
        glPushMatrix()
        glColor3f(*color)
        glTranslatef(x, y, z)
        glScalef(size, size, size)
        if shape == 'cube':
            glutSolidCube(1)
        else:
            glutSolidSphere(0.5, 16, 16)
        glPopMatrix()

def draw_powerups():
    # Draw shield/fire powerups
    for x, y, z, ptype in powerups:
        if ptype == 'fire':
            glColor3f(1.0, 0.5, 0.0)
            ch = 'F'
        else:
            glColor3f(0.0, 1.0, 1.0)
            ch = 'S'
        glPushMatrix()
        glRasterPos3f(x, y, z)
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
        glPopMatrix()

def draw_health_powerups():
    t = glutGet(GLUT_ELAPSED_TIME) / 1000.0
    shimmer = 0.6 + 0.4 * math.sin(t * 4)
    for x, y, z, size in health_powerups:
        glPushMatrix()
        glColor4f(1.0, 0.2 + 0.5 * math.sin(t * 4), 0.2 + 0.5 * math.sin(t * 4), shimmer)
        glTranslatef(x, y + math.sin(t * 2) * 0.3, z)
        glScalef(size, size, size)
        glBegin(GL_POLYGON)
        for angle in range(0, 360, 30):
            rad = math.radians(angle)
            heart_x = 0.5 * math.sin(rad) * abs(math.sin(rad))
            heart_y = 0.5 * math.cos(rad)
            glVertex3f(heart_x, heart_y, 0)
        glEnd()
        glPopMatrix()

def draw_double_score_powerups():
    t = glutGet(GLUT_ELAPSED_TIME) / 1000.0
    shimmer = 0.6 + 0.4 * math.sin(t * 5)
    for x, y, z, size in double_score_powerups:
        glPushMatrix()
        glColor4f(1.0, 1.0, 1.0, shimmer)
        glTranslatef(x, y + math.sin(t * 2) * 0.3, z)
        glScalef(size, size, size)
        glBegin(GL_QUADS)
        glVertex3f(-0.3, 0.3, 0)
        glVertex3f(0.3, 0.3, 0)
        glVertex3f(0.3, -0.3, 0)
        glVertex3f(-0.3, -0.3, 0)
        glEnd()
        glPopMatrix()

def draw_speed_powerups():
    t = glutGet(GLUT_ELAPSED_TIME) / 1000.0
    shimmer = 0.6 + 0.4 * math.sin(t * 8)
    for x, y, z, size in speed_powerups:
        glPushMatrix()
        glColor4f(1.0, 1.0, 1.0, shimmer)
        glTranslatef(x, y + math.sin(t * 3) * 0.3, z)
        glRotatef(t * 180 % 360, 1, 0, 0)
        glScalef(size * 1.5, size * 2.0, size * 1.5)
        glBegin(GL_TRIANGLES)
        glVertex3f(0.0, 0.5, 0)
        glVertex3f(-0.2, -0.5, 0)
        glVertex3f(0.2, -0.5, 0)
        glEnd()
        glPopMatrix()

def draw_slowmo_powerups():
    t = glutGet(GLUT_ELAPSED_TIME) / 1000.0
    shimmer = 0.6 + 0.4 * math.sin(t * 6)
    for x, y, z, size in slowmo_powerups:
        glPushMatrix()
        glColor4f(1.0, 1.0, 1.0, shimmer)
        glTranslatef(x, y + math.cos(t * 2) * 0.2, z)
        glRotatef(t * 90 % 360, 0, 1, 0)
        glScalef(size, size, size)
        glBegin(GL_POLYGON)
        for angle in range(0, 360, 30):
            rad = math.radians(angle)
            glVertex3f(math.cos(rad) * 0.5, math.sin(rad) * 0.5, 0)
        glEnd()
        glPopMatrix()

def draw_pitfalls():
    glColor3f(1, 1, 0)
    for i in pitfalls:
        if 0 <= i < len(track_points):
            x, y, z = track_points[i]
            glPushMatrix()
            glTranslatef(x, y - 0.2, z)
            glScalef(TRACK_WIDTH, 0.1, 0.5)
            glutSolidCube(1)
            glPopMatrix()

def draw_hud():
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glColor3f(1, 1, 1)
    glRasterPos2i(10, WINDOW_HEIGHT - 30)
    for ch in f"Score: {int(score)}  Health: {health}  High: {high_score}  BallX: {ball_x:.2f}  (P=Pause)":
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    
    if paused:
        t = glutGet(GLUT_ELAPSED_TIME) / 500.0
        if int(t) % 2 == 0:
            glPushMatrix()
            glLoadIdentity()
            glColor3f(1.0, 0.8, 0.2)
            glRasterPos2i(WINDOW_WIDTH // 2 - 60, WINDOW_HEIGHT // 2 + 20)
            for ch in b"=== PAUSED ===":
                glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ch)
            glPopMatrix()
    
    if game_over:
        glPushMatrix()
        glLoadIdentity()
        glColor3f(1.0, 0.4, 0.4)
        glRasterPos2i(WINDOW_WIDTH // 2 - 90, WINDOW_HEIGHT // 2 + 30)
        for ch in b"* GAME OVER *":
            glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ch)
        glRasterPos2i(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 - 20)
        for ch in b"Press 'R' to Restart":
            glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ch)
        glPopMatrix()

# --- Game Logic ---
def update_game():
    global ball_speed, ball_z, ball_x, ball_y, jumping, ball_vel_y, score
    global shield_active, shield_hits_remaining, fire_active, fire_end_time, health, game_over
    global double_score_active, double_score_start_time, slowmo_active, slowmo_start_time
    global speed_boost_active, speed_boost_start_time
    
    if paused or game_over:
        glutPostRedisplay()
        return

    if 0 <= int(ball_z) < len(track_points):
        cx = track_points[int(ball_z)][0]
        max_shift = TRACK_WIDTH / 2 - BALL_RADIUS - MARGIN_FROM_EDGE
        ball_x = max(min(ball_x, cx + max_shift), cx - max_shift)

    ball_z += ball_speed
    if not track_points or ball_z > track_points[-1][2] - 100:
        generate_track()

    if jumping:
        ball_vel_y -= 0.015
        ball_y += ball_vel_y
        if ball_y <= get_track_y(ball_z):
            ball_y = get_track_y(ball_z)
            ball_vel_y = 0
            jumping = False
    else:
        ball_y = get_track_y(ball_z)

    # Process shield/fire powerup collisions
    for i, (x, y, z, ptype) in enumerate(powerups):
        if abs(ball_z - z) < 0.6 and abs(ball_x - x) < 0.6 and not jumping:
            if ptype == 'shield':
                shield_active = True
                shield_hits_remaining = 5
                print("Shield activated")
            elif ptype == 'fire':
                fire_active = True
                fire_end_time = glutGet(GLUT_ELAPSED_TIME)/1000.0 + FIRE_DURATION
                print(f"Fire-mode for {FIRE_DURATION}s")
            powerups.pop(i)
            break

    # Process collisions with obstacles
    for i, (x, y, z, *_rest) in enumerate(obstacles):
        if i not in used_obstacles and abs(ball_z - z) < 0.6 and abs(ball_x - x) < 0.6:
            if not jumping:
                used_obstacles.add(i)
                if fire_active:
                    pass
                elif shield_active:
                    shield_hits_remaining -= 1
                    print(f"Shield absorbed obstacle, {shield_hits_remaining} left")
                    if shield_hits_remaining <= 0:
                        shield_active = False
                        print("Shield expired")
                else:
                    health -= 1
                    print(f"Health decreased due to obstacle at index={i}")
                    if health <= 0:
                        game_over = True
                        print("Game Over!")

    if fire_active and (glutGet(GLUT_ELAPSED_TIME)/1000.0) > fire_end_time:
        fire_active = False
        print("Fire-mode expired")

    # Process additional powerups from baler_game‑chudi
    if double_score_active and time.time() - double_score_start_time > 10:
        double_score_active = False
        print("Double Score ended")
    
    for i, (x, y, z, size) in enumerate(double_score_powerups[:]):
        if abs(ball_z - z) < 0.6 and abs(ball_x - x) < 0.6:
            double_score_active = True
            double_score_start_time = time.time()
            double_score_powerups.pop(i)
            print("Double Score activated!")
            break

    for i, (x, y, z, size) in enumerate(health_powerups[:]):
        if abs(ball_z - z) < 0.6 and abs(ball_x - x) < 0.6:
            if health < 5:
                health += 1
                print("Health Increased!")
            for j in range(10):
                angle = j * 36
                print(f"✨ Sparkle at angle {angle}°")
            health_powerups.pop(i)
            break

    if speed_boost_active and time.time() - speed_boost_start_time > 7:
        speed_boost_active = False
        print("Speed Boost ended")
    
    for i, (x, y, z, size) in enumerate(speed_powerups[:]):
        if abs(ball_z - z) < 0.6 and abs(ball_x - x) < 0.6:
            speed_boost_active = True
            speed_boost_start_time = time.time()
            speed_powerups.pop(i)
            print("Speed Boost activated!")
            break

    if slowmo_active and time.time() - slowmo_start_time > 6:
        slowmo_active = False
        print("Slow Motion ended")
    
    for i, (x, y, z, size) in enumerate(slowmo_powerups[:]):
        if abs(ball_z - z) < 0.6 and abs(ball_x - x) < 0.6:
            slowmo_active = True
            slowmo_start_time = time.time()
            slowmo_powerups.pop(i)
            print("Slow Motion activated!")
            break

    ball_speed = 0.08 if speed_boost_active else (0.035 if slowmo_active else 0.04)
    
    score += 0.1 if double_score_active else 0.05
    if ball_speed < MAX_BALL_SPEED:
        ball_speed = min(ball_speed + BALL_SPEED_INCREMENT, MAX_BALL_SPEED)
    glutPostRedisplay()

# --- Input Handlers ---
def keyboard(key, x, y):
    global jumping, ball_vel_y, game_over, ball_speed, ball_x, ball_y, ball_z, score, health, paused, high_score, shield_active, fire_active, fire_end_time, shield_hits_remaining
    if key == b'p':
        paused = not paused
        print("Paused" if paused else "Resumed")
    elif key == b' ' and not jumping and not paused:
        jumping = True
        ball_vel_y = 0.2
    elif key == b'r' and game_over:
        paused = False
        game_over = False
        score = 0
        high_score = 0
        health = 3
        ball_x = ball_y = ball_z = 0.0
        ball_speed = 0.05
        ball_vel_y = 0.0
        jumping = False
        used_obstacles.clear()
        used_pitfalls.clear()
        track_points.clear()
        obstacles.clear()
        pitfalls.clear()
        powerups.clear()
        shield_active = False
        shield_hits_remaining = 0
        fire_active = False
        fire_end_time = 0.0
        health_powerups.clear()
        double_score_powerups.clear()
        slowmo_powerups.clear()
        speed_powerups.clear()
        print("Game restarted.")
        generate_track()

def special_input(key, x, y):
    global ball_x
    if 0 <= int(ball_z) < len(track_points):
        cx = track_points[int(ball_z)][0]
        safe_shift = TRACK_WIDTH / 2 - BALL_RADIUS - MARGIN_FROM_EDGE
        if key == GLUT_KEY_RIGHT:
            ball_x = max(ball_x - 0.4, cx - safe_shift)
        elif key == GLUT_KEY_LEFT:
            ball_x = min(ball_x + 0.4, cx + safe_shift)

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60.0, WINDOW_WIDTH / WINDOW_HEIGHT, 1.0, 100.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(ball_x, ball_y + 3, ball_z - 7, ball_x, ball_y, ball_z, 0, 1, 0)
    draw_track()
    draw_ball()
    draw_pitfalls()
    draw_obstacles()
    draw_powerups()
    draw_health_powerups()
    draw_double_score_powerups()
    draw_speed_powerups()
    draw_slowmo_powerups()
    draw_hud()
    glutSwapBuffers()

def reshape(w, h):
    glViewport(0, 0, w, h)

def init():
    glClearColor(0.05, 0.05, 0.1, 1)
    glEnable(GL_DEPTH_TEST)

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutCreateWindow(b"Roller Ball Infinite - Merged")
    init()
    generate_track()
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(special_input)
    glutIdleFunc(update_game)
    glutMainLoop()

if __name__ == '__main__':
    main()