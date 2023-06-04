# Simple Lorentz attractor
# Arthur Lovekin
# https://github.com/Josephbakulikira/Lorenz-attractor-3D---pygame/blob/master/main.py
import pygame
import numpy as np
import pygame_widgets
from pygame_widgets.slider import Slider
from pygame_widgets.textbox import TextBox

width = 800
height = 600
size = (width, height)
pygame.init()
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Lorenz attractor")
clock = pygame.time.Clock()

# Parameters
sigma = 10
rho = 28
beta = 8/3

# Initial conditions
max_length = 10000 # maximum length of the tail
points = np.ones((max_length, 3)) * np.nan # holds all the points of the tail
x0 = 0.1
y0 = 0
z0 = 0
points[0] = np.array([x0, y0, z0]) # initial point
dt = 0.01

# Drawing parameters
scale = 10 # scaling the size of the attractor
hue_shift = 260 # degrees to shift the hue (0 is red, 120 is green, 240 is blue)
tail_decay = 4 # how fast the tail fades (higher is faster, should be >1)
# pen_color = (255, 0, 0) # red
screen_color = (0, 0, 0)   #black
fps = 60
pen_size = 1
yaw_pitch_roll = np.array([0.0, 0.0, 0.0])
view_speed = 0.1
change_yaw_pitch_roll = np.array([0.0, view_speed, 0.0]) # change how fast the view rotates (higher = faster)
max_line_length = 5.5 # max length of a line segment (set later), affects color

def rotate(points, yaw_pitch_roll) -> np.ndarray:
    """
    Rotate points around the origin by the given Tait-Bryan Angles
    args:
        points: (N, 3) array of points
        The intrinsic rotations are performed in order of z, y, x:
        z_rotation: rotation around z-axis (yaw)
        y_rotation: rotation around y'-axis (pitch) (where y' is the y-axis after rotating around z)
        x_rotation: rotation around x''-axis (roll) (where x'' is the x-axis after rotating around z then y')
    returns:
        rotated points (N, 3)
    """
    z_rotation,y_rotation,x_rotation = yaw_pitch_roll
    Rz = np.array([[np.cos(z_rotation), -np.sin(z_rotation), 0],
                        [np.sin(z_rotation), np.cos(z_rotation), 0],
                        [0, 0, 1]])
    Ry = np.array([[np.cos(y_rotation), 0, np.sin(y_rotation)],
                        [0, 1, 0],
                        [-np.sin(y_rotation), 0, np.cos(y_rotation)]])    
    Rx = np.array([[1, 0, 0],
                     [0, np.cos(x_rotation), -np.sin(x_rotation)],
                     [0, np.sin(x_rotation), np.cos(x_rotation)]])
    R = Rz @ Ry @ Rx
    return points @ R

def calculate_lorenz(x0,y0,z0, sigma, rho, beta, dt, max_length):
    points = np.ones((max_length, 3)) * np.nan # holds all the points of the tail
    points[0] = np.array([x0, y0, z0]) # initial point
    for i in range(max_length-1):
        x, y, z = points[i]
        dx = sigma*(y-x)
        dy = x*(rho-z)-y
        dz = x*y-beta*z
        points[i+1] = points[i] + dt*np.array([dx, dy, dz])
    return points

def draw_lorenz(points_numpy):
    # draw the attractor
    color = pygame.Color(0)
    color.hsva = (hue_shift, 50, 100, 100)
    closed = False
    
    # rotate the points for viewing, and project to 2D
    points_rotated = rotate(points_numpy, yaw_pitch_roll)[:, :2]
    # yaw_pitch_roll = (yaw_pitch_roll + change_yaw_pitch_roll) % (2*np.pi)

    # points needs to be a list of 2D tuples
    points = [(x*scale+width/2, y*scale+height/2) for x, y in points_rotated]
    pygame.draw.lines(screen, color, closed, points)

def recalculate_and_redraw():
    # redraw the attractor
    points_np = calculate_lorenz(x0, y0, z0, sigma, rho, beta, dt, max_length)
    screen.fill(screen_color)
    draw_lorenz(points_np)


# sliders for relevant parameters
sigma_slider = Slider(screen, 10, 10, 100, 10, min=0.5, max=60, step=0.5, color=(255, 255, 255), initial=sigma, text="sigma")
sigma_output = TextBox(screen, 160, 9, 25, 12, fontSize=14,borderThickness=0)
sigma_box = TextBox(screen, 120, 9, 34, 12, fontSize=14,borderThickness=0, textColour=(0, 0, 0))
sigma_box.setText("sigma")

rho_slider = Slider(screen, 10, 25, 100, 10, min=0.5, max=60, step=0.5, color=(255, 255, 255), initial=rho )
rho_output = TextBox(screen, x=160, y=24, width=25, height=12, fontSize=14,borderThickness=0)
rho_box = TextBox(screen, 120, 24, 34, 12, fontSize=14,borderThickness=0, textColour=(0, 0, 0))
rho_box.setText("rho")

beta_slider = Slider(screen, 10, 40, 100, 10, min=0.1, max=10, step=0.1, color=(255, 255, 255), initial=beta)
beta_output = TextBox(screen, 160, 39, 25, 12, fontSize=14,borderThickness=0)
beta_box = TextBox(screen, 120, 39, 34, 12, fontSize=14,borderThickness=0, textColour=(0, 0, 0))
beta_box.setText("beta")

# Main loop
screen.fill(screen_color)
running = True
i = 0
while running:
    # Event handling
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
                pygame.quit()
                quit()

            # movement with wasd
            if event.key == pygame.K_w:
                yaw_pitch_roll[0] = (yaw_pitch_roll[0] - view_speed)% (2*np.pi)
            if event.key == pygame.K_s:
                yaw_pitch_roll[0] = (yaw_pitch_roll[0] + view_speed)% (2*np.pi)
            if event.key == pygame.K_a:
                yaw_pitch_roll[1] = (yaw_pitch_roll[1] - view_speed)% (2*np.pi)
            if event.key == pygame.K_d:
                yaw_pitch_roll[1] = (yaw_pitch_roll[1] + view_speed)% (2*np.pi)
            if event.key == pygame.K_q:
                yaw_pitch_roll[2] = (yaw_pitch_roll[2] - view_speed)% (2*np.pi)
            if event.key == pygame.K_e:
                yaw_pitch_roll[2] = (yaw_pitch_roll[2] + view_speed)% (2*np.pi)
            recalculate_and_redraw()


        if event.type == pygame.QUIT:
            running = False

        

    sigma_new = sigma_slider.getValue()
    rho_new = rho_slider.getValue()
    beta_new = beta_slider.getValue()
    if sigma_new != sigma or rho_new != rho or beta_new != beta:
        sigma = sigma_new
        rho = rho_new
        beta = beta_new
        recalculate_and_redraw()
        sigma_output.setText(sigma)
        beta_output.setText(beta)
        rho_output.setText(rho)
        # pygame_widgets callback functionality wansn't working  

    pygame_widgets.update(events)
    pygame.display.flip()
    clock.tick(fps)