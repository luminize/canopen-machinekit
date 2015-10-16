''' can device class '''


class CanDevice(object):

    def __init__(self, node_id, parent_bus):
        self.node_id = node_id
        self.parent_bus = parent_bus
        self.last_timestamp = None # last known timestamp
        parent_bus.add_device(node_id, self)  # nb object reference, not name

    def dispatch(self, msg):
        print("device %d: msg %s" % (self.node_id, msg))
        self.last_timestamp = msg.timestamp

    def timer(self):
        print("device %d: timeout" % (self.node_id))

    # string representation of a CanDevice object:
    def __str__(self):
        s = "CanDevice "
        s += "node_id=%d " % self.node_id
        s += "parent=%s " % self.parent_bus.ifname
        return s
