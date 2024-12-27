from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

import math
import random

W_Width, W_Height = 500,500
speed = 0
color = [1,1,1]
bg = [0,0,0]
check = False
black = 0
white = 1

def drawhouse():
    # Roof
    glBegin(GL_LINES)
    glVertex2d(-100, 0)
    glVertex2d(100, 0)

    glVertex2d(-100, 0)
    glVertex2d(0, 100)

    glVertex2d(100, 0)
    glVertex2d(0, 100)

    # Body
    glVertex2d(80, -100)
    glVertex2d(80, 0)

    glVertex2d(-80, -100)
    glVertex2d(-80, 0)

    glVertex2d(-80, -100)
    glVertex2d(80, -100)

    # Door
    glVertex2d(-40, -100)
    glVertex2d(-40, -30)

    glVertex2d(-40, -30)
    glVertex2d(-5, -30)

    glVertex2d(-5, -100)
    glVertex2d(-5, -30)

    glEnd()

    # Door knob
    glPointSize(2)
    glBegin(GL_POINTS)
    glVertex2f(-15, -65)
    glEnd()

    # Window
    glBegin(GL_LINES)
    glVertex2d(45, -30)
    glVertex2d(25, -30)

    glVertex2d(45, -30)
    glVertex2d(45, -50)

    glVertex2d(25, -30)
    glVertex2d(25, -50)

    glVertex2d(25, -50)
    glVertex2d(45, -50)

    glVertex2d(25, -40)
    glVertex2d(45, -40)

    glVertex2d(35, -30)
    glVertex2d(35, -50)
    glEnd()
       

def init_raindrops():
    raindrops = []
    for i in range(100):  
        x = random.uniform(-W_Width, W_Width)
        y = random.uniform(-W_Height, W_Height)
        raindrops.append([x, y])
    return raindrops

raindrops = init_raindrops()

def drawraindrop():
    glPointSize(4)
    glBegin(GL_POINTS)
    r,g,b = color
    glColor3f(r,g,b)
    for x,y in raindrops:
        glVertex2d(x,y)
    glEnd()
    

def display():

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    r,g,b=bg
    glClearColor(r,g,b,0);	#//color black
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(0,0,200,	0,0,0,	0,1,0)
    glMatrixMode(GL_MODELVIEW)
    drawraindrop()
    drawhouse()
    glutSwapBuffers()

def init():
    glClearColor(0,0,0,0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(104,	1,	1,	1000.0)

def animate():
    if check !=True:
        for i in range(len(raindrops)):
            raindrops[i][1] -= 0.13 
            if raindrops[i][1] < -W_Height:
                raindrops[i][1] = W_Height  
            raindrops[i][0] += speed
            if raindrops[i][0] < -W_Width:
                raindrops[i][0] = W_Width
            if raindrops[i][0] > W_Width:
                raindrops[i][0] = -W_Width
    glutPostRedisplay()

def toggle():
    global check
    check= not check

def specialKeyListener(key,x,y):
    global speed
    if key==GLUT_KEY_RIGHT and speed<.24:
        speed += 0.04
        print("Go Right")
    if key==GLUT_KEY_LEFT and speed>-.24: 
        speed -= 0.04   
        print("Go Left")
    glutPostRedisplay()

def keyboardListener(key, x, y):

    global color,bg,check,black,white

    if key==b'd':
        black+=.05
        white-=.05
        color = [white,white,white]
        bg = [black,black,black]
        print("Day time")
    if key==b'n':
        black-=.05
        white+=.05    
        color = [white,white,white]
        bg = [black,black,black]
        print("Night Time")
    if key==b' ':
        toggle()

            
    
glutInit()
glutInitWindowSize(W_Width, W_Height)
wind = glutCreateWindow(b"House with Rain")
init()
glutDisplayFunc(display)	
glutIdleFunc(animate)
print("D = Day // N = Night // Space = Pause/Play // Arrow = Wind")
glutSpecialFunc(specialKeyListener)
glutKeyboardFunc(keyboardListener)
glutMainLoop()	