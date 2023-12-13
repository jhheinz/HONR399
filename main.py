import os
import random
from graphs import *


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


def read_directory(path):
    files = os.listdir(path)
    file_dicts = []
    for file in files:
        print("reading file", file)
        filepath = path + "/" + file
        node_edge = get_counts(filepath)
        file_dicts.append((node_edge[0], node_edge[1], read_file(filepath)))
    return file_dicts

def get_counts(filename):
    infile = open(filename, "r")
    for line in infile:
        if line.startswith("#"):
            if "Edges:" in line:
                lst = line.split("\t")
                lst[1] = lst[1].rstrip("\n")
                vals = []
                for x in lst:
                    num = ""
                    for c in x:
                        if c.isdigit():
                            num = num + c
                    vals.append(num)
    infile.close()
    return vals
def fix_edge_weights(old_dict, new_dict):
    for node in new_dict.keys():
        for tup in new_dict[node]:
            try:
                for tup2 in old_dict[node]:
                    if tup2[0] == tup[0]:
                        # tuple does not support item assignment, change following line
                        tup[1] = tup2[1]
            except KeyError:
                pass


# read all 733 files into their own dict
list_of_dicts = read_directory("as-733")

graphs_list = []
for graph in list_of_dicts:
    x = graph[2]
    dv = DistanceVector(x)
    returns = dv.distance_vector()
    graphs_list.append((graph[0], graph[1], returns[0], returns[1], returns[2]))
# print to csv
# dict2 = read_file("as19971111.txt")
# fix_edge_weights(dict1, dict2)
# print(dict1)
