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
            node_exists = False
            idx = 0
            try:
                for tup in node_dict[lst[1]]:
                    try:
                        tup.index(lst[0])
                        node_exists = True
                        break
                    except ValueError:
                        idx += 1
            except KeyError:
                pass
            if node_exists:
                node_dict[lst[0]].append((lst[1], node_dict[lst[1]][idx][1]))
            else:
                node_dict[lst[0]].append((lst[1], random.randrange(1, 100)))
    infile.close()
    return node_dict


dict1 = read_file("as19971110.txt")
print(dict1)

