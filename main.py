import os
import random
import csv
from threading import Thread
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
    i = 0
    for file in files:
        print("reading file", file)
        filepath = path + "/" + file
        node_edge = get_counts(filepath)
        file_dicts.append((node_edge[0], node_edge[1], read_file(filepath)))
        i+=1
        if i >= 50:
            break # capping at 50 files due to time
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
def distv(x, result, i):
    dv = DistanceVector(x)
    result[i] = dv.distance_vector()
# below is non-thread method
"""
# read all 733 files into their own dict
list_of_dicts = read_directory("as-733")

graphs_list = []
c = 0
for graph in list_of_dicts:
    x = graph[2]
    dv = DistanceVector(x)
    returns = dv.distance_vector()
    print(c,returns[0], returns[1], returns[2])
    graphs_list.append((graph[0], graph[1], returns[0], returns[1], returns[2]))
    c+=1
with open('dv_init.csv','w', newline='') as out:
    csv_out=csv.writer(out)
    for row in graphs_list:
        csv_out.writerow(row)"""
# threaded method with 2 threads.
list_of_dicts = read_directory("as-733")
graphs_list = []
results = [None] * 50
c = 0
for i in range(0, len(list_of_dicts),2):
    x = list_of_dicts[i][2]
    y = list_of_dicts[i+1][2]
    t1 = Thread(target=distv, args=(x, results, i))
    t1.start()
    t2 = Thread(target=distv, args=(y, results, i+1))
    t2.start()
    t1.join()
    print(c,results[i][0], results[i][1], results[i][2])
    c+=1
    t2.join()
    print(c,results[i+1][0], results[i+1][1], results[i+1][2])
    c+=1
# merge results with node and edge counts
for i in range(0, len(list_of_dicts),1):
    graphs_list.append((list_of_dicts[i][0], list_of_dicts[i][1], results[i][0], results[i][1], results[i][2]))
with open('dv_init.csv','w', newline='') as out:
    csv_out=csv.writer(out)
    for row in graphs_list:
        csv_out.writerow(row)

# print to csv
# dict2 = read_file("as19971111.txt")
# fix_edge_weights(dict1, dict2)
# print(dict1)
