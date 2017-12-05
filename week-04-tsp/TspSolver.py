import math


class TspSolver(object):
    def __init__(self, points):
        self.CMP_THRESHOLD = 10 ** -6
        self.points = points
        self.cycle = list(range(len(points))) + [0]
        self.obj = self.cycle_length()

    def __str__(self):
        obj = self.cycle_length()
        opt = 0
        if not self.is_valid_soln():
            raise ValueError("Solution not valid")
        output_str = "{:.2f} {}\n".format(obj, opt)
        output_str += ' '.join(map(str, self.cycle[:-1]))
        return output_str

    @staticmethod
    def point_dist(p1, p2):
        return math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)

    def is_valid_soln(self):
        return len(set(self.cycle[:-1])) == len(self.points) == len(self.cycle[:-1])

    def edge_length(self, v1, v2):
        p1 = self.points[v1]
        p2 = self.points[v2]
        return self.point_dist(p1, p2)

    def cycle_length(self):
        return sum(self.edge_length(v1, v2) for v1, v2 in zip(self.cycle[:-1], self.cycle[1:]))

    def greedy(self):
        cycle = [0]
        candidates = set(self.cycle[1:-1])
        while candidates:
            curr_point = cycle[-1]
            nearest_neighbor = None
            nearest_dist = math.inf
            for neighbor in candidates:
                neighbor_dist = self.edge_length(curr_point, neighbor)
                if neighbor_dist < nearest_dist:
                    nearest_neighbor = neighbor
                    nearest_dist = neighbor_dist
            cycle.append(nearest_neighbor)
            candidates.remove(nearest_neighbor)
        cycle.append(0)
        self.cycle = cycle
        self.obj = self.cycle_length()
        return self.__str__()
