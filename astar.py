""" generic implementation of A* path finding algorithm

    (c) Volker Poplawski 2018
"""
# priority queue dictionary
from pqdict import pqdict


def astar(adjafunc, distfunc, heurfunc, start, goal):
    """ adjafunc: node -> List(nodes)
        distfunc: node, node -> double
        start: start node
        goal: end node. Terminate when reached. 

        Return dict node -> absolute dist from start, dict node -> path predessor node
    """
    D = {start: 0}                   # final absolute distances
    P = {}                           # predecessors
    Q = pqdict({start: 0})           # fringe/frontier maps unexpanded node to estimated dist to goal

    considered = 0           # count how many nodes have been considered on multiple paths

    # keep expanding nodes from the fringe
    # until goal node is reached
    # or no more new nodes can be reached and fringe runs empty
    
    for n, estimation in Q.popitems():   # pop node with min estimated costs from queue
        if n == goal:                    # reached goal node
            break                        # stop expanding nodes

        for neighb in adjafunc(n):      # for all neighbours/adjacent of current node n
            considered += 1
            dist = D[n] + distfunc(n, neighb)        # calculate distance to neighbour: cost to current + cost reaching neighbour from current
            if neighb not in D or D[neighb] > dist:  # if neighbour never visited or shorter using this way
                D[neighb] = dist                     # found (shorter) distance to neighbour
                Q[neighb] = dist + heurfunc(neighb, goal)   # estimate distance from neighbour to goal
                P[neighb] = n                        # remember we reached neighbour via n  

    # expanding done: distance map D populated

    if goal not in D:                # goal node not in distance map
        return None, D, considered   # no path to goal found

    # build path from start to goal
    # by walking backwards on the predecessor map

    path = []              # start with empty path
    n = goal               # at the goal node
    
    while n != start:      # while not yet at the start node
        path.insert(0, n)  #     prepend node to path
        n = P[n]           #     get predecessor of node
        
    path.insert(0, start)  # dont forget the start node

    return path, D, considered


