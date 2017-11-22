#!/usr/bin/python3
# -*- coding: utf-8 -*-

import math
import itertools
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

    def is_valid_tour(self, tour):
        is_valid = (self.single_tour_demand(tour) <= self.v_cap) and \
                   (tour[0] == 0) and (tour[-1] == 0) and \
                   (0 not in tour[1:-1]) and \
                   (len(set(tour[1:-1])) == len(tour[1:-1]))
        return is_valid

    def is_valid_soln(self):
        return all([self.is_valid_tour(tour) for tour in self.tours])

    def single_tour_dist(self, tour):
        if not self.is_valid_tour(tour):
            return math.inf
        tour_dist = 0
        for i in range(1, len(tour)):
            tour_dist += self.dist(self.customers[tour[i]], self.customers[tour[i - 1]])
        return tour_dist

    def every_tour_dists(self):
        return {v: self.single_tour_dist(tour) for v, tour in enumerate(self.tours)}

    def total_tour_dist(self):
        dists = self.every_tour_dists()
        if math.inf in dists.values():
            raise ValueError("Invalid tour detected.")
        else:
            return sum(dists.values())

    def single_tour_demand(self, tour):
        return sum([self.customers[i].demand for i in tour])

    def every_tour_demands(self):
        return {v: self.single_tour_demand(tour) for v, tour in enumerate(self.tours)}

    def single_remaining_cap(self, tour):
        return self.v_cap - self.single_tour_demand(tour)

    def every_remaining_caps(self):
        return {v: self.single_remaining_cap(tour) for v, tour in enumerate(self.tours)}

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

    def shift(self, i_from, start_from, end_from, i_to, j_to):
        tour_from_old = self.tours[i_from]
        tour_to_old = self.tours[i_to]
        improved = False

        seg_shift = tour_from_old[start_from: end_from + 1]
        tour_from_new = tour_from_old[: start_from] + tour_from_old[end_from + 1:]

        tour_to_new_1 = tour_to_old[: j_to] + seg_shift + tour_to_old[j_to:]
        tour_to_new_2 = tour_to_old[: j_to] + seg_shift[::-1] + tour_to_old[j_to:]

        dist_from_old = self.single_tour_dist(tour_from_old)
        dist_to_old = self.single_tour_dist(tour_to_old)
        dist_from_new = self.single_tour_dist(tour_from_new)

        dist_to_new_1 = self.single_tour_dist(tour_to_new_1)
        dist_to_new_2 = self.single_tour_dist(tour_to_new_2)

        obj_new_1 = self.obj - \
                    (dist_from_old + dist_to_old) + \
                    (dist_from_new + dist_to_new_1)

        obj_new_2 = self.obj - \
                    (dist_from_old + dist_to_old) + \
                    (dist_from_new + dist_to_new_2)

        if obj_new_1 < self.obj:
            self.tours[i_from] = tour_from_new
            self.tours[i_to] = tour_to_new_1
            self.obj = obj_new_1
            improved = True

        if obj_new_2 < self.obj:
            self.tours[i_from] = tour_from_new
            self.tours[i_to] = tour_to_new_2
            self.obj = obj_new_2
            improved = True

        return improved

    def interchange(self, i_1, start_1, end_1, i_2, start_2, end_2, debug=False):
        tour_1_old = self.tours[i_1]
        tour_2_old = self.tours[i_2]
        improved = False
        if debug:
            print("".join(["-"] * 10))
            print("old tours")
            print(tour_1_old)
            print(tour_2_old)

        seg_1 = tour_1_old[start_1: end_1 + 1]
        seg_2 = tour_2_old[start_2: end_2 + 1]
        if debug:
            print("segs")
            print("{}, {}, {}".format(start_1, end_1, seg_1))
            print("{}, {}, {}".format(start_2, end_2, seg_2))

        # tour1 <- seg2, not reversed
        tour_1_new_1 = tour_1_old[: start_1] + seg_2 + tour_1_old[end_1 + 1:]
        # tour1 <- seg2, reversed
        tour_1_new_2 = tour_1_old[: start_1] + seg_2[::-1] + tour_1_old[end_1 + 1:]
        # tour2 <- seg1, not reversed
        tour_2_new_1 = tour_2_old[: start_2] + seg_1 + tour_2_old[end_2 + 1:]
        # tour2 <- seg1, reversed
        tour_2_new_2 = tour_2_old[: start_2] + seg_1[::-1] + tour_2_old[end_2 + 1:]
        if debug:
            print("new tours")
            print("{}|{}|{}".format(tour_1_old[: start_1], seg_2, tour_1_old[end_1 + 1:]))
            print("{}|{}|{}".format(tour_1_old[: start_1], seg_2[::-1], tour_1_old[end_1 + 1:]))
            print("{}|{}|{}".format(tour_2_old[: start_1], seg_1, tour_2_old[end_2 + 1:]))
            print("{}|{}|{}".format(tour_2_old[: start_1], seg_1[::-1], tour_2_old[end_2 + 1:]))

        # old tour lengths
        dist_1_old = self.single_tour_dist(tour_1_old)
        dist_2_old = self.single_tour_dist(tour_2_old)

        # new tour lengths
        dist_1_new_1 = self.single_tour_dist(tour_1_new_1)
        dist_1_new_2 = self.single_tour_dist(tour_1_new_2)
        dist_2_new_1 = self.single_tour_dist(tour_2_new_1)
        dist_2_new_2 = self.single_tour_dist(tour_2_new_2)

        new_obj_1 = self.obj - (dist_1_old + dist_2_old) + (dist_1_new_1 + dist_2_new_1)
        new_obj_2 = self.obj - (dist_1_old + dist_2_old) + (dist_1_new_1 + dist_2_new_2)
        new_obj_3 = self.obj - (dist_1_old + dist_2_old) + (dist_1_new_2 + dist_2_new_1)
        new_obj_4 = self.obj - (dist_1_old + dist_2_old) + (dist_1_new_2 + dist_2_new_2)

        if new_obj_1 < self.obj:
            self.tours[i_1] = tour_1_new_1
            self.tours[i_2] = tour_2_new_1
            self.obj = new_obj_1
            improved = True

        if new_obj_2 < self.obj:
            self.tours[i_1] = tour_1_new_1
            self.tours[i_2] = tour_2_new_2
            self.obj = new_obj_2
            improved = True

        if new_obj_3 < self.obj:
            self.tours[i_1] = tour_1_new_2
            self.tours[i_2] = tour_2_new_1
            self.obj = new_obj_3
            improved = True

        if new_obj_4 < self.obj:
            self.tours[i_1] = tour_1_new_2
            self.tours[i_2] = tour_2_new_2
            self.obj = new_obj_4
            improved = True

        return improved

    def exchange(self, i, start, end):
        improved = False
        tour_old = self.tours[i]
        seg = tour_old[start: end + 1]
        tour_new = tour_old[:start] + seg[::-1] + tour_old[end + 1:]
        new_obj = self.obj - self.single_tour_dist(tour_old) + self.single_tour_dist(tour_new)
        if new_obj < self.obj:
            self.tours[i] = tour_new
            self.obj = new_obj
            improved = True
        return improved

    def ladder(self, i_1, i_2, j_1, j_2):
        tour_1_old = self.tours[i_1]
        tour_2_old = self.tours[i_2]
        improved = False

        seg_1_head = tour_1_old[:j_1]
        seg_1_tail = tour_1_old[j_1:]
        seg_2_head = tour_2_old[:j_2]
        seg_2_tail = tour_2_old[j_2:]

        # head + tail
        tour_1_new_1 = seg_1_head + seg_2_tail
        tour_2_new_1 = seg_2_head + seg_1_tail

        # head + head(reversed) / tail(reversed) + tail
        tour_1_new_2 = seg_1_head + seg_2_head[::-1]
        tour_2_new_2 = seg_1_tail[::-1] + seg_2_tail

        # old tour lengths
        dist_1_old = self.single_tour_dist(tour_1_old)
        dist_2_old = self.single_tour_dist(tour_2_old)

        # new tour lengths
        dist_1_new_1 = self.single_tour_dist(tour_1_new_1)
        dist_1_new_2 = self.single_tour_dist(tour_1_new_2)
        dist_2_new_1 = self.single_tour_dist(tour_2_new_1)
        dist_2_new_2 = self.single_tour_dist(tour_2_new_2)

        new_obj_1 = self.obj - (dist_1_old + dist_2_old) + (dist_1_new_1 + dist_2_new_1)
        new_obj_2 = self.obj - (dist_1_old + dist_2_old) + (dist_1_new_2 + dist_2_new_2)

        if new_obj_1 < self.obj:
            self.tours[i_1] = tour_1_new_1
            self.tours[i_2] = tour_2_new_1
            self.obj = new_obj_1
            improved = True

        if new_obj_2 < self.obj:
            self.tours[i_1] = tour_1_new_2
            self.tours[i_2] = tour_2_new_2
            self.obj = new_obj_2
            improved = True

        return improved

    def solve(self, verbose=False):
        self.greedy_init()
        improved = True
        while improved:
            improved = False
            if verbose:
                print(self.obj)

            # try shift
            for i_from, tour_from in enumerate(self.tours):
                if improved: break
                for start_from, end_from in itertools.combinations(range(1, len(tour_from) - 1), 2):
                    if improved: break
                    for i_to, tour_to in enumerate(self.tours):
                        if improved: break
                        if i_from == i_to: continue
                        for j_to in range(1, len(tour_to) - 1):
                            if self.shift(i_from, start_from, end_from, i_to, j_to):
                                improved = True
                                break

            # try interchange
            for i_1, tour_1 in enumerate(self.tours):
                if improved: break
                for start_1, end_1 in itertools.combinations(range(1, len(tour_1) - 1), 2):
                    if improved: break
                    for i_2, tour_2 in enumerate(self.tours):
                        if improved: break
                        if i_1 == i_2: continue
                        for start_2, end_2 in itertools.combinations(range(1, len(tour_2) - 1), 2):
                            if self.interchange(i_1, start_1, end_1, i_2, start_2, end_2):
                                improved = True
                                break

            # try exchange
            for i, tour in enumerate(self.tours):
                for start, end in itertools.combinations(range(1, len(tour) - 1), 2):
                    if self.exchange(i, start, end):
                        improved = True
                        break

            # try ladder
            for i_1, tour_1 in enumerate(self.tours):
                if improved: break
                for j_1 in range(1, len(tour_1) - 1):
                    if improved: break
                    for i_2, tour_2 in enumerate(self.tours):
                        if improved: break
                        for j_2 in range(1, len(tour_2) - 1):
                            if self.ladder(i_1, i_2, j_1, j_2):
                                improved = True
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
    solver.solve()

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

