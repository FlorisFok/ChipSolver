import numpy as np
import random
import pandas as pd
import time
import sys

# File location
filename = r"data\options.xlsx"

# Get settings, this script must run when package is excecuted.
settings = sys.argv[2]
df = pd.read_excel(filename, sheet_name=0)
var = df.iloc[int(settings)]
var = [int(i) for i in var[:9]]

layer_coef = var[0]
NN_penalty = var[1]
layer_multiplier = [var[2],var[3],var[4],var[5],var[6]]#,var[7],var[8]]


def get_distance(matrix, points, p1, p2):
    '''
    distance matrix helper functon, gets the distance between two points
    '''
    ver = points.index(p1)
    hor = points.index(p2)
    return matrix[ver][hor]


def sort_points(starts, ends):
    '''
    A way of sorting the points, very easy and not thought out.
    '''
    # Make two indentical list, sort one and use the other for indexing
    distance = [abs(s[0]-e[0])+abs(s[1]-e[1]) for s,e in zip(starts,ends)]
    index = [abs(s[0]-e[0])+abs(s[1]-e[1]) for s,e in zip(starts,ends)]
    distance.sort()
    points_unsorted = list(zip(starts,ends))

    # Sort the starts and ends the same way as the distance, using the indexlist
    points = []
    for item in distance:
        i = index.index(item)
        points.append(points_unsorted[i])
        index[i] = -1

    # return the sorted points
    return points

def sort_points2(starts, ends):
    '''
    A way of sorting the points.
    Using the vertical, horizontal and the distance as a index of
    complexity, starting with the easiest points first
    '''
    # Make two indentical list, sort one and use the other for indexing
    def sorting(d):
        s = d[0]
        e = d[1]
        v = abs(s[0]-s[1])
        h = abs(e[0]-e[1])
        d = v+h
        return (v**2)*(h**2)*d

    points = list(zip(starts, ends))
    points.sort(key=sorting)
    # points.reverse()

    return points

def sort_points3(starts, ends, count_dict):
    '''
    A way of sorting the points, by the amount of points they need to connect with
    So most connected points first.
    '''
    # Make two indentical list, sort one and use the other for indexing
    def sortingdict(d):
        return d[1]

    points = list(zip(count_dict.keys(), count_dict.values()))
    points.sort(key=sortingdict)
    points.reverse()

    point_order = []
    point_rand = list(zip(starts,ends))
    point_rand += point_rand
    all_points = starts+ends

    for key, value in points:
        try:
            for v in range(value):
                i = all_points.index(key)
                point_order.append(point_rand[i])
                all_points[i] = 0
        except:
            pass

    def inOrder(list_of_T):
        '''
        Does the same as 'set()' but keeps order.
        '''
        new_list = []
        for i in list_of_T:
            if not i in new_list:
                new_list.append(i)
        return new_list

    return inOrder(point_order)


def sort_points_random(starts, ends):
    '''
    Randomly sorting points
    '''
    points_unsorted = list(zip(starts,ends))
    random.shuffle(points_unsorted)
    return points_unsorted

def first_value(size):
    '''
    Creates the first instance of the value grid
    Values are set, so it avoids the center
    '''
    # triple list comperhansion
    super_grid = [[[        1.00 + (abs(y-size[1]/2) + abs(x-size[1]/2)) * (1/size[1])
                            for z in range(size[2])]
                            for y in range(size[1])]
                            for x in range(size[0])]

    # Return a Numpy array (faster)
    super_matrix = np.array(super_grid)

    # layer bonus
    super_matrix *= np.array(layer_multiplier)
    return super_matrix

def second_value(size):
    '''
    Removes the values, and just declares it one everywere.
    '''
    # triple list comperhansion
    super_grid = [[[        1.00
                            for z in range(size[2])]
                            for y in range(size[1])]
                            for x in range(size[0])]

    # Return a Numpy array (faster)
    super_matrix = np.array(super_grid)

    return super_matrix

def update_layer(layer_info, value_grid):
    '''
    Update layers based on the info it got from the layer info
    '''
    # retrive the count dict
    empty = np.zeros(len(layer_info))

    # Calculate the occupiance of the layer
    for key in layer_info:
        layer_coverage = layer_info[key]['free']/255
        empty[key] = (1) + ((layer_coverage*layer_coef))

    # Matrix multiplication
    value_grid *= empty

    return value_grid

def edit_grid(grid, points, value_grid):
    '''
    Edit the value grid based on the points
    edits the values around the points and above
    '''
    # For every point
    for p in grid:
        p = grid[p]
        if p.location in points:

            # for every neighbour
            for N in p.neighbours:
                x,y,z = N.location
                value_grid[x][y][z] += NN_penalty ## changes to +


    return value_grid

def wire_NN_edit(grid, value_grid):
    '''
    Edit the values of the neighbours of the wires
    '''
    # for every point
    for p in grid:
        p = grid[p]

        # If it's a wire
        if p.attribute == 'wire':

            # Set all neighbours to 0.1
            for N in p.neighbours:
                x,y,z = N.location
                value_grid[x][y][z] += wire_penalty ## Changed to +++
    return value_grid
