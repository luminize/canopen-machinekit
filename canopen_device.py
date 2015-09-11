''' canopen device class '''

# NMT states
# http://www.a-m-c.com/download/sw/dw300_3-0-3/CAN_Manual300_3-0-3.pdf p15 4.1
NMT_BOOTUP  = 0x00
NMT_PREOP   = 0x7f
NMT_OP      = 0x05
NMT_STOPPED = 0x04

MSG_NMT_START_REMOTE = 0x01
MSG_NMT_STOP_REMOTE  = 0x02
MSG_NMT_PRE_OP       = 0x80
MSG_NMT_RESET_NODE   = 0x81
MSG_NMT_RESET_COM    = 0x82

class CanopenDevice:

    def __init__(self, node_id, parent_bus):
        self.node_id = node_id
        # fill states dictionary
        self.states = dict()
        self.states[NMT_BOOTUP] = 'BOOTUP'
        self.states[NMT_PREOP] = 'PRE-OPERATIONAL'
        self.states[NMT_PREOP] = 'PRE-OPERATIONAL'
        self.states[NMT_OP] = 'OPERATIONAL'
        self.states[NMT_STOPPED] = 'STOPPED'
        self.state = None # at startup unknown, determine from heartbeat
        self.parent_bus = parent_bus
        self.device_type = None  # at first discovery time not yet known
        self.manufacturer = None # so not a sensible creation-time param
        self.name = name = None  # set those later once discovery works
        self.last_timestamp = None # last known timestamp
        parent_bus.add_device(node_id, self)  # nb object reference, not name
        #print "init node %d on bus %s" % ((self.node_id), self.parent_bus.ifname)

    def process(self, msg):
        #print "device %d: msg %s" % (self.node_id, msg)
        self.last_timestamp = msg.timestamp
        #print "device %d last known timestamp %f:" % (self.node_id, \
        #                                               self.last_timestamp)
        node_id = msg.arbitration_id & ~0x780
        print "process node_%d msg.arbitration_id & 0x700 = msg %s" % (self.node_id, msg)
        if msg.arbitration_id & 0x700:
            # https://en.wikipedia.org/wiki/CANopen#Network_management_.28NMT.29_protocols
            # a heartbeat message, mirror the state of the hardware
            # check that there is only 1 byte
            if msg.dlc == 1 :
                print "heartbeat with %d byte" % msg.dlc
                msg_data = msg.data[0]
                #print "msg_data: %.8x" % msg_data
                if msg_data == NMT_BOOTUP:
                    self.state = NMT_BOOTUP
                if msg_data == NMT_PREOP:
                    self.state = NMT_PREOP
                if msg_data == NMT_OP:
                    self.state = NMT_OP
                if msg_data == NMT_STOPPED:
                    self.state = NMT_STOPPED
            else:
                print "heartbeat with %d bytes, while expectin 1 byte" % msg.dlc
            '''
            # fire off a 'switch to operational' nmt cmd
            self.state = NMT_OP
            #print "node %d switch to %d" % (node_id, self.state)
            self.parent_bus.send_nmt( node_id, MSG_NMT_START_REMOTE) # switch to operational
            '''
    def timeout(self):
        pass
        #print "device %d: timeout" % (self.node_id)

    # string representation of an object:
    def __str__(self):
        s = "CanopenDevice "
        s += "node_id=%d " % self.node_id
        s += "state=%d " % self.state
        s += "states=%d " % self.states
        s += "name=%s " % self.name
        s += "parent=%s " % self.parent_bus.ifname
        s += "device type=%s " % self.device_type
        s += "manufacturer=%s "% self.manufacturer
        return s
