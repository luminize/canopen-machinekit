''' canopen bus class '''

class CanopenBus:

    def __init__(self, name):
        self.name = name
        self.devices = dict() # node-id -> device object dict

    def add_device(self,node_id, device):
        self.devices[node_id] = device

    def displayname(self):
        print "name: ", self.name

    def num_devices(self):
        return len(self.devices.keys())

    def __str__(self):
        s = "CanopenBus: name=%s " % self.name
        return s
