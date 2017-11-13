#!/usr/bin/python3
# -*- coding: utf-8 -*-

import math
from collections import namedtuple

Customer = namedtuple("Customer", ['index', 'demand', 'x', 'y'])


def length(customer1, customer2):
    return math.sqrt((customer1.x - customer2.x) ** 2 + (customer1.y - customer2.y) ** 2)


def is_valid_tour(customers, tour, vehicle_cap):
    return sum([customers[i].demand for i in tour]) <= vehicle_cap


def is_valid_soln(customers, tours, vehicle_cap):
    return all([is_valid_tour(customers, tour, vehicle_cap) for tour in tours])


def single_tour_dist(customers, tour):
    dist = 0
    for i in range(1, len(tour)):
        dist += length(customers[tour[i]], customers[tour[i - 1]])
    return dist


def total_tour_dist(customers, tours):
    return sum([single_tour_dist(customers, tour) for tour in tours])


def make_output(customers, tours):
    obj = total_tour_dist(customers, tours)
    opt = 0
    output_str = "{:.2f} {}\n".format(obj, opt)
    for tour in tours:
        output_str += (' '.join(map(str,[c for c in tour])) + '\n')
    return output_str


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
    depot = customers[0]

    # trivial solution
    # assign customers to vehicles starting by the largest customer demands
    vehicle_tours = greedy(customers, vehicle_count, vehicle_capacity)

    # prepare the solution in the specified output format
    outputData = make_output(customers, vehicle_tours)
    return outputData


def naive(customers, vehicle_ct, vehicle_cap):
    tours = []
    customer_ct = len(customers)
    curr_idx = 1
    for v in range(vehicle_ct):
        remaining_cap = vehicle_cap
        tours.append([])
        tours[-1].append(0)
        while curr_idx < customer_ct and remaining_cap > customers[curr_idx].demand:
            tours[-1].append(curr_idx)
            remaining_cap -= customers[curr_idx].demand
            curr_idx += 1
        tours[-1].append(0)
    if curr_idx == customer_ct:
        return tours
    else:
        raise ValueError("Naive solution does not exist.")


def greedy(customers, vehicle_ct, vehicle_cap):
    tours = []
    customer_ct = len(customers)
    remaining_customers = set(customers[1:])
    for v in range(vehicle_ct):
        remaining_cap = vehicle_cap
        tours.append([])
        tours[-1].append(0)
        while remaining_customers and remaining_cap > min([c.demand for c in remaining_customers]):
            for customer in sorted(remaining_customers, reverse=True, key=lambda c: c.demand):
                if customer.demand <= remaining_cap:
                    tours[-1].append(customer.index)
                    remaining_cap -= customer.demand
                    remaining_customers.remove(customer)
                    continue
        tours[-1].append(0)
    if remaining_customers:
        raise ValueError("Greedy solution does not exist.")
    else:
        return tours


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
        print(solve_it(input_data))
    else:
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/vrp_5_4_1)')

