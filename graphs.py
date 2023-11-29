def init():
    return 0
def init_dv():
    tables = dict()
    for x in node_dict:
        tables[x] = dict()
        for y in node_dict:
            tables[x][y] = dict()
            for z in node_dict:
                tables[x][y][z] = float('inf')
        for end, weight in node_dict[x]:
            tables[x][x][end] = weight
def distance_vector(tables):
    for x in tables:
        prop = tables[x]
        for y, weight in node_dict[x]:
            xydist = prop[x][y]
            yval = tables[y][y]
            tables[y] = prop
            propval = prop[x]
            for z in propval:
                z += xydist
            for z in prop:
                if yval[z] < propval[z]:
                    tables[y][y][z] = yval[z]
                else:
                    tables[y][y][z] = propval[z]
    return tables
def remove_node_dv(node, tables):
    for x in tables:
        del tables[x][node]
        for y in tables[x]:
            del y[node]
    del tables[node]
def add_node_dv(node, tables):
    for x in tables:
        for y in tables[x]:
            tables[x][y][node] = float('inf')
            tables[x][node][y] = float('inf')
    tables[node] = dict()
    for x in node_dict:
        tables[node][x] = dict()
        for y in node_dict:
            tables[node][x][y] = float('inf')
    for end,weight in node_dict[node]:
        tables[node][node][end] = weight
        tables[end][end][node] = weight
def link_state():
    return 0
