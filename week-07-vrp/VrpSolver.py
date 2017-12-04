import math
import itertools
from time import time


class VrpSolver(object):
    def __init__(self, customers, vehicle_count, vehicle_capacity):
        self.CMP_THRESHOLD = 10 ** -6
        self.customers = customers
        assert self.customers[0].demand == 0
        self.c_ct = len(customers)
        self.v_ct = vehicle_count
        self.v_cap = vehicle_capacity
        self.obj = 0
        self.tours = self.greedy_init()
        return

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

    def tour_demand(self, tour):
        return sum([self.customers[i].demand for i in tour])

    def have_duplicate_missing(self):
        customers = set(range(1, len(self.customers)))
        for tour in self.tours:
            for c in tour[1:-1]:
                if c not in customers:
                    print("Duplicate")
                    return True
        if customers:
            print("Missing")
            return True
        return False

    def is_valid_tour(self, tour):
        """
        :param tour: list of int, tour of a single vehicle
        :return: True if tour is valid

        a tour is valid if:
        1. total demand doesn't not exceed vehicle cap
        2. start and end at customer[0], which is the base
        3. does not go back to base during the tour
        4. does not contain duplicate stop
        """
        is_valid = (self.tour_demand(tour) <= self.v_cap) and \
                   (tour[0] == 0) and (tour[-1] == 0) and \
                   (0 not in tour[1:-1]) and \
                   (len(set(tour[1:-1])) == len(tour[1:-1]))
        return is_valid

    def is_valid_soln(self):
        """
        :return: True if the whole solution is valid

        a solution is valid if:
        1. every tour is valid
        2. (TODO)no duplicate/missing customer
        """
        return all([self.is_valid_tour(tour) for tour in self.tours])

    def single_tour_dist(self, tour):
        if not self.is_valid_tour(tour):
            return math.inf
        tour_dist = 0
        for i in range(1, len(tour)):
            customer_1 = self.customers[tour[i - 1]]
            customer_2 = self.customers[tour[i]]
            tour_dist += self.dist(customer_1, customer_2)
        return tour_dist

    def every_tour_dists(self):
        return [self.single_tour_dist(tour) for tour in self.tours]

    def total_tour_dist(self):
        dists = self.every_tour_dists()
        if math.inf in dists:
            raise ValueError("Invalid tour detected.")
        else:
            return sum(dists)

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

    def shift(self, i_from, start_from, end_from, i_to, j_to, debug=False):
        """
        :param i_from: index of tour shift from
        :param start_from: start index of segment
        :param end_from: end index of segment (inclusive)
        :param i_to: index of tour shift to
        :param j_to: location
        :param debug: print details if True
        :return: True if improved

        shift a segment of tour into another tour
        2 possible ways:
        shift directly and reverse after shift
        """
        tour_from_old = self.tours[i_from]
        tour_to_old = self.tours[i_to]
        improved = False
        if debug:
            print("".join(["-"] * 10))
            print("old tours")
            print(tour_from_old)
            print(tour_to_old)

        seg_shift = tour_from_old[start_from: end_from + 1]

        tour_from_new = tour_from_old[:start_from] + tour_from_old[end_from + 1:]
        tour_to_new_1 = tour_to_old[:j_to] + seg_shift + tour_to_old[j_to:]
        tour_to_new_2 = tour_to_old[:j_to] + seg_shift[::-1] + tour_to_old[j_to:]
        if debug:
            print("seg_shift")
            print(seg_shift)
            print("new tours")
            print("{}|{}".format(tour_from_old[:start_from], tour_from_old[end_from + 1:]))
            print("{}|{}|{}".format(tour_to_old[:j_to], seg_shift, tour_to_old[j_to:]))
            print("{}|{}|{}".format(tour_to_old[:j_to], seg_shift[::-1], tour_to_old[j_to:]))

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

        if obj_new_1 < self.obj - self.CMP_THRESHOLD:
            self.tours[i_from] = tour_from_new
            self.tours[i_to] = tour_to_new_1
            # self.obj = obj_new_1
            self.obj = self.total_tour_dist()
            improved = True

        if obj_new_2 < self.obj - self.CMP_THRESHOLD:
            self.tours[i_from] = tour_from_new
            self.tours[i_to] = tour_to_new_2
            # self.obj = obj_new_2
            self.obj = self.total_tour_dist()
            improved = True

        return improved

    def interchange(self, i_1, start_1, end_1, i_2, start_2, end_2, debug=False):
        """
        :param i_1:
        :param start_1:
        :param end_1:
        :param i_2:
        :param start_2:
        :param end_2:
        :param debug:
        :return:

        interchange 2 segments from 2 tours
        4 possible ways:
        interchange directly, reverse either segment, reverse both segments
        """
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

        if new_obj_1 < self.obj - self.CMP_THRESHOLD:
            self.tours[i_1] = tour_1_new_1
            self.tours[i_2] = tour_2_new_1
            # self.obj = new_obj_1
            self.obj = self.total_tour_dist()
            improved = True

        if new_obj_2 < self.obj - self.CMP_THRESHOLD:
            self.tours[i_1] = tour_1_new_1
            self.tours[i_2] = tour_2_new_2
            # self.obj = new_obj_2
            self.obj = self.total_tour_dist()
            improved = True

        if new_obj_3 < self.obj - self.CMP_THRESHOLD:
            self.tours[i_1] = tour_1_new_2
            self.tours[i_2] = tour_2_new_1
            # self.obj = new_obj_3
            self.obj = self.total_tour_dist()
            improved = True

        if new_obj_4 < self.obj - self.CMP_THRESHOLD:
            self.tours[i_1] = tour_1_new_2
            self.tours[i_2] = tour_2_new_2
            # self.obj = new_obj_4
            self.obj = self.total_tour_dist()
            improved = True

        return improved

    def exchange(self, i, start, end, debug=False):
        """
        :param i:
        :param start:
        :param end:
        :param debug:
        :return:

        reverse a segment of a tour
        only 1 way to do this
        """
        improved = False
        tour_old = self.tours[i]
        seg = tour_old[start: end + 1]
        tour_new = tour_old[:start] + seg[::-1] + tour_old[end + 1:]
        if debug:
            print("".join(["-"] * 10))
            print("old tour")
            print(tour_old)
            print("seg")
            print(seg)
            print("new tour")
            print("{}|{}|{}".format(tour_old[:start], seg[::-1], tour_old[end + 1:]))

        new_obj = self.obj - self.single_tour_dist(tour_old) + self.single_tour_dist(tour_new)
        if new_obj < self.obj - self.CMP_THRESHOLD:
            self.tours[i] = tour_new
            # self.obj = new_obj
            self.obj = self.total_tour_dist()
            improved = True
        return improved

    def ladder(self, i_1, i_2, j_1, j_2, debug=False):
        """
        :param i_1:
        :param i_2:
        :param j_1:
        :param j_2:
        :param debug:
        :return:

        split two tours into head and tail respectively, and re-shuffle them
        2 possible ways
        """
        tour_1_old = self.tours[i_1]
        tour_2_old = self.tours[i_2]
        improved = False
        if debug:
            print("".join(["-"] * 10))
            print("old tours")
            print(tour_1_old)
            print(tour_2_old)

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
        if debug:
            print("new tours")
            print("{}|{}".format(seg_1_head, seg_2_tail))
            print("{}|{}".format(seg_2_head, seg_1_tail))
            print("{}|{}".format(seg_1_head, seg_2_head[::-1]))
            print("{}|{}".format(seg_1_tail[::-1], seg_2_tail))

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

        if new_obj_1 < self.obj - self.CMP_THRESHOLD:
            self.tours[i_1] = tour_1_new_1
            self.tours[i_2] = tour_2_new_1
            # self.obj = new_obj_1
            self.obj = self.total_tour_dist()
            improved = True

        if new_obj_2 < self.obj - self.CMP_THRESHOLD:
            self.tours[i_1] = tour_1_new_2
            self.tours[i_2] = tour_2_new_2
            # self.obj = new_obj_2
            self.obj = self.total_tour_dist()
            improved = True

        return improved

    def solve(self,
              shift=True,
              interchange=True,
              exchange=True,
              ladder=True,
              t_threshold=None,
              verbose=False,
              debug=False):
        improved = True
        t_start = time()

        while improved:
            if t_threshold and time() - t_start >= t_threshold:
                break
            shift_improved = False
            interchange_improved = False
            exchange_improved = False
            ladder_improved = False
            self.obj = self.total_tour_dist()
            prev_obj = self.obj
            if verbose or debug:
                print(self.obj)

            # try shift
            if shift:
                for i_from, tour_from in enumerate(self.tours):
                    if shift_improved: break
                    for start_from, end_from in itertools.combinations(range(1, len(tour_from) - 1), 2):
                        if shift_improved: break
                        for i_to, tour_to in enumerate(self.tours):
                            if shift_improved: break
                            if i_from == i_to: continue
                            for j_to in range(1, len(tour_to) - 1):
                                if self.shift(i_from, start_from, end_from, i_to, j_to, debug):
                                    shift_improved = True
                                    break

            # try interchange
            if interchange:
                for i_1, tour_1 in enumerate(self.tours):
                    if interchange_improved: break
                    for start_1, end_1 in itertools.combinations(range(1, len(tour_1) - 1), 2):
                        if interchange_improved: break
                        for i_2, tour_2 in enumerate(self.tours):
                            if interchange_improved: break
                            if i_1 == i_2: continue
                            for start_2, end_2 in itertools.combinations(range(1, len(tour_2) - 1), 2):
                                if self.interchange(i_1, start_1, end_1, i_2, start_2, end_2, debug):
                                    interchange_improved = True
                                    break

            # try exchange
            if exchange:
                for i, tour in enumerate(self.tours):
                    for start, end in itertools.combinations(range(1, len(tour) - 1), 2):
                        if self.exchange(i, start, end, debug):
                            exchange_improved = True
                            break

            # try ladder
            if ladder:
                for i_1, tour_1 in enumerate(self.tours):
                    if ladder_improved: break
                    for j_1 in range(2, len(tour_1) - 2):
                        if ladder_improved: break
                        for i_2, tour_2 in enumerate(self.tours):
                            if i_1 == i_2: continue
                            if ladder_improved: break
                            for j_2 in range(2, len(tour_2) - 2):
                                if self.ladder(i_1, i_2, j_1, j_2, debug):
                                    ladder_improved = True
                                    break
            if verbose or debug:
                print(shift_improved, interchange_improved, exchange_improved, ladder_improved)
                print(prev_obj - self.obj)
            improved = shift_improved or interchange_improved or exchange_improved or ladder_improved
        return self.tours
