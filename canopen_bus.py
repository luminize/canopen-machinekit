''' canopen bus class '''

class canopen_bus:
    buscount = 0
    devices = []
    ''' devices.append() will add a new device to this list '''

    def __init__(self, name):
        self.name = name
        canopen_bus.buscount += 1

    def add_device(self,devicename):
        self.devices.append(devicename)

    def displaycount(self):
        print "number of busses: %d" % canopen_bus.buscount

    def displayname(self):
        print "name: ", self.name
