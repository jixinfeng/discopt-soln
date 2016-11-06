#!/usr/bin/python3
# -*- coding: utf-8 -*-

import math
from collections import namedtuple
import itertools
import numpy as np
import networkx as nx
#import cvxopt
#import cvxopt.glpk
#cvxopt.glpk.options['msg_lev'] = 'GLP_MSG_OFF'

Point = namedtuple("Point", ['x', 'y'])

def length(point1, point2):
    return math.sqrt((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2)

def tspLength(cycle, points):
    return sum([length(points[cycle[i - 1]], points[cycle[i]]) 
                for i in range(len(points))])

def edgeLengths(points):
    dists = np.zeros([len(points), len(points)])
    for i, p in enumerate(points):
        for j, q in enumerate(points):
            if i == j:
                continue
            elif i < j:
                dists[i][j] = length(p, q)
            else:
                dists[i][j] = dists[j][i]
    return dists

def solve_it(input_data):
    # Modify this code to run your optimization algorithm

    # parse the input
    lines = input_data.split('\n')

    nodeCount = int(lines[0])

    points = []
    for i in range(1, nodeCount+1):
        line = lines[i]
        parts = line.split()
        points.append(Point(float(parts[0]), float(parts[1])))

    # build a trivial solution
    # visit the nodes in the order they appear in the file
    # ==========
    #solution = range(0, nodeCount)

    # naive solution
    # by applying brute force
    # prohibitively slow but optimal O(n!)
    # ==========
    #solution = naive(nodeCount, points)

    # greedy solution
    # ==========
    #solution = greedy(nodeCount, points)
    solution = dp(nodeCount, points)

    # MIP solution
    # slow but optimal
    # ==========
    #solution = mip(nodeCount, points)

    # calculate the length of the tour
    obj = tspLength(solution, points)

    # prepare the solution in the specified output format
    output_data = '%.2f' % obj + ' ' + str(0) + '\n'
    output_data += ' '.join(map(str, solution))

    return output_data

def mip(nodeCount, points):

    soln = []
    return soln

def greedy(nodeCount, points):
    kGraph = nx.Graph()
    for u in range(nodeCount):
        for v in range(u + 1, nodeCount):
            
            kGraph.add_edge(u, v, 
                            weight = length(points[u], points[v]))

    mst = nx.minimum_spanning_tree(kGraph)

#    for step in range(nodeCount - 1):
#        nextSteps = np.argsort(dists[soln[-1]])
#        soln.append([node for node in nextSteps if node not in set(soln)][0])
    return list(nx.dfs_preorder_nodes(mst))

def dp(nodeCount, points):
    dists = edgeLengths(points)
    return held_karp(dists)[1]

def held_karp(dists):
    """
    Implementation of Held-Karp, an algorithm that solves the Traveling
    Salesman Problem using dynamic programming with memoization.
    Parameters:
        dists: distance matrix
    Returns:
        A tuple, (cost, path).
    """
    n = len(dists)

    # Maps each subset of the nodes to the cost to reach that subset, as well
    # as what node it passed before reaching this subset.
    # Node subsets are represented as set bits.
    C = {}

    # Set transition cost from initial state
    for k in range(1, n):
        C[(1 << k, k)] = (dists[0][k], 0)

    # Iterate subsets of increasing length and store intermediate results
    # in classic dynamic programming manner
    for subset_size in range(2, n):
        for subset in itertools.combinations(range(1, n), subset_size):
            # Set bits for all nodes in this subset
            bits = 0
            for bit in subset:
                bits |= 1 << bit

            # Find the lowest cost to get to this subset
            for k in subset:
                prev = bits & ~(1 << k)

                res = []
                for m in subset:
                    if m == 0 or m == k:
                        continue
                    res.append((C[(prev, m)][0] + dists[m][k], m))
                C[(bits, k)] = min(res)

    # We're interested in all bits but the least significant (the start state)
    bits = (2**n - 1) - 1

    # Calculate optimal cost
    res = []
    for k in range(1, n):
        res.append((C[(bits, k)][0] + dists[k][0], k))
    opt, parent = min(res)

    # Backtrack to find full path
    path = []
    for i in range(n - 1):
        path.append(parent)
        new_bits = bits & ~(1 << parent)
        _, parent = C[(bits, parent)]
        bits = new_bits

    # Add implicit start state
    path.append(0)

    return opt, list(reversed(path))

def naive(nodeCount, points):
    minDist = 2 ** 32
    bestCycle = list(range(nodeCount))
    for cycle in itertools.permutations(range(nodeCount)):
        travelDist = tspLength(cycle, points)
        if travelDist < minDist:
            minDist = travelDist
            bestCycle = cycle
    return bestCycle

import sys

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
        print(solve_it(input_data))
    else:
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/tsp_51_1)')

