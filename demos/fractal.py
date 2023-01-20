# https://imagemagick.org/index.php
# convert -delay 200 -size 800x800 -loop 0 snow_*png snow.gif
import pygame
from time import sleep
from math import pi, sqrt, sin, cos

pygame.init()
w = 1000
maxiter = 7
# origin in the middle
h = w // 2
thickness = 20
window = pygame.display.set_mode( [ w, w ] )

# connect a sequence of points into a sequence of line segments
def segment(points):
    lines = []
    first = points.pop(0)
    while len(points) > 0:
        second = points.pop(0)
        lines.append((first, second))
        first = second
    return lines

# snowflake split: --- -> -^- 
def split(line):
    (sl, el) = line
    (xs, ys) = sl
    (xe, ye) = el
    dx = xs - xe
    dy = ys - ye
    dist =  sqrt(dx**2 + dy**2)
    points = [ sl ]
    slope = dy / dx
    # 1 one third, 2 mid, 3 two thirds
    for t in ((1 / 3, 1 / 2, 2 / 3)):
        nx = (1 - t) * xs + t * xe
        ny = (1 - t) * ys + t * ye
        points.append((nx, ny))
    points.append(el)        
    push = (dist / 3) * (sqrt(3) / 2)
    (xm, ym) = points[2]
    (xs, ys) = (xm + dy, ym - dx)
    t = push / dist
    px = (1 - t) * xm + t * xs
    py = (1 - t) * ym + t * ys
    points[2] = (px, py)
    return segment(points)

# origin in the middle, unit square
def translate(p, h):
    (x, y) = p
    # (0, 0) top left w x w
    y *= -1
    x *= h
    y *= h
    y += h
    x += h
    return (round(x), round(y))

# draw a unit-lenght line in the middle of the screen
lines = [ ]

a = pi / 2
i = 2 * pi / 3
r = 1 / sqrt(3)
# starting triangle
points = [ ( r * cos(p * i + a), r * sin(p * i + a)) for p in range(3) ]
points = [ translate(p, h) for p in points ]
points.append(points[0]) # close the triangle
lines = segment(points)

for i in range(maxiter):
    newlines = []
    window.fill((0, 0, 0))
    for line in lines:
        (spos, epos) = line
        pygame.draw.line(window,
                         '#ffffff',
                         spos, epos,
                         width = thickness)
        newlines += split(line)
    lines = newlines
    thickness = max(thickness // 2, 1)
    pygame.display.flip()
    print(f'Iteration {i}')
    pygame.image.save(window, f'snow_{i}.png')
    sleep(1)
ignore = input('Enter to close')

pygame.quit()
