import heapq
from enum import Enum
from json import dumps

class PacketType(Enum):
    DATA = 0
    CONTROL = 1

# Packet class for network simulator
class Packet:
    def __init__(self, src, dest, type: PacketType, seq_num, payload) -> None:
        self.src = src
        self.dest = dest
        self.type = type
        self.seq_num = seq_num
        self.payload = payload

# Graph class for network simulator
class Graph:
    def __init__(self, id):
        self.id = id
        self.graph = {}  # {node: [neighbors]}
        self.graph[id] = []
    
    def add_node(self, node):
        if node not in self.graph:
            self.graph[node] = []

    def add_edge(self, dest, cost):
        self.graph[self.id].append((dest, cost))

    def remove_edge(self, dest):
        for edge in self.graph[self.id]:
            if edge[0] == dest:
                self.graph[self.id].remove(edge)
                break

    def dijkstra(self):
        priority_queue = [(0, self.id)]  # [(distance, node)]
        visited = set()
        shortest_paths = {node: (float('inf'), None) for node in self.graph}  # {node: (distance, next_hop)}
        shortest_paths[self.id] = (0, self.id)

        while priority_queue:
            current_distance, current_node = heapq.heappop(priority_queue)

            if current_node in visited:
                continue

            visited.add(current_node)

            for (neighbor, cost) in self.graph[current_node]:
                if neighbor in self.graph:
                    distance = current_distance + cost
                    if distance < shortest_paths[neighbor][0]:
                        shortest_paths[neighbor] = (distance, current_node)
                        heapq.heappush(priority_queue, (distance, neighbor))

        return {node: (cost, next_hop) for node, (cost, next_hop) in shortest_paths.items()}

# Link class for network simulator
class Link:
    def __init__(self, src, dest, cost) -> None:
        self.src = src
        self.dest = dest
        self.cost = cost
        self.active = True  # active by default

# Router class for network simulator
class Router:
    def __init__(self, id) -> None:
        self.id = id
        self.links = {}  # {dest: Link}
        self.graph = Graph(id)
        self.next_hops = self.graph.dijkstra()  # initialize table of next hops
        self.seq_num = 1  # sequence number for LSA
        self.seq_num_table = {}  # {dest: seq_num}
        self.recv_buffer = []  # list of received control packets
        self.send_buffer = []  # list of control packets to send

    def add_link(self, dest, cost) -> None:
        if (dest != self.id):  # if not link to itself
            self.links[dest] = Link(self.id, dest, cost)
            self.seq_num_table[dest] = 0
            for node in self.graph.graph[self.id]:
                if node[0] == dest:
                    self.graph.graph[self.id].remove(node)  # remove as cost may have changed
                    break
            self.graph.graph[self.id].append((dest, cost))  # add link to graph
            self.next_hops = self.graph.dijkstra()  # update table of next hops

    def remove_link(self, dest) -> None:
        if dest in self.links:
            del self.links[dest]
            for node in self.graph.graph[self.id]:
                if node[0] == dest:
                    self.graph.graph[self.id].remove(node)  # remove link from graph
                    break
            self.next_hops = self.graph.dijkstra()  # update table of next hops

    def recv(self) -> None:
        for packet in self.recv_buffer:
            if packet.type == PacketType.DATA:
                # self.send_buffer.append(packet)
                continue  # not implemented yet
            elif packet.type == PacketType.CONTROL:
                # if unknown router or newer LSA
                if (packet.src not in self.links) or (packet.seq_num > self.seq_num_table[packet.src]):
                    self.seq_num_table[packet.src] = packet.seq_num
                    if (packet.src not in self.graph.graph) or (self.graph.graph[packet.src] != packet.payload):
                        self.graph.graph[packet.src] = packet.payload  # update src router's known neighbors
                        self.next_hops = self.graph.dijkstra()  # update table of next hops
        self.recv_buffer = []

    def send_LSA(self) -> None:
        for dest in self.links:
            neighbors = [(link.dest, link.cost) for link in self.links.values()]
            self.send_buffer.append(Packet(self.id, dest, PacketType.CONTROL, self.seq_num, neighbors))
        self.seq_num += 1

# Network class for network simulator
class Network:
    def __init__(self) -> None:
        self.routers = {}
    
    def add_router(self, id) -> None:
        self.routers[id] = Router(id)

    def add_router_and_links(self, id, links: [[int, float]]) -> None:
        self.add_router(id)
        for [dest, cost] in links:
            # add link from new router to existing router
            self.routers[id].add_link(dest, cost)
            # add link from existing router to new router
            self.routers[dest].add_link(id, cost)
    
    def remove_router(self, id) -> None:
        if id in self.routers:
            # delete all links to this router
            for router in self.routers:
                self.routers[router].remove_link(id)
            # delete router from network
            del self.routers[id]

    def add_link(self, a, b, cost) -> None:
        if (a in self.routers) and (b in self.routers):
            # add link from a to b and vice versa
            self.routers[a].add_link(b, cost)
            self.routers[b].add_link(a, cost)

    # remove link from a to b and vice versa
    def remove_link(self, a, b) -> None:
        if a in self.routers:
            self.routers[a].remove_link(b)
        if b in self.routers:
            self.routers[b].remove_link(a)

    def do_tick(self) -> None:
        # send and forward LSAs from each router
        for router in self.routers:
            self.routers[router].send_LSA()
            for packet in self.routers[router].send_buffer:
                self.routers[packet.dest].recv_buffer.append(packet)
                # log packet send
                print(f'LSA packet #{packet.seq_num} sent from {packet.src} to {packet.dest}: {packet.payload}')
            self.routers[router].send_buffer = []
        # receive LSA at each router
        for router in self.routers:
            self.routers[router].recv()
        # send data packets from each router
        # for router in self.routers:
        #     self.routers[router].send()
        # receive data packets at each router
        # for router in self.routers:
        #     self.routers[router].recv()
    
    def dump_network(self, outfile) -> None:
        # JSON dump of network
        with open(outfile, 'w') as f:
            routers_links = {router: [(link.dest, link.cost) for link in self.routers[router].links.values()] for router in self.routers}
            f.write(dumps(routers_links, indent=4))
