def init():
    return 0
def distance_vector():
    tables = dict()
    for x in node_dict:
        tables[x] = []
        for i in range(len(node_dict)):
            row = []
            for j in range(len(node_dict)):
                row.append(-1)
            tables[x].append(row)
        for end, weight in node_dict[x]:
            tables[x][x][end] = weight
    for x in tables:
        prop = tables[x]
        for y, weight in node_dict[x]:
            xydist = prop[x][y]
            tables[y][x] = prop[x] # need to copy all non-self rows
            yval = tables[y][y]
            tables[y] = prop
            propval = prop[x]
            for z in propval:
                z += xydist
            for i,z in enumerate(propval):
                if yval[i] < z:
                    tables[y][y][i] = yval[i]
                else:
                    tables[y][y][i] = z
    return tables
def remove_node_dv(node, tables):
    temp = tables[node]
    del tables[node]
def link_state():
    return 0
