from enum import Enum
from json import dumps
from main import read_file

class PriorityQEntry:
    def __init__(self, addr, cost, next_hop):
        self.addr = addr
        self.cost = cost
        self.next_hop = next_hop

    def __lt__(self, other):
        return (self.cost < other.cost)

    def __eq__(self, other):
        return (self.cost == other.cost)

class PacketType(Enum):
    DATA = 0
    CONTROL = 1

# Packet class for network simulator
class Packet:
    def __init__(self, src, dest, next, type: PacketType, seq_num, payload) -> None:
        self.src = src
        self.dest = dest
        self.next = next
        self.type = type
        self.seq_num = seq_num
        self.payload = payload

# Graph class for network simulator
class Graph:
    def __init__(self, id):
        self.id = id
        self.graph = {}  # {node: [(neighbor, cost)]}
        self.graph[id] = []
    
    def add_node(self, node):
        if node not in self.graph:
            self.graph[node] = []

    def add_edge(self, dest, cost):
        self.graph[self.id].append((dest, cost))
        self.graph[dest].append((self.id, cost))  # undirected graph

    def remove_edge(self, dest):
        for edge in self.graph[self.id]:
            if edge[0] == dest:
                self.graph[self.id].remove(edge)
                break

    def dijkstra(self):
        candidateQueue = []
        doneQueue = [PriorityQEntry(self.id, 0, self.id)]
        for node in self.graph[self.id]:
            candidateQueue.append(PriorityQEntry(node[0], node[1], node[0]))
        candidateQueue.sort(key=lambda x: x.cost)

        while len(candidateQueue) > 0:
            dst = candidateQueue.pop(0)
            doneQueue.append(dst)
            if not(dst.addr in self.graph.keys()):
                continue
            for node in self.graph[dst.addr]:
                found = False  # if node is already in doneQueue
                for e in doneQueue:
                    if e.addr == node[0]:
                        found = True
                        break
                if found:
                    continue
                newCost = dst.cost + node[1]

                found = False  # if node is in candidateQueue
                for e in candidateQueue:
                    if e.addr == node[0]:
                        found = True
                        if newCost < e.cost:
                            e.cost = newCost
                            e.next_hop = dst.next_hop
                        break
                if not found:
                    candidateQueue.append(PriorityQEntry(node[0], newCost, dst.next_hop))

                candidateQueue.sort(key=lambda x: x.cost)

        return {entry.addr: (entry.next_hop, entry.cost) for entry in doneQueue if entry.addr != self.id}

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
        self.next_hops = self.graph.dijkstra()  # initialize table of next hops {node: (next_hop, cost)}
        self.seq_num = 1  # sequence number for LSA
        self.seq_num_table = {}  # {dest: seq_num}
        self.recv_buffer = []  # list of received control packets
        self.send_buffer = []  # list of control packets to send
        self.updated_graph = False  # flag for if graph has changed
        self.lsas_sent = 0  # number of LSAs sent/forwarded

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

    def recv(self, do_dijkstra=True) -> None:
        self.updated_graph = False
        for packet in self.recv_buffer:
            if packet.type == PacketType.DATA:
                if (packet.dest == self.id):
                    packet.payload = packet.payload + f' -> {self.id}'
                    print(f"Data packet {packet.src} to {packet.dest} received @{self.id}!: {packet.payload}")
                else:
                    for dest in self.next_hops:
                        if dest == packet.dest:
                            packet.payload = packet.payload + f' -> {self.id}'
                            packet.next = self.next_hops[dest][0]
                            print(f"Data packet @{self.id} next_hop={packet.next} path so far: {packet.payload}")
                            self.send_buffer.append(packet)
            elif packet.type == PacketType.CONTROL:
                # if unknown router or newer LSA
                if (packet.src not in self.links) or (packet.seq_num > self.seq_num_table[packet.src]):
                    self.seq_num_table[packet.src] = packet.seq_num
                    if (packet.src not in self.graph.graph) or (self.graph.graph[packet.src] != packet.payload):
                        self.graph.graph[packet.src] = packet.payload  # update src router's known neighbors
                        # self.next_hops = self.graph.dijkstra()  # update table of next hops
                        self.updated_graph = True
                    for dest in self.links:  # forward LSA to all neighbors
                        packet.dest = dest  # update destination
                        packet.next = dest
                        self.send_buffer.append(packet)
                        self.lsas_sent += 1
        if self.updated_graph and do_dijkstra:
            self.next_hops = self.graph.dijkstra()  # run Dijkstra's on graph if graph changed
        self.recv_buffer = []

    def send_LSA(self) -> None:
        for dest in self.links:
            neighbors = [(link.dest, link.cost) for link in self.links.values()]
            self.send_buffer.append(Packet(self.id, dest, dest, PacketType.CONTROL, self.seq_num, neighbors))
            self.lsas_sent += 1
        self.seq_num += 1

    def send_data(self, dest) -> None:
        if dest in self.next_hops:
            print(f"Sending data packet from {self.id} to {dest}")
            self.send_buffer.append(Packet(self.id, dest, self.next_hops[dest][0], PacketType.DATA, 0, f'{self.id}'))

    def print_router(self) -> None:
        print(f'Router {self.id} STATE')
        print(f'Links: {[(link.dest, link.cost) for link in self.links.values()]}')
        print(f'Graph: {self.graph.graph}')
        print(f'Next hops: {self.next_hops}')

# Network class for network simulator
class Network:
    def __init__(self) -> None:
        self.routers = {}
        self.iteration = 0
        self.converged = False  # check after do_tick()
        self.packet_sent = False  # check after do_tick()

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
        # add routers if they don't exist
        if a not in self.routers:
            self.add_router(a)
        if b not in self.routers:
            self.add_router(b)
        # add link from a to b and vice versa
        self.routers[a].add_link(b, cost)
        self.routers[b].add_link(a, cost)

    # remove link from a to b and vice versa
    def remove_link(self, a, b) -> None:
        if a in self.routers:
            self.routers[a].remove_link(b)
        if b in self.routers:
            self.routers[b].remove_link(a)

    def do_tick(self, send_lsas=True, do_dijkstra=True) -> None:
        self.packet_sent = False
        # send and forward data/LSAs from each router
        for router in self.routers:
            if send_lsas:
                self.routers[router].send_LSA()
                self.packet_sent = True
            for packet in self.routers[router].send_buffer:
                self.routers[packet.next].recv_buffer.append(packet)
                self.packet_sent = True
                # log packet send
                # print(f'LSA packet #{packet.seq_num} sent from {packet.src} to {packet.dest}: {packet.payload}')
            self.routers[router].send_buffer = []
        self.converged = True
        # receive data/LSAs at each router
        for router in self.routers:
            self.routers[router].recv(do_dijkstra)
            if self.routers[router].updated_graph:
                self.converged = False
        self.iteration += 1
    
    def dump_network(self, outfile) -> None:
        # print metrics
        print(f'Network converged after {self.iteration} iterations with {sum([router.lsas_sent for router in self.routers.values()])} LSAs sent')
        # JSON dump of network
        with open(outfile, 'w') as f:
            routers_links = {router: [(link.dest, link.cost) for link in self.routers[router].links.values()] for router in self.routers}
            f.write(dumps(routers_links, indent=4))


def link_state_1():
    network = Network()
    # network.add_router_and_links(1, [[2, 1], [3, 1]])
    # network.add_router_and_links(2, [[1, 1], [3, 1]])
    # network.add_router_and_links(3, [[1, 1], [2, 1]])
    network.add_link(1, 2, 1)
    network.add_link(1, 3, 1)
    network.add_link(2, 3, 3)
    network.add_link(2, 4, 1)
    network.add_link(4, 5, 2)
    print("Iteration 1:")
    network.do_tick()
    network.routers[5].print_router()
    print("Iteration 2:")
    network.do_tick()
    network.routers[5].print_router()
    print("Iteration 3:")
    network.do_tick()
    network.routers[5].print_router()
    print("Iteration 4:")
    network.do_tick()
    network.routers[5].print_router()
    network.routers[5].send_data(3)
    network.do_tick()
    network.do_tick()
    network.do_tick()
    network.do_tick()
    network.dump_network("ls_test.json")

    return 0

def link_state_2():
    network = Network()
    network.add_link(1, 2, 1)
    network.add_link(1, 3, 1)
    network.add_link(2, 3, 3)
    network.add_link(2, 4, 1)
    network.add_link(4, 5, 2)
    while not network.converged:
        network.do_tick()
    network.dump_network("ls_test.json")

    return 0

def link_state_snap():
    node_dict = read_file("as19971110.txt")
    network = Network()
    for router in node_dict:
        network.add_router(router)
        for link in node_dict[router]:
            if link[0] != router:  # don't add links to self
                network.add_link(router, link[0], link[1])
    network.do_tick(send_lsas=True)
    # while not network.converged:
    for i in range(10):
        network.do_tick(send_lsas=False)
        print(f'Iteration {network.iteration} complete')
        network.dump_network(f'ls_snap_{network.iteration}.json')
    print(f'Network converged after {network.iteration} iterations with {sum([router.lsas_sent for router in network.routers.values()])} LSAs sent')

    return 0

def link_state_lsa_data():
    node_dict = read_file("as19971110.txt")
    network = Network()
    for router in node_dict:
        network.add_router(router)
        for link in node_dict[router]:
            if link[0] != router:  # don't add links to self
                network.add_link(router, link[0], link[1])
    network.do_tick(send_lsas=True, do_dijkstra=False)
    print(f'Iteration {network.iteration} complete with {sum([router.lsas_sent for router in network.routers.values()])} LSAs sent')
    while network.packet_sent:  # while there are still LSAs to be sent/forwarded
        network.do_tick(send_lsas=False, do_dijkstra=False)
        print(f'Iteration {network.iteration} complete with {sum([router.lsas_sent for router in network.routers.values()])} LSAs sent')
    print(f'No packets forwarded after {network.iteration} iterations with {sum([router.lsas_sent for router in network.routers.values()])} LSAs sent')
