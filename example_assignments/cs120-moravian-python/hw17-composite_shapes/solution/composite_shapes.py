# In class we wrote a function to draw a house given certain parameters. To
# draw the house we drew lines using the draw_line() function, so we say that a
# house is *composed* of lines.
#
# I wanted to write a draw_circle() function in class as well but we ran out of
# time. I have included draw_circle() below which you may use.
#
# Write your own functions to draw composite shapes. You may write as many
# functions as you want, but the minimum requirement is that you have at least
# one top-level shape that is composed of at least 2 other types of
# shapes. Your top-level shape must also take parameters that determine where
# to draw the shape, and your program should draw at least 2 of your top-level
# shape in different positions.
#
# For example, you may write a function called draw_eye() which draws a circle
# with another circle inside of it, representing an eye. This alone is not
# enough because it is only composed of circles. You could then write a
# function called draw_mouth() which draws a crude mouth with lines. Then you
# could write a function called draw_face() that draws a face using one big
# circle, two eyes using draw_eye(), and a mouth using draw_mouth(). You should
# then be able to call draw_face() twice with two different positions and draw
# two faces side-by-side.
#
# If you want to draw something elaborate, feel free, but the point of the
# assignment is to write functions to break down a problem, not to draw an
# amazing drawing.


import turtle


# Purpose - draw a line
# Parameters:
#    x1 - starting x coordinate (float)
#    y1 - starting y coordinate (float)
#    x2 - ending x coordinate (float)
#    y2 - ending y coordinate (float)
#    t - the turtle that does the drawing (Turtle)
# Return value:
#    None
def draw_line(x1, y1, x2, y2, t):
    t.penup()
    t.goto(x1, y1)
    t.pendown()
    t.goto(x2, y2)


# Purpose - draw a circle
# Parameters:
#    center_x - x coordinate of the center of the circle (float)
#    center_y - y coordinate of the center of the circle (float)
#    radius - radius of the circle (float)
#    t - the turtle that does the drawing (Turtle)
# Return value:
#    None
def draw_circle(center_x, center_y, radius, t):
    t.penup()
    t.goto(center_x, center_y - radius)
    t.setheading(0)
    t.pendown()
    t.circle(radius)


def draw_eye(x, y, width, t):
    draw_circle(x, y, width / 2, t)
    draw_circle(x, y, width, t)


def draw_mouth(x, y, width, t):
    draw_line(x - width / 2, y, x + width / 2, y, t)


def draw_face(x, y, width):
    t = turtle.Turtle()
    t.speed(0)
    draw_circle(x, y, width / 2, t)
    draw_eye(x - width / 6, y + width / 6, width / 6, t)
    draw_eye(x + width / 6, y + width / 6, width / 6, t)
    draw_mouth(x, y - width / 6, width / 3, t)


draw_face(200, 0, 200)
draw_face(-200, 0, 200)

turtle.exitonclick()
