# Simple Lorentz attractor
# Arthur Lovekin
# https://github.com/Josephbakulikira/Lorenz-attractor-3D---pygame/blob/master/main.py
import pygame
import numpy as np

width = 800
height = 600
size = (width, height)
pygame.init()
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Lorentz attractor")
clock = pygame.time.Clock()

# Parameters
sigma = 10
rho = 28
beta = 8/3

# Initial conditions
max_length = 10000 # maximum length of the tail
points = np.ones((max_length, 3)) * np.nan # holds all the points of the tail
points[0] = np.array([0.1, 0, 0]) # initial point
dt = 0.01

# Drawing parameters
scale = 10 # scaling the size of the attractor
hue_shift = 240 # degrees to shift the hue (0 is red, 120 is green, 240 is blue)
tail_decay = 4 # how fast the tail fades (higher is faster, should be >1)
# pen_color = (255, 0, 0) # red
screen_color = (0, 0, 0)   #black
fps = 60
pen_size = 1
rotation_speed = 0.01
change_yaw_pitch_roll = np.array([0.0, 0.01, 0.0]) # change how fast the view rotates (higher = faster)

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



# Main loop
screen.fill(screen_color)
running = True
i = 0
yaw_pitch_roll = np.array([0.0, 0.0, 0.0])
max_line_length = 5.5
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                running = False
        if event.type == pygame.QUIT:
            running = False

    # Lorenz attractor
    x, y, z = points[i]
    dx = sigma*(y-x)
    dy = x*(rho-z)-y
    dz = x*y-beta*z
    points[(i+1)%max_length] = points[i] + dt*np.array([dx, dy, dz])
    i = (i+1) % max_length

    # rotate the points for viewing, and project to 2D
    points_rotated = rotate(points, yaw_pitch_roll)[:, :2]
    yaw_pitch_roll = (yaw_pitch_roll + change_yaw_pitch_roll) % (2*np.pi)

    # Draw
    screen.fill(screen_color)
    
    for j in range(max_length):
        x, y = points_rotated[j]
        if np.isnan(x) or np.isnan(y):
            continue

        # end of the matrix, need to connect to the beginning
        if j == max_length-1:
            x_next, y_next = points_rotated[0]
        else:
            x_next, y_next = points_rotated[j+1]
        if np.isnan(x_next) or np.isnan(y_next):
            continue
        
        # actual end of tail
        if i==j:
            continue

        # let color be a function of line length (how fast the point is moving)
        line_length = np.linalg.norm(points_rotated[j] - points_rotated[(j+1)%max_length])
        if line_length > max_line_length:
            max_line_length = line_length
            # print(max_line_length)
        hue = int((360*line_length/max_line_length + hue_shift)%360)
        
        # # let the value be a function of the index (how old the point is)
        # # transparency on black background is the same as value       
        age = (j-i)/max_length if j>i else (max_length - (i-j))/max_length
        # value = int(100*age) # linear
        # value = int(100 * (tail_decay**age -1) / (tail_decay - 1)) # exponential f(age) = c1*age^a + c2
        value = int(100*np.exp(1-(1/age**tail_decay)))

        color = pygame.Color(0)
        color.hsva = (hue, 100, value, 100)

        pygame.draw.line(screen, color, (int(width/2+scale*x), int(height/2+scale*y)), (int(width/2+scale*x_next), int(height/2+scale*y_next)), width=pen_size)
        

    pygame.display.flip()
    clock.tick(fps)