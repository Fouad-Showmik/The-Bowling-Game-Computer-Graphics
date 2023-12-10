from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import time

ball_x = 600
ball_y = 10
ball_radius = 15
ball_height = 60

bottle_positions = [(480, 700), (560, 700), (640, 700), (720, 700), (800, 700)]
bottle_height = 60

collision_flag = False
game_over_flag = False
win_flag = False
pause = False
cross=False

def plot_point(x, y):
    glPointSize(2)
    glBegin(GL_POINTS)
    glVertex2f(x, y)
    glEnd()

def draw_circle(xc, yc, x, y):
    plot_point(xc + x, yc + y)
    plot_point(xc - x, yc + y)
    plot_point(xc + x, yc - y)
    plot_point(xc - x, yc - y)
    plot_point(xc + y, yc + x)
    plot_point(xc - y, yc + x)
    plot_point(xc + y, yc - x)
    plot_point(xc - y, yc - x)

def midpoint_circle(xc, yc, r):
    x = 0
    y = r
    p = 1 - r
    draw_circle(xc, yc, x, y)
    while x < y:
        x += 1
        if p < 0:
            p += 2 * x + 1
        else:
            y -= 1
            p += 2 * (x - y) + 1
        draw_circle(xc, yc, x, y)

def draw_bottle(x, y, r, h):
    for i in range(0, r):
        midpoint_circle(x, y + r, r - i)
    eight_way_symmetry(x - r - 5, y - h, x + r + 5, y - h)
    eight_way_symmetry(x, y + r, x + r + 5, y - h)
    eight_way_symmetry(x, y + r, x - r - 5, y - h)

def draw_ball():
    global ball_x, ball_y, collision_flag, game_over_flag
    glColor3f(1.0, 0.0, 0.0)
    midpoint_circle(ball_x, ball_y + ball_radius, ball_radius)
    
def draw_cross():
    eight_way_symmetry(50, 780,30,760) 
    eight_way_symmetry(30, 780,50, 760)
    
def draw_reset():
    eight_way_symmetry(1220,770,1250, 770) 
    eight_way_symmetry(1220,770,1230, 780)
    eight_way_symmetry(1220,770,1230, 760)

def eight_way_symmetry(x0, y0, x1, y1):
    zone = findZone(x0, y0, x1, y1)
    x_0, y_0 = ZoneZeroConversion(zone, x0, y0)
    x_1, y_1 = ZoneZeroConversion(zone, x1, y1)
    MidPointLine(zone, x_0, y_0, x_1, y_1)

def findZone(x0, y0, x1, y1):
    dx = x1 - x0
    dy = y1 - y0
    if abs(dx) > abs(dy):
        if dx > 0 and dy > 0:
            return 0
        elif dx < 0 and dy > 0:
            return 3
        elif dx < 0 and dy < 0:
            return 4
        else:
            return 7
    else:
        if dx > 0 and dy > 0:
            return 1
        elif dx < 0 and dy > 0:
            return 2
        elif dx < 0 and dy < 0:
            return 5
        else:
            return 6

def ZoneZeroConversion(zone, x, y):
    if zone == 0:
        return x, y
    elif zone == 1:
        return y, x
    elif zone == 2:
        return -y, x
    elif zone == 3:
        return -x, y
    elif zone == 4:
        return -x, -y
    elif zone == 5:
        return -y, -x
    elif zone == 6:
        return -y, x
    elif zone == 7:
        return x, -y

def MidPointLine(zone, x0, y0, x1, y1):
    dx = x1 - x0
    dy = y1 - y0
    d_init = 2 * dy - dx
    d_e = 2 * dy
    d_ne = 2 * (dy - dx)
    x = x0
    y = y0
    while x <= x1:
        a, b = ZeroToOriginal(zone, x, y)
        plot_point(a, b)
        if d_init <= 0:
            x += 1
            d_init += d_e
        else:
            x += 1
            y += 1
            d_init += d_ne

def ZeroToOriginal(zone, x, y):
    if zone == 0:
        return x, y
    if zone == 1:
        return y, x
    if zone == 2:
        return -y, -x
    if zone == 3:
        return -x, y
    if zone == 4:
        return -x, -y
    if zone == 5:
        return -y, -x
    if zone == 6:
        return y, -x
    if zone == 7:
        return x, -y

def check_collision():
    global ball_y, collision_flag, game_over_flag, bottle_positions, win_flag
    for position in bottle_positions:
        if (
            position[0] - ball_radius <= ball_x <= position[0] + ball_radius
            and ball_y + ball_radius >= position[1]
        ):
            collision_flag = True
            if bottle_positions.index(position) != 2:
                bottle_positions.remove(position)
            else:
                win_flag = True
            return True
    return False

def check_game_over():
    global ball_y, bottle_positions, game_over_flag, win_flag
    if win_flag:
        return False
    for position in bottle_positions:
        if (
            position[0] - ball_radius <= ball_x <= position[0] + ball_radius
            and ball_y + ball_radius >= position[1]
        ):
            bottle_positions.remove(position)
            if len(bottle_positions) == 0:
                return True
    return False

def iterate():
    glViewport(0, 0, 1280, 800)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0.0, 1280, 0.0, 800, 0.0, 1.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

drawing_in_progress = False
def idle():
    global drawing_in_progress, ball_x, collision_flag, game_over_flag, ball_y, win_flag
    glColor3f(0.0, 0.0, 0.0)
    if not drawing_in_progress:
        drawing_in_progress = True
        showScreen()
        if not win_flag and not pause:
            ball_y += 10  # Update the y-coordinate for forward movement
        if check_collision():
            if win_flag:
                game_over_flag = True
            elif check_game_over():
                game_over_flag = True
        elif ball_y > 700:  # Check if the ball has passed through the gap
            game_over_flag = True
            win_flag = False
        drawing_in_progress = False
        glutSwapBuffers()
        time.sleep(0.05)  # Introduce a delay between frames for smoother animation
        
def reset_game():
    global ball_x, ball_y, collision_flag, game_over_flag, win_flag, bottle_positions
    ball_x = 600
    ball_y = 10
    collision_flag = False
    game_over_flag = False
    win_flag = False
    bottle_positions = [(480, 700), (560, 700), (640, 700), (720, 700), (800, 700)]

def keyboardListener(key, x, y):
    global pause

    if key == b' ':
        pause = not pause  # Toggle the pause state
        if not pause:
            glutTimerFunc(0, timer, 0)

    glutPostRedisplay()

def specialKeyListener(key, x, y):
    global ball_x
    if key == GLUT_KEY_RIGHT:
        ball_x += 10
    if key == GLUT_KEY_LEFT:
        ball_x -= 10
    glutPostRedisplay()
    

def mouseListener(button, state, x, y):
    global pause, cross
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        if 30 <= x <= 50 and (800 - 780) <= y <= (800 - 760):
            glutLeaveMainLoop()
        if 1220 <= x <= 1250 and (800-770) <= y <= (800-760):
            reset_game()
            print("New Game")
            glutPostRedisplay()

            
def timer(value):
    global ball_y, collision_flag, game_over_flag, win_flag, pause
    if not game_over_flag and not win_flag and not pause:
        ball_y += 10  # Update the y-coordinate for forward movement
        if check_collision():
            if win_flag:
                game_over_flag = True
            elif check_game_over():
                game_over_flag = True
    glutPostRedisplay()
    glutTimerFunc(25, timer, 0)

def showScreen():
    global collision_flag, game_over_flag, win_flag
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    iterate()
    glColor3f(1.0, 0.0, 0.0)
    eight_way_symmetry(0, 700, 1280, 700)
    draw_ball()
    draw_cross()
    draw_reset()
    glRasterPos2f(1000, 50) 
    text="Created By Group 6"
    for character in text:
        glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(character))
    if game_over_flag:
        if win_flag:
            glColor3f(0.0, 1.0, 0.0)
            glRasterPos2f(550, 400)  # Set position for the text
            text = "You Win!"
            for character in text:
                glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(character))
        else:
            glColor3f(1.0, 0.0, 0.0)
            glRasterPos2f(550, 400)  # Set position for the text
            text = "You Lose!"
            for character in text:
                glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(character))
            if not win_flag:  # Show remaining bottles only if not a win
                for position in bottle_positions:
                    draw_bottle(position[0], position[1], 15, 60)
    else:
        for position in bottle_positions:
            draw_bottle(position[0], position[1], 15, 60)
    glutSwapBuffers()

# Initialize OpenGL
glutInit()
glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE)
glutInitWindowSize(1280, 800)
glutInitWindowPosition(0, 0)
wind = glutCreateWindow(b"OpenGL Bowling Game")

# Register callbacks
glutDisplayFunc(showScreen)
glutIdleFunc(idle)
glutSpecialFunc(specialKeyListener)
glutTimerFunc(0, timer, 0)
glutKeyboardFunc(keyboardListener)
glutMouseFunc(mouseListener)
# Start the main loop
glutMainLoop()
