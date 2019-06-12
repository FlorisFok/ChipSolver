class Instance( ):

    def __init__(self, mainGrid, wires = []):
        self.main = mainGrid
        self.wires = wires
        self.connected = []
        self.not_connected = []
        self.add_wires()
        self.t = 1
        self.swap = 5

    def start(self, vars):
        self.wires = vars[0]
        self.not_connected = vars[1]

    def add_wires(self):
        for w in self.wires:
            self.main.add_wire(w)

    def run(self):
        return self.wires, self.not_connected

    def score1(self):
        return int(len(self.wires))

    def score2(self):
        try:
            return int(sum([i.length for i in self.wires]))
        except:
            0

    def swires(self, wires):
        self.wires = wires

    def gwires(self):
        return self.wires

    def snotc(self, nc):
        self.not_connected = nc

    def gnotc(self):
        return self.not_connected
