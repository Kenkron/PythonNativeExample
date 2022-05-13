Python Native Example
=====================

Demonstration of running C code from Python

The program 'min_span.py' creates a set of 200 random points. When you press return, python will run the minimum spanning tree code written in min_span.c, and compiled into min_span.dll. The tree will appear blue. Alternatively, if any other key is pressed, the minimum spanning tree will be computed in pure python, and the result will appear red. The time taken for each operation will appear red.

The implementations function the same way (inefficiently), but the performance difference is incredible. On my computer, the c implementation takes 0.03 seconds, while the python implementation takes around 5.5 seconds. Pypy takes around 0.06 seconds, which is considerably faster than the default CPython, though this is still around half the speed of the c implementation. These tests demonstrate the drastic performance increase that native implementation provides for expensive functions. However, it should be noted that most python libraries (eg. numpy) use a native backend already. Native code written to replace these functions are unlikely to be any faster than the functions already are.

Controls
--------

* To add points, left click
* To remove points, right click
* To change initial points, run with the desired number of points as an argument (eg. `python min-span.py 1000`)

It's possible that the python implementation could
be improved, but even if it could, the C
implementation didn't have to be improved.

Dependencies
------------

* pyglet (for rendering)

`python -m pip install pyglet`

Compiling the C code
--------------------

### Windows

1. Open a Developer Command Prompt (this comes with Visual Studios)
2. Navigate to the directory with *native_min_span.c*
3. Run `cl /LD native_min_span.c` to compile the code into *native_min_span.dll*

### Linux

```
gcc -c -fPIC -O3 native_min_span.c -o native_min_span.o
gcc native_min_span.o -shared -o native_min_span.so
```

Running the code
----------------

`python visualization.py`
