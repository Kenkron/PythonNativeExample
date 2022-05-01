import sys
print(sys.path)
import min_span
import pyglet
import random
import time

window = pyglet.window.Window(1600,900)

label = pyglet.text.Label(
    "Press ENTER for C, or any other key for Python",
    font_name='Times New Roman',
    font_size=16,
    x=0, y=0,
    anchor_x='left', anchor_y='bottom')

points = []
edges = []
salesman_path = []
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
    for i in range(len(salesman_path)):
        s = salesman_path[i - 1]
        e = salesman_path[i]
        pyglet.shapes.Line(
            s[0], s[1],
            e[0], e[1],
            width=2, color=(0,255,0)).draw()
        
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
    global salesman_path
    label_text = ""
    start = time.time()
    if native:
        label_text = "C: "
        edge_color = (0, 0, 255)
        edges = min_span.min_span_c(points)
    else:
        label_text = "Python: "
        edge_color = (255, 0, 0)
        edges = min_span.min_span_py(points)
    label_text += str(time.time() - start) + " seconds"
    label.text = label_text
    salesman_path = min_span.travelling_salesman_from_edges(points, edges)

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
    global salesman_path
    label.text = "Computing..."
    native = (symbol == pyglet.window.key.ENTER)

    # This makes pyglet call run_min_span after it
    # updates the label to say "Computing..."
    def callback(dt):
        run_min_span(native)
    pyglet.clock.schedule_once(callback, 0.001)

pyglet.app.run()
