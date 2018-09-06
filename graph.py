""" graph representation functions

    (c) Volker Poplawski 2018
"""
import quadtree
import math
from mapgen import IMPASSABLE, PASSABLE


def euclidian(start, end):
    dx, dy = start.center()[0] - end.center()[0], start.center()[1] - end.center()[1]
    return math.sqrt(dx**2 + dy**2)


def manhatten(start, end):
    dx, dy = start.center()[0] - end.center()[0], start.center()[1] - end.center()[1]
    return dx + dy


def neighbours(qt, tile):
    """
    Return neighbour tiles for tile in quadtree.
    
    There are more efficient ways to find neighbouring tiles in a quadtree!
    Here we simply intersect the whole quadtree with a slightly expanded bounding box
    of the query tile.
    """
    neigh = []
    qt.intersect(quadtree.BoundingBox(tile.bb.x - 1, tile.bb.y -1, tile.bb.w + 2, tile.bb.h + 2), neigh)
    return neigh



def make_adjacent_function(quadtree):
    """
    Return function suitable as adjacent function as parameter for call to A*
    
    this wrapper function captures the quadtree in a closure of the adjacent function
    """
    def adjacent(tile):
        a = []
        for neighbour in neighbours(quadtree, tile):
            assert neighbour.childs is None        # must be leaf node
            if neighbour.color != IMPASSABLE:
                a.append(neighbour)

        return a

    return adjacent


