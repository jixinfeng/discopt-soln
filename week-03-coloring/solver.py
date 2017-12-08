#!/usr/bin/python3
# -*- coding: utf-8 -*-

from psutil import cpu_count
from gurobipy import *
import networkx as nx


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

    # trivial solution
    # every node has its own color
    # ==========
    # obj = node_count
    # opt = 0
    # solution = range(0, node_count)

    if node_count <= 100:
        # MIP solution using Gurobi
        # slow but optimal
        # ==========
        obj, opt, solution = mip(node_count, edges,
                                 verbose=False,
                                 num_threads=1,
                                 time_limit=3600*4,
                                 greedy_init=True)
    else:
        # greedy solution
        # try all greedy strategies provided by NetworkX and pick the best one
        # ==========
        obj, opt, solution = greedy(node_count, edges)

    # prepare the solution in the specified output format
    output_data = str(obj) + ' ' + str(opt) + '\n'
    output_data += ' '.join(map(str, solution))

    return output_data


def mip(node_count, edges, verbose=False, num_threads=None, time_limit=None, greedy_init=False):
    m = Model("graph_coloring")
    m.setParam('OutputFlag', verbose)
    if num_threads:
        m.setParam("Threads", num_threads)
    else:
        m.setParam("Threads", cpu_count())

    if time_limit:
        m.setParam("TimeLimit", time_limit)

    init_color_count, _, greedy_color = greedy(node_count, edges)

    colors = m.addVars(init_color_count, vtype=GRB.BINARY, name="colors")
    nodes = m.addVars(node_count, init_color_count, vtype=GRB.BINARY, name="assignments")
    # nodes[(node_idx, color_idx)]

    if greedy_init:
        for i in range(init_color_count):
            colors[i].setAttr("Start", 0)
            for j in range(node_count):
                nodes[(j, i)].setAttr("Start", 0)

        for i, j in enumerate(greedy_color):
            colors[j].setAttr("Start", 1)
            nodes[(i, j)].setAttr("Start", 1)

    m.setObjective(quicksum(colors), GRB.MINIMIZE)

    # each node has only one color
    m.addConstrs((nodes.sum(i, "*") == 1
                  for i in range(node_count)),
                 name="eq1")

    # only color in use can be assigned ot nodes
    m.addConstrs((nodes[(i, k)] - colors[k] <= 0
                  for i in range(node_count)
                  for k in range(init_color_count)),
                 name="ieq2")

    # vertices sharing one edge have different colors
    m.addConstrs((nodes[(edge[0], k)] + nodes[(edge[1], k)] <= 1
                  for edge in edges
                  for k in range(init_color_count)),
                 name="ieq3")

    # color index should be as low as possible
    m.addConstrs((colors[i] - colors[i + 1] >= 0
                  for i in range(init_color_count - 1)),
                 name="ieq4")

    m.update()
    m.optimize()

    isol = [int(var.x) for var in m.getVars()]
    color_count = sum(isol[:init_color_count])
    soln = [j for i in range(node_count) for j in range(init_color_count)
            if isol[init_color_count + init_color_count * i + j] == 1]

    if m.status == 2:
        opt = 1
    else:
        opt = 0

    return color_count, opt, soln


def greedy(node_count, edges):
    graph = nx.Graph()
    graph.add_nodes_from(range(node_count))
    graph.add_edges_from(edges)

    strategies = [nx.coloring.strategy_largest_first,
                  nx.coloring.strategy_random_sequential,
                  nx.coloring.strategy_smallest_last,
                  nx.coloring.strategy_independent_set,
                  nx.coloring.strategy_connected_sequential_bfs,
                  nx.coloring.strategy_connected_sequential_dfs,
                  nx.coloring.strategy_connected_sequential,
                  nx.coloring.strategy_saturation_largest_first]

    best_color_count, best_coloring = node_count, {i: i for i in range(node_count)}
    for strategy in strategies:
        curr_coloring = nx.coloring.greedy_color(G=graph, strategy=strategy)
        curr_color_count = max(curr_coloring.values()) + 1
        if curr_color_count < best_color_count:
            best_color_count = curr_color_count
            best_coloring = curr_coloring
    return best_color_count, 0, [best_coloring[i] for i in range(node_count)]


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
        print(solve_it(input_data))
    else:
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/gc_4_1)')

