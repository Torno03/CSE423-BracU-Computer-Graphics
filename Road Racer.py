from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import random
import sys


WINDOW_WIDTH  = 600
WINDOW_HEIGHT = 800

y1, y2, y3, y4 = 400, 350, 350, 300
check = False
start = False
level = [10, 20, 30, 40, 50]
player_car = [0,-300,52,72]
incoming_cars = []
is_collision_detected = False
score = 0
speed = 0.7
distance = 0
car_avoided = 0

#------------Algorithm---------------

# Function for finding Zone
def findZone(dx, dy):
    if abs(dx) > abs(dy):
        if dx >= 0 and dy >= 0:  # zone 0
            return "zone0"
        elif dx <= 0 and dy >= 0:  # zone 3
            return "zone3"
        elif dx <= 0 and dy <= 0:  # zone 4
            return "zone4"
        elif dx >= 0 and dy <= 0:  # zone 7
            return "zone7"
    else:
        if dx >= 0 and dy >= 0:  # zone 1
            return "zone1"
        elif dx <= 0 and dy >= 0:  # zone 2
            return "zone2"
        elif dx <= 0 and dy <= 0:  # zone 5
            return "zone5"
        elif dx >= 0 and dy <= 0:  # zone 6
            return "zone6"

# Function to convert from Zone 0 to any other zone (reflection of coordinates)
def convert_to_zone_0(x,y,zone):
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

# Function to convert back from Zone 0 to the original zone
def convert_from_zone_0(x,y,zone):
    if zone == "zone0":  # zone 0
        glVertex2f(x, y)
    elif zone == "zone1":  # zone 1
        glVertex2f(y, x)
    elif zone == "zone2":  # zone 2
        glVertex2f(-y, x)
    elif zone == "zone3":  # zone 3
        glVertex2f(-x, y)
    elif zone == "zone4":  # zone 4
        glVertex2f(-x, -y)
    elif zone == "zone5":  # zone 5
        glVertex2f(-y, -x)
    elif zone == "zone6":  # zone 6
        glVertex2f(y, -x)
    elif zone == "zone7":  # zone 7
        glVertex2f(x, -y)

#Midpoint Line Drawing Algorithm to draw a line from (x1, y1) to (x2, y2)
def midPoint(x1,y1,x2,y2):
   dx = x2 - x1
   dy = y2 - y1
   zone = findZone(dx, dy)
   x1,y1 = convert_to_zone_0(x1,y1,zone)
   x2,y2 = convert_to_zone_0(x2,y2,zone)

   dx = x2 - x1
   dy = y2 - y1

   d = 2 * dy - dx
   incrE = 2 * dy
   incrNE = 2 * (dy - dx)

   x = x1
   y = y1
   while x <= x2:
       convert_from_zone_0(x,y,zone)
       x += 1
       if d > 0:
           d += incrNE
           y += 1
       else:
           d += incrE

# Midpoint Circle Algorithm to draw a circle with center (x, y) and radius (Zone 1)
def drawCircle(radius,xOG,yOG):
    d = 1 - radius
    x = 0
    y = radius
    while x < y:
        glVertex2f(x+xOG, y+yOG)
        glVertex2f(y+xOG, x+yOG)
        glVertex2f(y+xOG, (x*-1)+yOG)
        glVertex2f(x+xOG, (y*-1)+yOG)
        glVertex2f((x*-1)+xOG, (y*-1)+yOG)
        # glVertex2f((y*-1)+xOG,(x*-1)+yOG)
        # glVertex2f((y*-1)+xOG, x+yOG)
        glVertex2f((x*-1)+xOG, y+yOG)
        if d < 0:
            d = d + (2*x) + 3
            x += 1
        else:
            d = d + (2*x) - (2*y) + 5
            x += 1
            y -= 1

#ROAD
def sidewaysWhite():
    global y1,y2,y3,y4
    sideways = []
    for i in range(9):  
        sideways.append([-296, y1,-296,y2])
        y1-=100
        y2 -= 100
    return sideways
sidewaysWhite = sidewaysWhite()

def sideways_blue():
    global y1,y2,y3,y4
    sidewaysBlue = []
    for i in range(9):  
        sidewaysBlue.append([-296, y3, -296, y4])
        y3 -=100
        y4 -= 100
    return sidewaysBlue

sidewaysBlue = sideways_blue()

def init_road():
    y= 400
    y1 = 340
    road = []
    for i in range(6):  
        road.append([None, y,None,y1])
        y-=140
        y1 -= 140
    return road
road = init_road()

#Draw
def drawRoad():
    global y1, y2, y3, y4,sidewaysWhite,sidewaysBlue
    glPointSize(5)
    glBegin(GL_POINTS)

    #Sideways
    for i in sidewaysWhite:
        glColor3f(1,1,1)
        midPoint(i[0],i[1],i[2],i[3])
        midPoint(-i[0],i[1],-i[2],i[3])
    for i in sidewaysBlue:
        glColor3f(0,0,1)
        midPoint(i[0],i[1],i[2],i[3])
        midPoint(-i[0],i[1],-i[2],i[3])

    #Lane
    for i in road:
        glColor3f(0.5, 0.5, 0.5)
        midPoint(-150, i[1], -150, i[3])
        midPoint(0, i[1], 0, i[3])
        midPoint(150, i[1], 150, i[3])
    glEnd()

#CAR
def drawCar(x,y):
    glBegin(GL_POINTS)
    midPoint(x+22,y+32,x+22,y-28)
    midPoint(x+22,y+32,x+12,y+37)
    midPoint(x+22,y-28,x+12,y-33)

    midPoint(x+22,y+17,x+27,y+17)
    midPoint(x+22,y+27,x+27,y+27)
    midPoint(x+22,y-13,x+27,y-13)
    midPoint(x+22,y-23,x+27,y-23)
    midPoint(x+27,y+17,x+27,y+27)
    midPoint(x+27,y-13,x+27,y-23)

    drawCircle(2, x, y)


    midPoint(x-8,y+37,x+12,y+37)
    midPoint(x-8,y-33,x+12,y-33)

    midPoint(x-18,y+32,x-18,y-28)
    midPoint(x-18,y+32,x-8,y+37)
    midPoint(x-18,y-28,x-8,y-33)

    midPoint(x-18,y+17,x-23,y+17)
    midPoint(x-18,y+27,x-23,y+27)
    midPoint(x-18,y-13,x-23,y-13)
    midPoint(x-18,y-23,x-23,y-23)
    midPoint(x-23,y+17,x-23,y+27)
    midPoint(x-23,y-13,x-23,y-23)    
    glEnd()

#Incoming Cars
def incdrawCar(x, y):
    glBegin(GL_POINTS)
    midPoint(x+22,y+30,x+22,y-30)
    midPoint(x+22,y+30,x+12,y+35)
    midPoint(x+22,y-30,x+12,y-35)

    midPoint(x+22,y+15,x+27,y+15)
    midPoint(x+22,y+25,x+27,y+25)
    midPoint(x+22,y-15,x+27,y-15)
    midPoint(x+22,y-25,x+27,y-25)
    midPoint(x+27,y+15,x+27,y+25)
    midPoint(x+27,y-15,x+27,y-25)

    midPoint(x-8,y+35,x+12,y+35)
    midPoint(x-8,y-35,x+12,y-35)

    midPoint(x-18,y+30,x-18,y-30)
    midPoint(x-18,y+30,x-8,y+35)
    midPoint(x-18,y-30,x-8,y-35)

    midPoint(x-18,y+15,x-23,y+15)
    midPoint(x-18,y+25,x-23,y+25)
    midPoint(x-18,y-15,x-23,y-15)
    midPoint(x-18,y-25,x-23,y-25)
    midPoint(x-23,y+15,x-23,y+25)
    midPoint(x-23,y-15,x-23,y-25)    
    glEnd()

def drawIncomingCars():
    global x_value
    for car in incoming_cars:
        glColor3f(*car[2])
        incdrawCar(car[0], car[1])


def init_incoming_cars():
    cars = []
    y_spacing = 100

    while len(cars) < 8:
        
        x = random.randint(-270, 270)
        y = random.randint(300, 800)

        color_choice = random.choice([(255,0,0),(255,165,0),(255,255,0),(0,0,255),(75,0,130),(128,0,128),(255,140,0),(0,128,0),(128,128,0),(0,128,128),(0,255,255),(139,0,139),(255,192,203)])
        
        flag = 0
        for car in cars:
            if abs(car[0]-x) + abs(car[1]-y) <= 200:
                flag = 1
                break
        if flag == 0:
            cars.append([x, y, color_choice])

    return cars

incoming_cars = init_incoming_cars()

#Button
def drawButton():
   
    glPointSize(3)
    glBegin(GL_POINTS)

     #Exit
    glColor3f(1,0,0)
    midPoint(245,365,270,335)
    midPoint(245,335,270,365)

    if check == False:
        #Pause
        glColor3f(1, 0.5, 0.5)

        midPoint(5,365,5,335)
        midPoint(-6,335,-6,365)
    else:
        #play
        glColor3f(1, 0.5, 0.5)
        midPoint(-10, 365, -10, 335)
        midPoint(-10, 365, +10, 350)
        midPoint(-10, 335, +10, 350)

    
    #Reset
    glColor3f(0.5,1,0.5)
    drawCircle(15,-260,350)
    midPoint(-270,360,-260,350)
    midPoint(-270,360,-260,370)
    glEnd()

def check_collision(car1_x, car1_y, car1_width, car1_height, car2_x, car2_y, car2_width, car2_height):
    global is_collision_detected
    car1_left = car1_x - (car1_width/2)
    car1_right = car1_x + (car1_width/2)
    car1_top = car1_y + (car1_height/2)
    car1_bottom = car1_y - (car1_height/2)

    car2_left = car2_x - (car2_width/2)
    car2_right = car2_x + (car2_width/2)
    car2_top = car2_y + (car2_height/2)
    car2_bottom = car2_y - (car2_height/2)

    if (car1_right >= car2_left and car1_left <= car2_right and
            car1_top >= car2_bottom and car1_bottom <= car2_top):
        is_collision_detected = True
    
def check_player_collision():
    global player_car, incoming_cars,is_collision_detected
    for car in incoming_cars:
        incoming_car_x, incoming_car_y = car[0], car[1]
        incoming_car_width = player_car[2] 
        incoming_car_height = player_car[3]
        check_collision(player_car[0], player_car[1], player_car[2], player_car[3],incoming_car_x, incoming_car_y, incoming_car_width, incoming_car_height)                          

def drawPlay():
    glBegin(GL_POINTS)
    midPoint(-60,40,60,40)
    midPoint(-60,-40,60,-40)
    midPoint(-60,-40,-60,40)
    midPoint(60,-40,60,40)
    midPoint(-15,-20,-15,20)
    midPoint(-15,-20,15,0)
    midPoint(-15,20,15,0)
    glEnd()

def show_screen():
    global check, score, is_collision_detected, start, distance, car_avoided
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    drawButton()
    if start == True:
        drawRoad()
        glColor3f(1, 0.5, 0)
        drawCar(player_car[0], player_car[1])
        drawIncomingCars()
        
        score_text = f'Score: {score}'
        glColor3f(1, 1, 1)
        glRasterPos2f(-220, 365)
        for char in score_text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))

        distance_text = f'Distance: {distance} mm'
        glColor3f(1, 1, 1)
        glRasterPos2f(-220, 345)
        for char in distance_text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))

        car_avoided_text = f'Car Avoided: {car_avoided}'
        glColor3f(1, 1, 1)
        glRasterPos2f(-220, 325)
        for char in car_avoided_text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))

        if check and is_collision_detected != True:
            glColor3f(1, 1, 0)
            glRasterPos2f(-55, 0)
            for char in "Game Paused":
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
        if is_collision_detected:
            glColor3f(1, 1, 0)
            glRasterPos2f(-50, 0)
            for char in "Game Over":
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))

            score_text = f'Your last score: {score}'
            glRasterPos2f(-70, -30)
            for char in score_text:
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
    else:
        drawPlay()

    glutSwapBuffers()

def toggle():
    global check
    check= not check

def animate():
    global y1, y2, y3, y4, sidewaysWhite, sidewaysBlue, road, check, score, x_value, speed, start, distance, car_avoided
    check_player_collision()
    if start == True:
        if is_collision_detected != True:
            if check != True:
                
            
                
                #--level try--------
                if score==level[0]:
                    speed = 0.9
                if score==level[1]:
                    speed = 1.1
                if score==level[2]:
                    speed = 1.3
                if score==level[3]:
                    speed = 1.5
                if score==level[4]:
                    speed = 1.7
                #------------------
                for i in sidewaysWhite:
                    i[1] -= speed
                    i[3] -= speed
                    if i[3]<-450:
                        i[1] = 450
                        i[3] = 400
                for y1 in sidewaysBlue:
                    y1[1] -= speed
                    y1[3] -= speed
                    if y1[3]<-450:
                        y1[1] = 450
                        y1[3] = 400
                for y1 in road:
                    y1[1] -= speed
                    y1[3] -= speed
                    if y1[3]<-450:
                        y1[1] = 450
                        y1[3] = 400
                        score += 1
                        distance += 1
                        print("Distance travelled by 1mm, Score Increased by 1")
  
                for car in incoming_cars:
                    car[1] -= speed
                    if car[1] < -500:
                        while True:
                            x = random.randint(-270, 270)
                            y = random.randint(300, 800)

                            color_choice = random.choice([(255,0,0),(255,165,0),(255,255,0),(0,0,255),(75,0,130),(128,0,128),(255,140,0),(0,128,0),(128,128,0),(0,128,128),(0,255,255),(139,0,139),(255,192,203)])
                            
                            flag = 0
                            for new_car in incoming_cars:
                                if abs(new_car[0]-x) + abs(new_car[1]-y) <= 200:
                                    flag = 1
                                    break
                            if flag == 0:
                                car[0] = x
                                car[1] = y
                                break
                        ## point system
                        car_avoided += 1
                        score += 1
                        print("Avoided one car successfully, Score Increased by 1")
    glutPostRedisplay()

def keyboardListener(key, x, y):
    global check,player_car,start
    if key==b' ':
        toggle()
    if key == b'a' and not check and not is_collision_detected:
        if player_car[0] -50 > -WINDOW_WIDTH / 2:
            player_car[0] -= 25
    if key == b'd' and not check and not is_collision_detected:
        if player_car[0] + 50 < WINDOW_WIDTH / 2:
            player_car[0] += 25

    if key == b'w' and not check and not is_collision_detected:
        if player_car[1] + 50 < WINDOW_HEIGHT / 2:
            player_car[1] += 25
    if key == b's' and not check and not is_collision_detected:
        if player_car[1] - 50 > -WINDOW_HEIGHT / 2:
            player_car[1] -= 25

    if key==b'g':
        start = True


def check_exit_button_click(x, y):
    return 545 <= x <= 570 and 730 <= y <= 765

def check_pause_button_click(x,y):
    return 290 <= x <= 320 and 730 <= y <= 765

def check_reset_button(x,y):
    return 20 <= x <= 60 and 730 <= y <= 765

def check_start_button_click(x,y):
    return 188 <= x <= 312 and 355 <= y <= 445

def mouse_click(button, state, x, y):
    global speed, check, score, is_collision_detected, incoming_cars, player_car, start, distance, car_avoided
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        y = WINDOW_HEIGHT-y
        if check_exit_button_click(x,y):
            print('Exiting')
            glutLeaveMainLoop()

        if check_pause_button_click(x,y):
            toggle()

        if check_reset_button(x,y):
            speed = 0.5
            check = False
            score = 0
            distance = 0
            car_avoided = 0
            is_collision_detected = False
            incoming_cars = init_incoming_cars()
            player_car[0] = 0
            player_car[1] =-300
            print("Resetting Game")
        
        if check_start_button_click(x,y):
            start = True
            print('starting')
            print('WASD to Move // Space = Pause')

def initialize():
    glViewport(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-WINDOW_WIDTH/2, WINDOW_WIDTH/2, -WINDOW_HEIGHT/2, WINDOW_HEIGHT/2, 0.0, 1.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glutMouseFunc(mouse_click)

glutInit()
glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
glutInitWindowPosition(0, 0)
wind = glutCreateWindow(b"Traffic Racer")

glutDisplayFunc(show_screen)
glutIdleFunc(animate)
glutKeyboardFunc(keyboardListener)

glEnable(GL_DEPTH_TEST)
initialize()
glutMainLoop()
