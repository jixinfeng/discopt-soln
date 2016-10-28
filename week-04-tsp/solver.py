#!/usr/bin/python3
# -*- coding: utf-8 -*-

import math
from collections import namedtuple
import itertools
import numpy as np
import cvxopt
import cvxopt.glpk
cvxopt.glpk.options['msg_lev'] = 'GLP_MSG_OFF'

Point = namedtuple("Point", ['x', 'y'])

def length(point1, point2):
    return math.sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2)

def cycleLength(cycle, points):
    return sum([length(points[cycle[i - 1]], points[cycle[i]]) 
                for i in range(len(points))])

def pairLengths(points):
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
    solution = greedy(nodeCount, points)

    # MIP solution
    # slow but optimal
    # ==========
    #solution = mip(nodeCount, points)

    # calculate the length of the tour
    obj = cycleLength(solution, points)

    # prepare the solution in the specified output format
    output_data = '%.2f' % obj + ' ' + str(0) + '\n'
    output_data += ' '.join(map(str, solution))

    return output_data

def mip(nodeCount, points):

    soln = []
    return soln

def greedy(nodeCount, points):
    soln = [0]
    dists = pairLengths(points)
    for step in range(nodeCount - 1):
        nextSteps = np.argsort(dists[soln[-1]])
        soln.append([node for node in nextSteps if node not in set(soln)][0])
    return soln

def naive(nodeCount, points):
    minDist = 2 ** 32
    bestCycle = list(range(nodeCount))
    for cycle in itertools.permutations(range(nodeCount)):
        travelDist = cycleLength(cycle, points)
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

