#!/usr/bin/python3
# -*- coding: utf-8 -*-

import math
from collections import namedtuple

Customer = namedtuple("Customer", ['index', 'demand', 'x', 'y'])


class VrpSolver(object):
    def __init__(self, customers, vehicle_count, vehicle_capacity):
        self.customers = customers
        assert self.customers[0].demand == 0
        self.c_ct = len(customers)
        self.v_ct = vehicle_count
        self.v_cap = vehicle_capacity
        self.obj = 0
        self.tours = []

    def __str__(self):
        obj = self.total_tour_dist()
        opt = 0
        if not self.is_valid_soln():
            raise ValueError("Solution not valid")
        output_str = "{:.2f} {}\n".format(obj, opt)
        for tour in self.tours:
            output_str += (' '.join(map(str, [c for c in tour])) + '\n')
        return output_str

    @staticmethod
    def dist(c1, c2):
        return math.sqrt((c1.x - c2.x) ** 2 + (c1.y - c2.y) ** 2)

    def single_tour_dist(self, tour):
        tour_dist = 0
        for i in range(1, len(tour)):
            tour_dist += self.dist(self.customers[tour[i]], self.customers[tour[i - 1]])
        return tour_dist

    def every_tour_dists(self):
        return {v: self.single_tour_dist(tour) for v, tour in enumerate(self.tours)}

    def total_tour_dist(self):
        return sum([self.single_tour_dist(tour) for tour in self.tours])

    def single_tour_demand(self, tour):
        return sum([self.customers[i].demand for i in tour])

    def every_tour_demands(self):
        return {v: self.single_tour_demand(tour) for v, tour in enumerate(self.tours)}

    def sinlge_remaining_cap(self, tour):
        return self.v_cap - self.single_tour_demand(tour)

    def every_remaining_caps(self):
        return {v: self.sinlge_remaining_cap(tour) for v, tour in enumerate(self.tours)}

    def is_valid_tour(self, tour):
        return self.single_tour_demand(tour) <= self.v_cap

    def is_valid_soln(self):
        return all([self.is_valid_tour(tour) for tour in self.tours])

    def greedy_init(self):
        tours = []
        remaining_customers = set(self.customers[1:])
        for v in range(self.v_ct):
            remaining_cap = self.v_cap
            tours.append([])
            tours[-1].append(0)
            while remaining_customers and remaining_cap > min([c.demand for c in remaining_customers]):
                for customer in sorted(remaining_customers, reverse=True, key=lambda c: c.demand):
                    if customer.demand <= remaining_cap:
                        tours[-1].append(customer.index)
                        remaining_cap -= customer.demand
                        remaining_customers.remove(customer)
            tours[-1].append(0)
        if remaining_customers:
            raise ValueError("Greedy solution does not exist.")
        else:
            self.tours = tours
            self.obj = self.total_tour_dist()
            return self.tours

    def move(self, i_from, j_from, i_to, j_to):
        new_tour_from = self.tours[i_from][:]
        new_tour_to = self.tours[i_to][:]
        customer_idx = new_tour_from.pop(j_from)
        new_tour_to.insert(j_to, customer_idx)
        if not self.is_valid_tour(new_tour_to):
            return False
        new_obj = self.obj - \
                  (self.single_tour_dist(self.tours[i_from]) + self.single_tour_dist(self.tours[i_to])) + \
                  (self.single_tour_dist(new_tour_from) + self.single_tour_dist(new_tour_to))
        if new_obj < self.obj:
            self.tours[i_from] = new_tour_from
            self.tours[i_to] = new_tour_to
            self.obj = new_obj
            return True
        else:
            return False

    def swap(self, i_c1, j_c1, i_c2, j_c2):
        pass

    def flip(self, c1, c2):
        pass

    def solve(self):
        self.greedy_init()
        improved = True
        while improved:
            improved = False
            for v_from, tour_from in enumerate(self.tours):
                if improved:
                    break
                for idx_from in range(1, len(tour_from) - 1):
                    if improved:
                        break
                    for v_to, tour_to in enumerate(self.tours):
                        if improved:
                            break
                        if v_from == v_to:
                            continue
                        for idx_to in range(1, len(tour_to) - 1):
                            improved = self.move(v_from, idx_from, v_to, idx_to)
                            if improved:
                                break
        return self.tours


def solve_it(input_data):
    # Modify this code to run your optimization algorithm

    # parse the input
    lines = input_data.split('\n')

    parts = lines[0].split()
    customer_count = int(parts[0])
    vehicle_count = int(parts[1])
    vehicle_capacity = int(parts[2])
    
    customers = []
    for i in range(1, customer_count+1):
        line = lines[i]
        parts = line.split()
        customers.append(Customer(i-1, int(parts[0]), float(parts[1]), float(parts[2])))

    # the depot is always the first customer in the input
    solver = VrpSolver(customers, vehicle_count, vehicle_capacity)
    tours = solver.solve()

    output_data = solver.__str__()
    return output_data


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
        print(solve_it(input_data))
    else:
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/vrp_5_4_1)')

