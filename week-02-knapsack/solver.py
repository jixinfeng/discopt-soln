#!/usr/bin/python3
# -*- coding: utf-8 -*-

from collections import namedtuple
from operator import attrgetter

from gurobipy import *

# import numpy as np
# import cvxopt
# import cvxopt.glpk
# cvxopt.glpk.options['msg_lev'] = 'GLP_MSG_OFF'

Item = namedtuple("Item", ['index', 'value', 'weight', 'density'])

def solve_it(input_data):
    # Modify this code to run your optimization algorithm

    # parse the input
    lines = input_data.split('\n')

    firstLine = lines[0].split()
    item_count = int(firstLine[0])
    capacity = int(firstLine[1])

    items = []

    for i in range(1, item_count+1):
        line = lines[i]
        parts = line.split()
        v, w = int(parts[0]), int(parts[1])
        items.append(Item(i-1, v, w, 1.0 * v / w))

    value, taken = mip_gurobi(capacity, items)
    # value, taken = dp(capacity, items)
    # value, taken = mip_glpk(capacity, items)

    # prepare the solution in the specified output format
    output_data = str(value) + ' ' + str(0) + '\n' 
    output_data += ' '.join(map(str, taken))
    return output_data


def mip_gurobi(cap, items, verbose=False, num_threads=None):
    item_count = len(items)
    values = [item.value for item in items]
    weights = [item.weight for item in items]

    m = Model("knapsack")
    m.setParam('OutputFlag', verbose)
    if num_threads:
        m.setParam("Threads", num_threads)

    x = m.addVars(item_count, vtype=GRB.BINARY, name="items")
    m.setObjective(LinExpr(values, [x[i] for i in range(item_count)]), GRB.MAXIMIZE)
    m.addConstr(LinExpr(weights, [x[i] for i in range(item_count)]), GRB.LESS_EQUAL, cap, name="capacity")

    m.update()
    m.optimize()

    return int(m.objVal), [int(var.x) for var in m.getVars()]


# def mip_glpk(cap, items):
#     item_count = len(items)
#     values = np.zeros(item_count)
#     weights = np.zeros([1, item_count])
#
#     for i in range(item_count):
#         values[i] = items[i].value
#         weights[0][i] = items[i].weight
#
#     binVars=set()
#     for var in range(item_count):
#         binVars.add(var)
#
#     status, isol = cvxopt.glpk.ilp(c = cvxopt.matrix(-values, tc='d'),
#                                    G = cvxopt.matrix(weights, tc='d'),
#                                    h = cvxopt.matrix(cap, tc='d'),
#                                    I = binVars,
#                                    B = binVars)
#     taken = [int(val) for val in isol]
#     value = int(np.dot(values, np.array(taken)))
#     return value, taken


def dp(cap, items):
    n = len(items)
    taken = [0] * n
    values = [[0 for j in range(cap + 1)] for i in range(n + 1)]
    for i in range(n + 1):
        if i > 0:
            value = items[i - 1].value
            weight = items[i - 1].weight
        for j in range(cap + 1):
            if i == 0 or j == 0:
                continue
            elif weight > j:
                values[i][j] = values[i - 1][j]
            else:
                vTake = values[i - 1][j - weight] + value
                vKeep = values[i - 1][j]
                values[i][j] = max(vTake, vKeep)

    totalWeight = cap
    for i in reversed(range(n)):
        if values[i][totalWeight] == values[i + 1][totalWeight]:
            continue
        else:
            taken[i] = 1
            totalWeight -= items[i].weight

    return values[-1][-1], taken


def greedy(cap, items):
    n = len(items)
    taken = [0] * n
    filled = 0
    value = 0
    for item in sorted(items, key=attrgetter('density')):
        if filled + item.weight <= cap:
            taken[item.index] = 1
            value += item.value
            filled += item.weight

    return value, taken


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
        #solve_it(input_data)
        print(solve_it(input_data))
    else:
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/ks_4_0)')

