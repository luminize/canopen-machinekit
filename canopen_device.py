''' canopen device class '''

# NMT states
# http://www.a-m-c.com/download/sw/dw300_3-0-3/CAN_Manual300_3-0-3.pdf p15 4.1
NMT_BOOTUP = 0
NMT_PREOP = 1
NMT_OP = 2
NMT_STOPPED = 3


class CanopenDevice:

    def __init__(self, node_id, parent_bus):
        self.node_id = node_id
        self.state = NMT_BOOTUP
        self.parent_bus = parent_bus
        self.device_type = None  # at first discovery time not yet known
        self.manufacturer = None # so not a sensible creation-time param
        self.name = name = None  # set those later once discovery works
        parent_bus.add_device(node_id, self)  # nb object reference, not name

    def process(self, msg):
        print "device %d: msg %s" % (self.node_id, msg)
        if msg.arbitration_id & 0x700:
            # a bootup message, switch to preop
            self.state = NMT_PREOP
            print "node %d state=preop" % (msg.arbitration_id & ~0x700)

    def timeout(self):
         print "device %d: timeout" % (self.node_id)

    # string representation of an object:
    def __str__(self):
        s = "CanopenDevice "
        s += "node_id=%d " % self.node_id
        s += "name=%s " % self.name
        s += "parent=%s " % self.parent_bus.name
        s += "device type=%s " % self.device_type
        s += "manufacturer=%s "% self.manufacturer
        return s


