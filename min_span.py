#!/usr/bin/env python3
"""
A test of python native integration.

The spanning tree function should be an O(n^3)
operation, but converting the data to/from a ctype
should be O(1) Thus, there should be a performance
benefit to running a minimum spanning tree in C.
"""

import math

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
    min_span_lib = ctypes.CDLL('./native_min_span.so')
if platform.system() == "Windows":
    min_span_lib = ctypes.CDLL('./native_min_span.dll')
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

def get_direction(a, b):
    """
    Gets a unit vector pointing from b to a
    """
    difference = (a[0] - b[0], a[1] - b[1])
    length = (difference[0]**2 + difference[1]**2)**0.5
    return (difference[0]/length, difference[1]/length)

def dot(a, b):
    return a[0] * b[0] + a[1] * b[1]

def cross(a, b):
    return a[0] * b[1] - b[0] * a[1]

def angle(a, b):
    """
    returns the angle between two unit vectors
    """
    angle = math.atan2(cross(a, b), dot(a, b)) + math.pi
    if math.pi * 2 - angle < 0.0000001:
        return 0
    return angle

def remove_duplicates(points):
    """
    Returns a new list of points from the input parameter,
    but without duplicates. The input is not mutated.
    Order is preserved, with only the first of a duplicate
    kept.
    """
    new_points = []
    added = set()
    for p in points:
        if p not in added:
            added.add(p)
            new_points.append(p)
    return new_points

def travelling_salesman_from_edges(points, min_span_edges):
    """
    Provides an approximation of the travelling salesman problem
    based on the minimum spanning tree. This is guaranteed to be
    no more than twice the length of the actual solution.
    """
    # graph maps points to a list of adjacent points
    graph = {}
    for e in min_span_edges:
        if e[0] not in graph:
            graph[e[0]] = []
        graph[e[0]].append(e[1])
        if e[1] not in graph:
            graph[e[1]] = []
        graph[e[1]].append(e[0])

    # Start with a single segment of the tree
    start = 0
    while len(graph[start]) > 1:
        start += 1;
    
    path = [start]
    # Set will have fast lookups
    added = {points[start]}
    # Start walking at any adjacent point
    previous = start
    walker = graph[previous][0]
    # The walker will always follow the left-most path
    while len(path) < len(points):
        backwards = get_direction(points[walker], points[previous])
        next_step = graph[walker][0]
        for adjacent in graph[walker]:
            forwards = get_direction(points[adjacent], points[walker])
            to_next_step = get_direction(points[next_step], points[walker])
            
            if angle(backwards, forwards) > angle(backwards, to_next_step):
                next_step = adjacent
        if points[walker] not in added:
            path.append(walker)
            added.add(points[walker])
        previous = walker
        walker = next_step
    
    path_points = [points[p] for p in path]
    clean_path(path_points)
    return path_points

def segments_intersect(a, b, c, d):
    """
    Returns True iff line segments ab and cd intersect
    """
    p = a
    r = (b[0] - a[0], b[1] - a[1])
    q = c
    s = (d[0] - c[0], d[1] - c[1])
    q_p = (q[0] - p[0], q[1] - p[1])
    rxs = cross(r, s)
    if rxs == 0:
        if cross(q_p, r) == 0:
            # Points are colinear. Do a bb check
            return (
                min(a[0], b[0]) <= max(c[0], d[0]) and
                min(c[0], d[0]) <= max(a[0], b[0]) and
                min(a[1], b[1]) <= max(c[1], d[1]) and
                min(c[1], d[1]) <= max(a[1], b[1]))
        else:
            # Points are parallel
            return False
    t = cross(q_p, s) / rxs
    u = cross(q_p, r) / rxs
    return (
        0 <= t and
        t <= 1 and
        0 <= u and
        u <= 1)

def clean_path(points):
    """
    Removes crossing segments of a path.
    This mutates the input, and also returns it
    for chaining.

    It works by switching the second point of the 
    first segment with the first point of the second
    segment, repeating until there are no more overlaps.

    If the path cannot be cleaned in len(points) iterations,
    processing is halted.
    """
    cleared = False
    i = 0
    while not cleared and i < len(points):
        i += 1
        cleared = True
        for i in range(1, len(points)):
            for j in range(i + 2, len(points)):
                a = points[i]
                b = points[(i + 1) % len(points)]
                c = points[j]
                d = points[(j + 1) % len(points)]
                if segments_intersect(a, b, c, d):
                    tmp = points[i]
                    points[(i + 1) % len(points)] = c
                    points[j] = b
                    cleared = False
    return points
