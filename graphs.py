def init():
    return 0
def init_dv(node_dict):
    tables = dict()
    for x in node_dict:
        tables[x] = dict()
        for y in node_dict:
            tables[x][y] = (float('inf'),-1)
        for end, weight in node_dict[x]:
            tables[x][x] = (weight, end)
    return tables
def distance_vector(node_dict, tables):
    count = 0
    changesC = 0
    for i in tables:
        for x in tables:
            prop = tables[x]
            for y, weight in node_dict[x]:
                xydist = prop[y][0]
                yval = tables[y]
                for z in prop:
                    if yval[z] > prop[z][0]+xydist:
                        tables[y][z] = (prop[z][0]+xydist, prop[z][1])
                        changesC+=1
                count+=1
    print("Update counter:", count)
    print("Changed value counter:", changesC)
    return tables
def remove_node_dv(node, tables):
    for x in tables:
        del tables[x][node]
    del tables[node]
    return tables
def add_node_dv(node_dict, node, tables):
    for x in tables:
        tables[x][node] = (float('inf'),-1)
    tables[node] = dict()
    for x in node_dict:
        tables[node][x] = (float('inf'),-1)
    for end, weight in node_dict[node]:
        tables[node][end] = (weight, end)
        tables[end][node] = (weight, node)
    return tables
def remove_link_dv(start, end, tables):
    tables[start][end] = (float('inf'),-1)
    tables[end][start] = (float('inf'),-1)
    return tables
def add_link_dv(start, end, tables, node_dict):
    for dest, weight in node_dict[start]:
        if (dest == end):
            if tables[start][end][0] > weight:
                tables[start][end] = (weight, end)
            break
    for dest, weight in node_dict[end]:
        if (dest == start):
            if tables[end][start][0] > weight:
                tables[end][start] = (weight, start)
            break
    return tables
def link_state():
    return 0
