#!/usr/bin/python3
# -*- coding: utf-8 -*-

from collections import namedtuple
from operator import attrgetter

from psutil import cpu_count
from gurobipy import *

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

    # greedy solution
    # put items with higher value "density" first
    # obj, opt, taken = greedy(capacity, items)

    # dynamic programming solution
    # optimal but high memory utilization with larger problem
    # ==========
    # obj, taken = dp(capacity, items)

    obj, opt, taken = mip(capacity, items)

    # prepare the solution in the specified output format
    output_data = str(obj) + ' ' + str(opt) + '\n'
    output_data += ' '.join(map(str, taken))
    return output_data


def mip(cap, items, verbose=False, num_threads=None):
    item_count = len(items)
    values = [item.value for item in items]
    weights = [item.weight for item in items]

    m = Model("knapsack")
    m.setParam('OutputFlag', verbose)
    if num_threads:
        m.setParam("Threads", num_threads)
    else:
        m.setParam("Threads", cpu_count())

    x = m.addVars(item_count, vtype=GRB.BINARY, name="items")
    m.setObjective(LinExpr(values, [x[i] for i in range(item_count)]), GRB.MAXIMIZE)
    m.addConstr(LinExpr(weights, [x[i] for i in range(item_count)]), GRB.LESS_EQUAL, cap, name="capacity")

    m.update()
    m.optimize()

    if m.status == 2:
        opt = 1
    else:
        opt = 0

    return int(m.objVal), opt, [int(var.x) for var in m.getVars()]


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

    return values[-1][-1], 1, taken


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

    return value, 0, taken


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

