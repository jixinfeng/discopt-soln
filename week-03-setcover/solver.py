#!/usr/bin/python3
# -*- coding: utf-8 -*-

# The MIT License (MIT)
#
# Copyright (c) 2014 Carleton Coffrin
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


from collections import namedtuple
from psutil import cpu_count
from gurobipy import *

Set = namedtuple("Set", ['index', 'cost', 'items'])

def solve_it(input_data):
    # Modify this code to run your optimization algorithm

    # parse the input
    lines = input_data.split('\n')

    parts = lines[0].split()
    item_count = int(parts[0])
    set_count = int(parts[1])
    
    sets = []
    for i in range(1, set_count+1):
        parts = lines[i].split()
        sets.append(Set(i-1, float(parts[0]), set(map(int, parts[1:]))))

    # trivial solution
    # pick add sets one-by-one until all the items are covered
    # ==========
    # obj, opt, solution = naive(item_count, sets)

    # MIP solution
    # slow but optimal
    # ==========
    obj, opt, solution = mip(item_count, sets,
                             verbose=False,
                             time_limit=3600)

    # calculate the cost of the solution
    # obj = sum([s.cost*solution[s.index] for s in sets])

    # prepare the solution in the specified output format
    output_data = str(obj) + ' ' + str(opt) + '\n'
    output_data += ' '.join(map(str, solution))

    return output_data


def naive(item_count, sets):
    soln = [0] * len(sets)
    covered = set()

    for s in sets:
        soln[s.index] = 1
        covered |= set(s.items)
        if len(covered) >= item_count:
            break

    value = int(sum(map(lambda s: s.cost * soln[s.index], sets)))

    return value, 0, soln



def mip(item_count, sets, verbose=False, num_threads=None, time_limit=None):
    m = Model("set_covering")
    m.setParam('OutputFlag', verbose)
    if num_threads:
        m.setParam("Threads", num_threads)
    else:
        m.setParam("Threads", cpu_count())

    if time_limit:
        m.setParam("TimeLimit", time_limit)

    selections = m.addVars(len(sets), vtype=GRB.BINARY, name="set_selection")

    m.setObjective(LinExpr([s.cost for s in sets], [selections[i] for i in range(len(sets))]), GRB.MINIMIZE)

    m.addConstrs((LinExpr([1 if j in s.items else 0 for s in sets], [selections[i] for i in range(len(sets))]) >= 1
                  for j in range(item_count)),
                 name="ieq1")

    m.update()
    m.optimize()

    soln = [int(var.x) for var in m.getVars()]
    total_cost = int(sum([sets[i].cost * soln[i] for i in range(len(sets))]))

    if m.status == 2:
        opt = 1
    else:
        opt = 0

    return total_cost, opt, soln



if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
        print(solve_it(input_data))
    else:
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/sc_6_1)')

