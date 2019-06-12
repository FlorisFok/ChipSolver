from scripts.point import Point
from scripts.wire import Wire
from scripts.instance import Instance
from scripts import grid
from scripts.settings import second_value
import matplotlib.pyplot as plt

import random
import numpy as np
import pandas as pd
import sys
import time
import math
import numpy
import pickle
import time
import datetime

option_file = r"data\options.xlsx"

def make_fig(data, netlist_number, test, Wires):
    '''
    Make a double plot of the scores and save the data (Wires and scores)
    '''
    # Extract data
    y = range(len(data))
    w = [i[0] for i in data]
    c = [i[1]for i in data]

    # MAke time stamp
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y%m%d_%H%M')

    # Dump pickles
    pickle.dump(data,
                open( f"data\\pre_made_wires\\{netlist_number[0]}\\data{netlist_number}_{test}_{len(data)}T{st}.p", "wb" ))
    # pickle.dump(Wires,
    #             open( f"data\\pre_made_wires\\{netlist_number[0]}\\wire{netlist_number}_{test}_{len(data)}T{st}.p", "wb" ))

    # plot double axis plot
    fig, ax1 = plt.subplots()
    ax1.plot(y, w, color='b')
    # Create equal high plots for comperhansion results ## temporary
    ax1.set_ylim([700, 1200])
    ax1.set_xlabel('Iterations')
    ax1.set_ylabel('Total length', color='b')
    ax1.tick_params('y', colors='b')
    ax2 = ax1.twinx()
    ax2.plot(y, c, color='r')
    ax2.set_ylabel('Total connected', color='r')
    ax2.tick_params('y', colors='r')
    ax2.set_title("The "+str(test)+" algorithm")
    fig.tight_layout()


    # Save the figure
    plt.savefig(f'generated_figs\\fig_of_{netlist_number}_{test}_{st}.png')
    print("saved")

def Check(wires):
    '''
    Checks if the wires aren't crossing. Very useful during testing
    '''
    all = []
    pointss = []

    # get all wire/point pieces
    for i in wires:
        all += i.route
        pointss.append(i.start)
        pointss.append(i.end)

    all_wire = []
    # For all wires that are not in points, append
    for a in all:
        if not a in pointss:
            all_wire.append(a)

    # Check if there are overlapping locations in the wires
    return (len(all_wire) == len(set(all_wire)))

def make_avg_data(avg_data):
    '''
    Takes list of list and calculates the average across the list
    '''
    dl = len(avg_data)

    # Adjusts on the
    data = [(
            (sum([avg_data[j][i][0] for j in range(dl)]))/dl,
            (sum([avg_data[j][i][1] for j in range(dl)]))/dl
            )
            for i in range(len(avg_data[0]))]
    return data

def get_options(settings):
    '''
    Get the options values from the excel sheet
    '''
    # Read file
    df = pd.read_excel(option_file, sheet_name=0)
    var = df.iloc[int(settings)]

    # Assign the column name to the value in a option dict
    options = {}
    for key in list(df):
        options[key] = df.iloc[int(settings)][list(df).index(key)]

    return options

def shuffle(items):
    '''
    Shuffle wires without shuffling the original list
    ~ improvement nessecarry ~
    '''
    r = [random.randint(0,1) for i in range(len(items))]
    # Random order
    items1 = [items[n]  for n, i in enumerate(r) if i == 1]
    items2 = [items[n]  for n, i in enumerate(r) if i == 0]
    return items1+items2

def update_temperature(T, delta_t):
    '''
    Temprature update fucntion
    linear and exponetial
    '''
    # return T - delta_t
    return T * delta_t

def sortit(i):
    return i.score1()

def shortestit(i):
    return i.score2()

def best_wire(w):
    return sum([i.length for i in w])

def acceptance_probability(old_cost, new_cost, temperature):
    '''
    Probability function for Simulated annealing.
    Always accept improvement
    '''
    if new_cost < old_cost:
        return 2.0
    else:
        return math.exp((old_cost - new_cost) / temperature)

def get_wires(mainGrid, points_to_connect):
    '''
    Lay wires down
    '''
    # Start the loop for all the wires
    wires = []
    connected = 0
    not_connected = []

    # For every unconnected pair of points, try to connect them
    for start,end in points_to_connect:
        # find line, else return empty dict
        parent = mainGrid.Astar(start, end)
        if parent == {}:
            not_connected.append((start, end))
            pass
        else:
            # Retrace the line and laydown the wire
            wire = mainGrid.make_wire(start, end, parent)
            con_wire = Wire(start, end, wire)
            wires.append(con_wire)
            connected += 1

    return wires, connected, not_connected

def swap_wires(wires, not_connected, mainGrid, swaps):
    '''
    swaps wires based on simply improvement, greedy
    '''
    # get wire lenght and not connected count
    len_list1 = sum([i.length for i in wires]) ##
    len1 = len(not_connected)

    # fresh variables
    popped_wires = []
    old_wires = [i for i in wires]

    # for a few wires: remove them from the grid
    for wire in old_wires[:swaps]:
        coords = mainGrid.remove_wire(wire)
        popped_wires.append(wires.pop(wires.index(wire)))
        not_connected.append(coords)

    # Try to connect the wires removed and the pairs not connected
    wires2, connected, not_connected = get_wires(mainGrid, not_connected)
    len2 = len(not_connected)

    len_list2 = sum([i.length for i in wires2 + wires]) ##

    # Check for inprovement in wires connected
    if len1 > len2: ##
        wires3 = wires2 + wires ##
        return mainGrid, wires3, not_connected ##

    # Check for inprovement in lenght if all wires are connected
    elif len1 == len2 and len_list2 < len_list1: ##
        wires3 = wires2 + wires ##
        return mainGrid, wires3, not_connected ##
    # else, reverse everything
    else:
        # Remove the new wires
        for w in wires2:
            not_connected.append(mainGrid.remove_wire(w))
        # Add the old removed wires
        for w in popped_wires:
            not_connected.pop(not_connected.index(mainGrid.add_wire(w)))
        # Re create the wires list
        wires3 = popped_wires + wires
        return mainGrid, wires3, not_connected



def make_new_gen(X, GENS, swap_count, SIZE, all_points):
    '''
    Make new generations for x gens.
    '''
    generations = [Instance(grid.Grid(SIZE, all_points)) for n in range(GENS)]
    # print(GENS, swap_count)
    for geni in generations:
        # This copies the class
        geni.snotc([i for i in X.not_connected])
        new_wire = []
        for i,w in enumerate(X.wires):
            new_wire.append(Wire(w.start, w.end, w.route))
            geni.main.add_wire(new_wire[i])
        geni.swires(new_wire)
        geni.swap = swap_count

        # Reset the grid
        geni.main.value_grid = second_value(SIZE)

    return generations

def load_gen(gen, name, excel_data):
    '''
    Load generation from pickle file
    '''
    wires = pickle.load( open( name, "rb" ) )
    not_connected  = excel_data
    gen.snotc([i for i in not_connected])
    new_wire = []
    for i,w in enumerate(wires):
        new_wire.append(Wire(w.start, w.end, w.route))
        gen.main.add_wire(new_wire[i])
    gen.swires(new_wire)
    return gen

def loading(i, total):
    print(f"{round(i/total*100)}%", end='\r')


def swap_wires_prop(wires, not_connected, mainGrid, swaps, t):
    '''
    Swapping with probability fucntions
    '''
    len1 = len(not_connected)
    len_list = sum([i.length for i in wires]) ##
    popped_wires = []
    old_wires = [i for i in wires]

    for wire in old_wires[:swaps]:
        coords = mainGrid.remove_wire(wire)
        popped_wires.append(wires.pop(wires.index(wire)))
        not_connected.append(coords)

    wires2, connected, not_connected2 = get_wires(mainGrid, not_connected)
    len2 = len(not_connected2)

    prop = acceptance_probability(len1, len2, t)
    len_list2 = sum([i.length for i in wires2 + wires]) ##
    prop2 = acceptance_probability(len_list, len_list2, t) ##


    # If wire inprovement
    # if (prop > random.random()):
    if len1 >= len2:
        # wires3 = wires2 + wires
        # return mainGrid, wires3, not_connected2
        # If lenght improvement on same wire
        if prop2 > random.random():
            wires3 = wires2 + wires
            return mainGrid, wires3, not_connected2
        # # If wire is not same
        # elif prop == 2.0:
        #     wires3 = wires2 + wires
        #     return mainGrid, wires3, not_connected2

    for w in wires2:
        not_connected2.append(mainGrid.remove_wire(w))

    for w in popped_wires:
        not_connected2.pop(not_connected2.index(mainGrid.add_wire(w)))

    wires3 = popped_wires + wires
    return mainGrid, wires3, not_connected2

def sortbothvalue(g):
    num = g.score1()
    dec = int((2000 - g.score2())*0.5)
    return float(f'{num}.{dec}')

def bothvalue(w_l, num):
    dec = int((2000 - w_l)*0.5)
    return float(f'{num}.{dec}')

def cal_fitness(ma, mi, g_class):
    f = ((ma-sortbothvalue(g_class))/(ma-mi))
    f = 1 - f
    return 0.5*(numpy.tanh((4*f)-2)+1)

def repo_s(score):
    # More generations for bad solutions, stops homogene field
    return int(numpy.ceil(5*score*random.random()))

def swap_s(score, MAX):
    d = ((1-score)*random.random()*MAX)
    return int(numpy.ceil(d))

def swap_wires_plant(wires, not_connected, mainGrid, swaps):
    '''
    swaps wires always return result
    '''
    # fresh variables
    popped_wires = []
    old_wires = [i for i in wires]

    # for a few wires: remove them from the grid
    for wire in old_wires[:swaps]:
        coords = mainGrid.remove_wire(wire)
        popped_wires.append(wires.pop(wires.index(wire)))
        not_connected.append(coords)

    # Try to connect the wires removed and the pairs not connected
    wires2, connected, not_connected = get_wires(mainGrid, not_connected)


    wires3 = wires2 + wires
    return mainGrid, wires3, not_connected


def make_random_points(size, resolution, number=-1):
    '''
    FOR TESTING, make some random points
    can be used to find optimal values
    '''
    points = []
    # Make random points
    for i in range(0,size[0],resolution):
        for j in range(0,size[1],resolution):
            points.append((i,j,0))

    # Remove uneven points
    if len(points) % 2 != 0:
        points = points[:-1]

    # shuffle, cut and divide in start en end
    random.shuffle(points)
    points = points[:number]
    ends = points[int(len(points)/2):]
    starts = points[:int(len(points)/2)]

    return starts, ends

def length_score(data_file, wires, percentile, not_connected,
                 cal_time, net_number, points_to_connect):
    '''
    Nice way to "SCORE" and save our result
    '''
    # Retrive data
    len_list = [i.length for i in wires]
    minlen_list = [abs(i.start[0] - i.end[0]) +
                   abs(i.start[1] - i.end[1])
                   for i in wires]

    # Stats
    data = {'netlist':net_number}
    data['total_connected'] = percentile
    data['true_len'] = sum(len_list)
    data['longest'] = max(len_list)
    data['shortest'] = min(len_list)
    data['mean'] = data['true_len'] / len(len_list)
    data['q25'] = len_list[int(len(len_list)/4)]
    data['q75'] = len_list[-int(len(len_list)/4)]
    data['cal_time'] = cal_time
    data['len_percentile'] = sum(len_list)/sum(minlen_list)
    data['starting order'] = str(points_to_connect)
    data['ending order'] = str(not_connected)
    df = pd.read_excel(option_file, sheet_name=0)
    settings = sys.argv[2]
    var = df.iloc[int(settings)]
    data['options'] = str(list(var))
    data['option_num'] = int(settings)

    print(f'\nThe score was: {percentile}')
    print(f'The len was: {sum(len_list)}')
    output(data_file, data)
    print(f'Data is saved in {data_file}\n')
    return percentile

def make_imported_points(points, netlist):
    start_index, end_index = zip(*netlist)
    starts = [(points[i][0],points[i][1],0) for i in start_index]
    ends = [(points[i][0],points[i][1],0) for i in end_index]

    count_dict = {}
    for i in ends+starts:
        if i in count_dict:
            count_dict[i] +=1
        else:
            count_dict[i] = 1

    return ends, starts, count_dict

def output(filename, data):
    df = pd.read_excel(filename, sheet_name=0)
    data['time'] = str(time.localtime())
    df_new = pd.DataFrame(data, index = [1])
    df_file = df.append(df_new, ignore_index=True, sort=False)
    df_file.to_excel(filename)
