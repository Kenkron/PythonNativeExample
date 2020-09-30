#!/usr/bin/env python3

"""
A test of python native integration.

The spanning tree function should be an O(n^3)
operation, but converting the data to/from a ctype
should be O(1) Thus, there should be a performance
benefit to running a minimum spanning tree in C.
"""

def min_span_py(points):
    """
    Python implementation of minimum spanning tree

    Any points already connected together by edges
    are considered to be in the same "forest". At
    the start, since no points have been connected
    yet, each point is in its own "forest".

    The algorithm finds the two closest points in
    different "forests", connects them with an
    edge, and combines them into one forest. This
    is repeated until there is only one forest.

    This is a greedy algorithm. Because it always
    searches for the shortest useful edge, the end
    result will use the shortest edges possible.

    This algorithm is designed to mirror the C
    implementation in min_span.c.
    """
    edges = []
    edge_color = (255, 0, 0)
    groups = []

    for i in range(len(points)):
        groups.append(i)

    # There should be len(points) - 1 edges in a min spanning tree
    # If len(points) < 2, there cannot be any edges
    if len(points) < 2:
        return edges

    for e in range(len(points) - 1):
        min_edge_2 = -1
        min_edge_i = 0
        min_edge_j = 0
        for i in range(len(points)):
            for j in range(i, len(points)):
                # a^2 + b^2 = c^2
                dist2 =  (points[i][0] - points[j][0])**2
                dist2 += (points[i][1] - points[j][1])**2
                if (min_edge_2 == -1 or dist2 < min_edge_2) and groups[i] != groups[j]:
                    min_edge_2 = dist2
                    min_edge_i = i
                    min_edge_j = j
        edges.append((min_edge_i, min_edge_j))
        groupi = groups[min_edge_i]
        groupj = groups[min_edge_j]
        for i in range(len(groups)):
            if groups[i] == groupj:
                groups[i] = groupi
    return edges

import ctypes
import sys
import platform
min_span_lib = None
if platform.system() == "Linux":
    min_span_lib = ctypes.CDLL('./min_span.so')
if platform.system() == "Windows":
    min_span_lib = ctypes.CDLL('./min_span.dll')
min_span_lib.min_span.argtypes = (ctypes.c_int, ctypes.POINTER(ctypes.c_int))
min_span_lib.min_span.restype = ctypes.POINTER(ctypes.c_int)
min_span_lib.free_data.argtypes = [ctypes.c_void_p]
min_span_lib.free_data.restype = None

def min_span_c(points):
    """
    Calls a C implementation of minimum spanning tree

    This implementation is written in min_span.c,
    compiled to either a .dll (windows) or .so (linux),
    and called using the ctypes library.

    The c implementation of minimum spanning tree is
    designed to function the same way as the python
    implementation.
    """
    n_points = len(points)
    pointVals = []
    for p in points:
        pointVals.append(p[0])
        pointVals.append(p[1])

    array_type = ctypes.c_int * len(pointVals)

    output = min_span_lib.min_span(ctypes.c_int(n_points), array_type(*pointVals))

    edges = []
    for i in range(n_points - 1):
        edges.append((output[i * 2], output[i * 2 + 1]))

    free_pointer = ctypes.cast(output, ctypes.c_void_p)
    min_span_lib.free_data(free_pointer)
    return edges

import pyglet
import random
import time

window = pyglet.window.Window()

label = pyglet.text.Label(
    "Press ENTER for C, or any other key for Python",
    font_name='Times New Roman',
    font_size=16,
    x=0, y=0,
    anchor_x='left', anchor_y='bottom')

points = []
edges = []
BORDER = 4
POINT_RADIUS = 3

startingPoints = 200

if len(sys.argv) > 1:
    startingPoints = int(sys.argv[1])

for i in range(startingPoints):
    points.append((random.randrange(BORDER, window.width - BORDER), random.randrange(label.font_size + BORDER, window.height - BORDER)))

@window.event
def on_draw():
    window.clear()
    for p in points:
        pyglet.shapes.Circle(p[0], p[1], POINT_RADIUS, segments=8).draw()
    for e in edges:
        pyglet.shapes.Line(
            points[e[0]][0], points[e[0]][1],
            points[e[1]][0], points[e[1]][1],
            width=2, color=edge_color).draw()
    label.draw()


def run_min_span(native):
    """
    This is triggered by on_key_press, but separated
    into its own function so that the 'Computing...'
    message can be displayed.
    """
    global edges
    global edge_color
    global label
    label_text = ""
    start = time.time()
    if native:
        label_text = "C: "
        edge_color = (0, 0, 255)
        edges = min_span_c(points)
    else:
        label_text = "Python: "
        edge_color = (255, 0, 0)
        edges = min_span_py(points)
    label_text += str(time.time() - start) + " seconds"
    label.text = label_text

@window.event
def on_mouse_press(x, y, button, modifiers):
    if button == pyglet.window.mouse.RIGHT:
        global edges
        edges = []
        closest = -1
        closest_point = None
        for p in points:
            dist2 = (p[0] - x) ** 2 + (p[1] - y) ** 2
            if closest < 0 or dist2 < closest:
                closest_point = p
                closest = dist2
        if closest <= POINT_RADIUS**2:
            points.remove(closest_point)
    else:
        points.append((x, y))

@window.event
def on_key_press(symbol, modifiers):
    global label
    label.text = "Computing..."
    native = (symbol == pyglet.window.key.ENTER)

    # This makes pyglet call run_min_span after it
    # updates the label to say "Computing..."
    def callback(dt):
        run_min_span(native)
    pyglet.clock.schedule_once(callback, 0.001)

pyglet.app.run()
