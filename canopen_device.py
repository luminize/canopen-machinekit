''' canopen device class '''
from candevice import CanDevice

# NMT states
# http://www.a-m-c.com/download/sw/dw300_3-0-3/CAN_Manual300_3-0-3.pdf p15 4.1
NMT_BOOTUP  = 0x00
NMT_PREOP   = 0x7f
NMT_OP      = 0x05
NMT_STOPPED = 0x04

nmt_states = {
    NMT_BOOTUP: 'BOOTUP',
    NMT_PREOP : 'PRE-OPERATIONAL',
    NMT_OP : 'OPERATIONAL',
    NMT_STOPPED : 'STOPPED'
}

MSG_NMT_START_REMOTE = 0x01
MSG_NMT_STOP_REMOTE  = 0x02
MSG_NMT_PRE_OP       = 0x80
MSG_NMT_RESET_NODE   = 0x81
MSG_NMT_RESET_COM    = 0x82

# a list of COB ID's shamelessly taken from
# https://github.com/CANopenNode/CANopenNode/blob/b7166438453beeab84b0e1cf569fa329cb69dd3a/CANopen.h#L67-L91
'''
        /**
        * Default CANopen identifiers.
        *
        * Default CANopen identifiers for CANopen communication objects. Same as
        * 11-bit addresses of CAN messages. These are default identifiers and
        * can be changed in CANopen. Especially PDO identifiers are confgured
        * in PDO linking phase of the CANopen network configuration.
        */
        typedef enum{
            CO_CAN_ID_NMT_SERVICE = 0x000, /**< 0x000, Network management */
            CO_CAN_ID_SYNC = 0x080, /**< 0x080, Synchronous message */
            CO_CAN_ID_EMERGENCY = 0x080, /**< 0x080, Emergency messages (+nodeID) */
            CO_CAN_ID_TIME_STAMP = 0x100, /**< 0x100, Time stamp message */
            CO_CAN_ID_TPDO_1 = 0x180, /**< 0x180, Default TPDO1 (+nodeID) */
            CO_CAN_ID_RPDO_1 = 0x200, /**< 0x200, Default RPDO1 (+nodeID) */
            CO_CAN_ID_TPDO_2 = 0x280, /**< 0x280, Default TPDO2 (+nodeID) */
            CO_CAN_ID_RPDO_2 = 0x300, /**< 0x300, Default RPDO2 (+nodeID) */
            CO_CAN_ID_TPDO_3 = 0x380, /**< 0x380, Default TPDO3 (+nodeID) */
            CO_CAN_ID_RPDO_3 = 0x400, /**< 0x400, Default RPDO3 (+nodeID) */
            CO_CAN_ID_TPDO_4 = 0x480, /**< 0x480, Default TPDO4 (+nodeID) */
            CO_CAN_ID_RPDO_4 = 0x500, /**< 0x500, Default RPDO5 (+nodeID) */
            CO_CAN_ID_TSDO = 0x580, /**< 0x580, SDO response from server (+nodeID) */
            CO_CAN_ID_RSDO = 0x600, /**< 0x600, SDO request from client (+nodeID) */
            CO_CAN_ID_HEARTBEAT = 0x700 /**< 0x700, Heartbeat message */
                            NMT error control, heartbeat and node guarding
        }CO_Default_CAN_ID_t;
'''


class CanopenDevice(CanDevice):

    def __init__(self, node_id, parent_bus):
        super(CanopenDevice, self).__init__(node_id, parent_bus)
        self.nmt_state = None # at startup unknown, determine from heartbeat
        self.device_type = None  # at first discovery time not yet known
        self.manufacturer = None # so not a sensible creation-time param
        self.name = name = None  # set those later once discovery works

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
        s += "state=%s " % nmt_states[self.state]
        s += "name=%s " % self.name
        s += "parent=%s " % self.parent_bus.ifname
        s += "device type=%s " % self.device_type
        s += "manufacturer=%s "% self.manufacturer
        return s
