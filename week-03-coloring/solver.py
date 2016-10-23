#!/usr/bin/python3
# -*- coding: utf-8 -*-

import networkx as nx
import numpy as np
import cvxopt
import cvxopt.glpk
cvxopt.glpk.options['msg_lev'] = 'GLP_MSG_OFF'
cvxopt.glpk.options['tm_lim'] = 100 * 10 ** 3 #ms
#cvxopt.glpk.options['mip_gap'] = 0.25 #%

# python2.x only
#import constraint as cstrt

def solve_it(input_data):
    # Modify this code to run your optimization algorithm

    # parse the input
    lines = input_data.split('\n')

    first_line = lines[0].split()
    node_count = int(first_line[0])
    edge_count = int(first_line[1])

    edges = []
    for i in range(1, edge_count + 1):
        line = lines[i]
        parts = line.split()
        edges.append((int(parts[0]), int(parts[1])))

    # build a trivial solution
    # every node has its own color
    # ==========
    #solution = range(0, node_count)

    # greedy solution
    # n < 100 --> largest first greedy
    # n >= 100 --> independent set greedy
    # ==========
    if node_count < 100:
        solution = greedy(node_count, 
                          edges, 
                          strategy = nx.coloring.strategy_largest_first)
    else:
        solution = greedy(node_count, 
                          edges, 
                          strategy = nx.coloring.strategy_independent_set)

    # MIP solution
    # slow but optimal
    # not practical for graphs with order bigger than 20
    # ==========
    #print("V =", node_count)
    #print("E =", len(edges))
    #solution = mip(node_count, edges)

    # constraint programming solution
    # using module "python-constraint"
    # only work with python2
    # ==========
    #solution = pycst(node_count, edges)

    # prepare the solution in the specified output format
    output_data = str(node_count) + ' ' + str(0) + '\n'
    output_data += ' '.join(map(str, solution))

    return output_data

def pycst(node_count, edges):
    minColor = cstrt.Problem()
    for node in range(node_count):
        minColor.addVariable(node, range(node_count))
    for edge in edges:
        minColor.addConstraint(lambda a, b: a != b, (edge[0], edge[1]))
    soln = minColor.getSolutions()[0]
    return [soln[node] for node in range(node_count)]

def mip(node_count, edges):
    # objective
    color_count = node_count
    edge_count = len(edges)
    c = np.ones(color_count)
    for i in range(color_count):
        c = np.hstack([c, np.zeros(node_count)])

    # equality constraints
    xA = []
    yA = []
    valA = []
    for i in range(node_count):
        for j in range(color_count):
            xA.append(i)
            yA.append(color_count + node_count * j + i)
            valA.append(1)

    b = np.ones(node_count)

    # inequality constraints
    xG = []
    yG = []
    valG = []

    ## x_ik - y_k <= 0
    xPos = 0
    for i in range(node_count):
        for j in range(color_count):
            xG.append(i * color_count + j)
            yG.append(j)
            valG.append(-1)
            xG.append(i * color_count + j)
            yG.append(color_count + j * node_count + i)
            valG.append(1)

    ## x_ik + x_jk <= 1
    xPos += node_count * color_count
    for i, edge in enumerate(edges):
        for j in range(color_count):
            xG.append(xPos + i * color_count + j)
            yG.append(color_count + j * node_count + edge[0])
            valG.append(1)
            xG.append(xPos + i * color_count + j)
            yG.append(color_count + j * node_count + edge[1])
            valG.append(1)

    ## y_(i + 1) - y_i <= 0
    xPos += edge_count * color_count
    for j in range(color_count - 1):
        xG.append(xPos + j)
        yG.append(j)
        valG.append(-1)
        xG.append(xPos + j)
        yG.append(j + 1)
        valG.append(1)

    #G = np.empty(shape = (0, color_count * (node_count + 1)))
    #for i in range(node_count):
    #    for j in range(color_count):
    #        gRow = np.zeros(color_count * (node_count + 1))
    #        gRow[j] = -1
    #        gRow[color_count + j * node_count + i] = 1
    #        G = np.vstack([G, gRow])

    #for edge in edges:
    #    for j in range(color_count):
    #        gRow = np.zeros(color_count * (node_count + 1))
    #        gRow[color_count + j * node_count + edge[0]] = 1
    #        gRow[color_count + j * node_count + edge[1]] = 1
    #        G = np.vstack([G, gRow])

    #for i in range(color_count - 1):
    #    gRow = np.zeros(color_count * (node_count + 1))
    #    gRow[i] = -1
    #    gRow[i + 1] = 1
    #    G = np.vstack([G, gRow])
    
    h = np.hstack([np.zeros(node_count * color_count), 
                   np.ones(len(edges) * color_count),
                   np.zeros(color_count - 1)])

    binVars=set()
    for var in range(color_count * (node_count + 1)):
        binVars.add(var)

    status, isol = cvxopt.glpk.ilp(c = cvxopt.matrix(c),
                                   G = cvxopt.spmatrix(valG, xG, yG),
                                   h = cvxopt.matrix(h),
                                   A = cvxopt.spmatrix(valA, xA, yA),
                                   b = cvxopt.matrix(b),
                                   I = binVars,
                                   B = binVars)
    soln = []
    for i in range(node_count):
        for j in range(color_count):
            if isol[color_count + node_count * j + i] == 1:
                soln.append(j)
                break
    return soln

def greedy(node_count, edges, strategy):
    G = nx.Graph()
    G.add_nodes_from(range(node_count))
    G.add_edges_from(edges)
    coloring = nx.coloring.greedy_color(G = G, strategy = strategy)
    return(list(coloring.values()))

import sys

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
        print(solve_it(input_data))
    else:
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/gc_4_1)')

