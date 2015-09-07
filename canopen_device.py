''' canopen device class '''

class CanopenDevice:

    def __init__(self, node_id, parent_bus):
        self.node_id = node_id
        self.parent_bus = parent_bus
        self.device_type = None  # at first discovery time not yet known
        self.manufacturer = None # so not a sensible creation-time param
        self.name = name = None  # set those later once discovery works
        parent_bus.add_device(node_id, self)  # nb object reference, not name

    # string representation of an object:
    def __str__(self):
        s = "CanopenDevice "
        s += "node_id=%d " % self.node_id
        s += "name=%s " % self.name
        s += "parent=%s " % self.parent_bus.name
        s += "device type=%s " % self.device_type
        s += "manufacturer=%s "% self.manufacturer
        return s
