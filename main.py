import random


def read_file(filename):
    infile = open(filename, "r")
    node_dict = {}
    for line in infile:
        if not line.startswith("#"):
            lst = line.split("\t")
            lst[1] = lst[1].rstrip("\n")
            if not lst[0] in node_dict.keys():
                node_dict[lst[0]] = []
            # need to update this line to check if edge already exists, if so use existing weight
            node_dict[lst[0]].append((lst[1], random.randrange(1, 100)))
    infile.close()
    return node_dict


dict1 = read_file("as19971110.txt")
print(dict1)



