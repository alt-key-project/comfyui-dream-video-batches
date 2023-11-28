# -*- coding: utf-8 -*-
from __future__ import division

import math
from functools import cache


class Vector2d:
    def __init__(self, x, y=0.0):
        if isinstance(x, tuple):
            self.x = x[0]
            self.y = x[1]
        else:
            self.x = x
            self.y = y

    def tuple(self):
        return (self.x, self.y)

    def __getitem__(self, item):
        if item == 0:
            return self.x
        elif item == 1:
            return self.y
        else:
            raise Exception("Bad index - {}!".format(item))

    def align(self, other):
        x = self.x
        y = self.y
        if self.x > 0 and other.x < 0:
            x = -self.x
        if self.y > 0 and other.y < 0:
            y = -self.y
        if self.x < 0 and other.x > 0:
            x = -self.x
        if self.y < 0 and other.y > 0:
            y = -self.y
        return Vector2d(x, y)

    def normalized(self):
        return self.multiply(1.0 / self.length())

    def neg(self):
        return Vector2d(-self.x, -self.y)

    def multiply(self, v):
        return Vector2d(self.x * v, self.y * v)

    def length(self):
        return math.sqrt(self.x * self.x + self.y * self.y)

    def add(self, vector):
        return Vector2d(self.x + vector.x, self.y + vector.y)

    def sub(self, vector):
        return Vector2d(self.x - vector.x, self.y - vector.y)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "{:.3f},{:.3f}".format(self.x, self.y)


def _intersect_lines(pt1, pt2, ptA, ptB):
    DET_TOLERANCE = 0.00000001
    x1, y1 = pt1
    x2, y2 = pt2
    dx1 = x2 - x1
    dy1 = y2 - y1
    x, y = ptA
    xB, yB = ptB
    dx = xB - x
    dy = yB - y
    DET = (-dx1 * dy + dy1 * dx)
    if math.fabs(DET) < DET_TOLERANCE: return None
    DETinv = 1.0 / DET
    r = DETinv * (-dy * (x - x1) + dx * (y - y1))
    s = DETinv * (-dy1 * (x - x1) + dx1 * (y - y1))
    xi = (x1 + r * dx1 + x + s * dx) / 2.0
    yi = (y1 + r * dy1 + y + s * dy) / 2.0
    return xi, yi


class Quad2d:
    def __init__(self, x1, y1, x2, y2):
        self.mincorner = Vector2d(min(x1, x2), min(y1, y2))
        self.maxcorner = Vector2d(max(x1, x2), max(y1, y2))
        self._default_forgiveness = self.maxcorner.sub(self.mincorner).length() * 0.00001

    @property
    def diagonal_length(self):
        return self.maxcorner.sub(self.mincorner).length()

    def add(self, v: Vector2d):
        a = self.mincorner.add(v)
        b = self.maxcorner.add(v)
        return Quad2d(a.x, a.y, b.x, b.y)

    @property
    def corners(self):
        return (self.mincorner, Vector2d(self.mincorner.x, self.maxcorner.y),
                self.maxcorner, Vector2d(self.maxcorner.x, self.mincorner.y))

    @property
    def center(self):
        return self.maxcorner.add(self.mincorner).multiply(0.5)

    def contains_vector(self, v: Vector2d, forgiveness: float = None):
        if forgiveness is None:
            forgiveness = self._default_forgiveness
        b = (self.mincorner.x - forgiveness) <= v.x <= (self.maxcorner.x + forgiveness) and \
            (self.mincorner.y - forgiveness) <= v.y <= (self.maxcorner.y + forgiveness)
        return b

    def calculate_intersections(self, pos: Vector2d, direction: Vector2d):
        (a, b, c, d) = self.corners

        p1 = pos.add(direction.normalized().multiply(self.diagonal_length))
        p2 = pos.sub(direction.normalized().multiply(self.diagonal_length))

        i1 = _intersect_lines(p1.tuple(), p2.tuple(), a.tuple(), b.tuple())
        i2 = _intersect_lines(p1.tuple(), p2.tuple(), b.tuple(), c.tuple())
        i3 = _intersect_lines(p1.tuple(), p2.tuple(), c.tuple(), d.tuple())
        i4 = _intersect_lines(p1.tuple(), p2.tuple(), d.tuple(), a.tuple())
        results = list()
        if (i1 is not None) and self.contains_vector(Vector2d(i1)):
            results.append(Vector2d(i1))
        if (i2 is not None) and self.contains_vector(Vector2d(i2)):
            results.append(Vector2d(i2))
        if (i3 is not None) and self.contains_vector(Vector2d(i3)):
            results.append(Vector2d(i3))
        if (i4 is not None) and self.contains_vector(Vector2d(i4)):
            results.append(Vector2d(i4))
        a = results[0]
        if a.sub(results[1]).length() > self._default_forgiveness:
            return a, results[1]
        else:
            return a, results[2]

    def __str__(self):
        return "({} - {})".format(self.mincorner, self.maxcorner)
