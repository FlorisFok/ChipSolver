
class Point(object):
    '''
    A point in the grid
    '''

    def __init__(self, location):
        self.location = location
        self.attribute = 'free'
        self.neighbours = []
        self.value = None
        self.g = 0
        self.parent = None

    def set_neighbour(self, neighbour):
        self.neighbours.append(neighbour)

    def get_neighbours(self):
        return self.neighbours

    def set_attribute(self, attribute):
        self.attribute = attribute

    def get_attribute(self):
        return self.attribute

    def set_value(self, tup_end, value_grid, current_point):
        tup_cur = self.location

        # Get distance values
        dis2end = threedimdistance(tup_cur, tup_end)
        dis2start = current_point.g + 1

        # Get coordinates
        x,y,z = tup_cur[0],tup_cur[1],tup_cur[2]

        # Adjust for value_grid
        value = (dis2end + dis2start)*float(value_grid[x][y][z])
        self.g = dis2start
        self.value = value

    def setG(self, g):
        self.g = g

    def __str__(self):
        return(f"This point is at location {self.location} and is " +
               f"{self.attribute} with {self.neighbours} as neighbours " +
               f"and has value {self.value}")

def threedimdistance( i, j):
    '''
    Get three dimesional distance
    '''
    deltaxsquared = abs(i[0] - j[0])
    deltaysquared = abs(i[1] - j[1])
    deltazsquared = abs(i[2] - j[2])
    return deltaxsquared + deltaysquared + deltazsquared
