import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import colors
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as animation

from scripts.point import Point
from scripts.extra import *
from scripts.wire import Wire
from scripts.settings import *


class Grid(object):
    '''
    The grid for the gates and wires to connect
    '''
    def __init__(self, size, points):
        '''
        Initialize the variables
        '''
        #  Basic variables
        self.size = size
        self.points = points
        self.grid = self.make_grid()
        self.MAX_TRIES = size[0]*size[1]*size[2]

        # Some deeper charataristics of the grid
        self.make_neighbours()
        self.set_points()
        # self.matrix = self.distance_matrix()

        # Add some logic to the grid
        self.value_grid = first_value(size)
        self.edit_grid()

    def make_grid(self):
        '''
        Make the 3D grid in the demensions given at __init__
        '''
        size = self.size
        grid = {}
        # X by Y by layers
        for i in range(size[0]):
            for j in range(size[1]):
                for k in range(size[2]):
                    grid[(i,j,k)] = Point((i,j,k))
        return grid

    def make_neighbours(self):
        '''
        Set the neighbours of the points
        '''
        # Make neighbours
        for x,y,z in self.grid:
            point = self.grid[(x,y,z)]
            # Choose all the 1 offset points, 6 sides, 6 get_neighbours
            # Tries are nessecarry if you're at the border
            try:
                point.set_neighbour(self.grid[(x+1,y,z)])
            except:
                pass
            try:
                point.set_neighbour(self.grid[(x-1,y,z)])
            except:
                pass
            try:
                point.set_neighbour(self.grid[(x,y+1,z)])
            except:
                pass
            try:
                point.set_neighbour(self.grid[(x,y-1,z)])
            except:
                pass
            try:
                point.set_neighbour(self.grid[(x,y,z-1)])
            except:
                pass
            try:
                point.set_neighbour(self.grid[(x,y,z+1)])
            except:
                pass

    def set_points(self):
        '''
        Set the given points in the grid, using the attribute of the points
        '''
        # Count and set points
        count = 0
        for point in self.grid:
            point = self.grid[point]
            if point.location in self.points:
                count+=1
                point.set_attribute('point')


    def Astar(self, start, end):
        '''
        Astar
        '''
        # Set key attributes and start point
        closedl = []
        openl = []

        self.grid[start].set_attribute('closed')
        self.grid[end].set_attribute('end')
        current_point  = self.grid[start]

        # Set temp memory variables
        found = False
        parent = {}
        tries = 0

        def takeValue(elem):
            return elem.value
        def takeG(elem):
            return elem.g

        # Continue until found
        while not found:
            # Check for each neighbour if end is there, or is free.
            for N in current_point.get_neighbours():
                # when end is there: "You found the line"
                if N.attribute == 'end':
                    parent[N.location] = current_point.location
                    found = True

                # When open is there: "Possible next move"
                elif N.attribute == "free":
                    N.set_value(end, self.value_grid, current_point)
                    parent[N.location] = current_point.location
                    N.set_attribute('open')
                    openl.append(N)


            # Sereach all the open points for the lowest point,
            # this will be the next move

            openl.sort(key=takeValue)
            lowest_point_list = [i for i in openl if i.value == openl[0].value]

            lowest_point_list.sort(key=takeG)
            # When there are no open points, give error (impossiple area)
            try:
                lowest_point = lowest_point_list[0]
                lowest_point.set_attribute('closed')
                openl.pop(0)
                current_point = lowest_point
            except:
                found = True
                parent = {}

            tries += 1
            if tries > self.MAX_TRIES:
                found = True
                parent = {}

        # Reset the 'open' and 'closed' attributes to free. (clear memory)
        for P in self.grid.values():
            if P.attribute == 'open' or P.attribute == 'closed' or P.attribute == 'end':
                P.set_attribute('free')
                P.g = 0

        # The parent contains the backtrace, which is needed to create the wire
        return parent


    def make_wire(self, start, end, parent):
        '''
        Goining in reverse, we are looking for the start from the end.
        This will give us the garanteed shortest route between the two.
        '''
        cur = self.grid[end].location
        wire = []

        while cur!= start:
            # Add the coordinates to the wire list and set attribute to wire
            wire.append(cur)
            self.grid[cur].set_attribute('wire')
            cur = parent[cur]

        # If end is found, add the end (here: 'start' -> reversed).
        wire.append(cur)
        self.grid[cur].set_attribute('wire')

        # Return the wire
        return wire

    def plot_wire(self, wires):
        '''
        Plot the wires and points
        '''
        # Set figure and 3D plot
        fig = plt.figure(figsize=(self.size[0],self.size[2]))
        ax = fig.add_subplot(111, projection='3d')

        colors= ['b','g','r','c','m','y', 'k']


        # Extract data and plot small lines
        for i, l in enumerate([i.route for i in wires]):
            linex,liney, linez = zip(*l)
            ax.plot(linex, liney,linez, linewidth=5, color=colors[i%len(colors)])

        # Plot the points
        px, py, pz = zip(*self.points)
        ax.scatter(px, py, pz, linewidth=10, color='red')
        ax.set_zlim(0,7)

        # draw gridlines
        plt.xticks(range(self.size[0]))
        plt.yticks(range(self.size[1]))
#         ax.zticks(range(size[2])) # Doesnt work for some reason...
        plt.grid(which='major', axis='both', linestyle='-', color='k', linewidth=2)

        # Show all
        plt.show()

    def layer_info(self):
        '''
        Retrive info over the layers, which can be used to calculate new values
        output: {'layer(int)':{'attribute(str)': count(int)}}
        '''
        count_dict = {}
        # For all points
        for point in self.grid:
            point = self.grid[point]
            # If layer is allready in dict
            if point.location[-1] in count_dict:
                # If attribute is already in dict
                if point.attribute in count_dict[point.location[-1]]:
                    # Count
                    count_dict[point.location[-1]][point.attribute] += 1
                else:
                    # Set attribute
                    count_dict[point.location[-1]][point.attribute] = 1
            else:
                # Set layer
                count_dict[point.location[-1]] = {point.attribute:1}
        return count_dict

    def remove_wire(self, wire):
        '''

        '''
        start, end = wire.start, wire.end
        for pos in wire.route:
            self.grid[pos].set_attribute('free')

        return (start, end)

    def add_wire(self, wire):
        for pos in wire.route:
            self.grid[pos].set_attribute('wire')

        return (wire.start, wire.end)

    def distance_matrix(self):
        points = []
        for i in range(self.size[0]):
            for j in range(self.size[1]):
                for k in range(self.size[2]):
                    points.append((i,j,k))

        self.plane_points = points
        matrix = []
        for vertical in points:
            line = []
            for horizontal in points:
                line.append(round(threedimdistance(vertical, horizontal),1))
            matrix.append(line)
        return matrix


    ################################################## CLever ################
    def update_layer(self):
        '''
        Update layers based on the info it got from the layer info
        '''
        self.value_grid = update_layer(self.layer_info(), self.value_grid)

    def edit_grid(self):
        '''
        Edit the value grid based on the points
        edits the values around the points and above
        '''
        self.value_grid = edit_grid(self.grid, self.points, self.value_grid)

    def wire_NN_edit(self):
        '''
        Edit the values of the neighbours of the wires
        '''
        self.value_grid = wire_NN_edit(self.grid, self.value_grid)

    ################################################## end CLever #############
    ''' Re-write the value updaters as a fucntion of a point, so that just a
    single loop is nessecarry for the edditing of the point_values (faster) '''

    ##########################################################################3
