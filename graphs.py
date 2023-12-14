from ls_network import *

def init():
    return 0
class DistanceVector:
    def __init__(self, tables) -> None:
        self.tables = dict()
        if (tables is not None):
            for x in tables:
                self.tables[x] = dict()
                for y in tables:
                    self.tables[x][y] = (float('inf'),-1)
                for end, weight in tables[x]:
                    self.tables[x][end] = (weight, end)
                self.tables[x][x] = (0, x)
        self.queue = []
        for x in self.tables:
            self.queue.append(x)
    def distance_vector(self):
        changesC = 0
        count = 0
        packets = 0
        while (self.queue):
            x = self.queue.pop(0)
            for y in self.tables[x]:
                change = False
                if (self.tables[x][y][1]==y and self.tables[x][y][0] != 0):
                    packets+=1 #packet sent to router y
                    xydist = self.tables[x][y][0]
                    yval = self.tables[y]
                    for z in self.tables[x]:
                        if self.tables[x][z][1] == y:
                            #split horizon avoidance of count to infinity
                            continue
                        elif yval[z][0] > self.tables[x][z][0]+xydist:
                            #print("Value from", y, "to", z, "changed to", prop[z][0]+xydist, "from", self.tables[y][z][0])
                            self.tables[y][z] = (self.tables[x][z][0]+xydist, x)
                            changesC+=1 # number of times an edge cost is updated
                            change = True
                    if change:
                        count+=1 # number of times a router gets updated (and put onto the queue)
                        if y not in self.queue:
                            self.queue.append(y)
            #print(len(self.queue))
        #print("Routers updated:", count, "times")
        #print("Changed value counter:", changesC)    
        #print("Packets sent:", packets)
        return (packets, count, changesC)                
        #for x in self.tables:
            #print("x:", self.tables[x])
    def remove_node(self, node):
        for x in self.tables:
            del self.tables[x][node]
        del self.tables[node]
    def add_node(self, node):
        self.tables[node] = dict()
        for x in self.tables:
            self.tables[node][x] = (float('inf'),-1)
            self.tables[x][node] = (float('inf'),-1)
        self.tables[node][node] = (0, node)
    def remove_link(self, start, end):
        self.tables[start][end] = (float('inf'),-1)
        self.tables[end][start] = (float('inf'),-1)
    def add_link(self, start, end, weight):
        if self.tables[start][end][0] > weight:
            self.tables[start][end] = (weight, end)
            if start not in self.queue:
                self.queue.append(start)
            if end not in self.queue:
                self.queue.append(end)
        if self.tables[end][start][0] > weight:
            self.tables[end][start] = (weight, start)
            if start not in self.queue:
                self.queue.append(start)
            if end not in self.queue:
                self.queue.append(end)

def link_state():
    network = Network()
    # network.add_router_and_links(1, [[2, 1], [3, 1]])
    # network.add_router_and_links(2, [[1, 1], [3, 1]])
    # network.add_router_and_links(3, [[1, 1], [2, 1]])
    network.add_router(1)
    network.add_router(2)
    network.add_router(3)
    network.add_link(1, 2, 1)
    network.add_link(1, 3, 1)
    network.add_link(2, 3, 1)
    network.do_tick()
    network.dump_network("ls_test.json")

    return 0

def dist_vec():
    dv = DistanceVector(None)
    """dv.add_node(1)
    dv.add_node(2)
    dv.add_node(3)
    dv.add_node(4)
    dv.add_node(5)
    dv.add_link(1,2,1)
    dv.add_link(1,3,1)
    dv.add_link(2,3,3)
    dv.add_link(2,4,1)
    dv.add_link(4,5,2)
    dv.distance_vector()"""
    dv.add_node(1)
    dv.add_node(2)
    dv.add_node(3)
    dv.add_node(4)
    dv.add_node(5)
    dv.add_link(1,2,1)
    dv.add_link(2,3,1)
    dv.add_link(3,4,1)
    dv.add_link(4,5,1)
    dv.distance_vector()
    dv.remove_link(1,2)
    dv.distance_vector()

if __name__ == "__main__":
    link_state()
    dist_vec()
