from TspSolver import *
from itertools import combinations
from time import time


class TwoOptSolver(TspSolver):
    def swap(self, start, end):
        improved = False
        new_cycle = self.cycle[:start] + self.cycle[start:end + 1][::-1] + self.cycle[end + 1:]
        new_obj = self.obj - \
                     (self.edge_length(self.cycle[start - 1], self.cycle[start]) +
                      self.edge_length(self.cycle[end], self.cycle[(end + 1)])) + \
                     (self.edge_length(new_cycle[start - 1], new_cycle[start]) +
                      self.edge_length(new_cycle[end], new_cycle[(end + 1)]))
        if new_obj < self.obj - self.CMP_THRESHOLD:
            self.cycle = new_cycle
            self.obj = new_obj
            improved = True
        return improved

    def solve(self, t_threshold=None):
        improved = True
        t = time()
        while improved:
            if t_threshold and time() - t >= t_threshold:
                break
            improved = False
            for start, end in combinations(range(1, len(self.cycle) - 1), 2):
                if self.swap(start, end):
                    improved = True
                    break
        return self.__str__()
