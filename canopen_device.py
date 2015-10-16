''' canopen device class '''
from socketcan import CanBus,CanFrame,SDODownloadExp
from candevice import CanDevice
import time

# NMT states
# http://www.a-m-c.com/download/sw/dw300_3-0-3/CAN_Manual300_3-0-3.pdf p15 4.1
NMT_UNKNOWN = 0xff
NMT_BOOTUP  = 0x00
NMT_PREOP   = 0x7f
NMT_OP      = 0x05
NMT_STOPPED = 0x04

nmt_states = {
    NMT_UNKNOWN: 'UNKNOWN',
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

# COB id's in this device
TPDO_1 = 0x180
TPDO_2 = 0x280
TPDO_3 = 0x380
TPDO_4 = 0x480

# where are the TPDO parameters located in the device? should be set-up
# by the integrator because this can differ per device and setup.
# for now hard-coded, but should be done via an xml file (EDS file) which is
# device specific. Over all this is ready for improvement.
tpdo_mapping_registers = {
    TPDO_1: 0x1A00,
    TPDO_2: 0x1A01,
    TPDO_3: 0x1A02,
    TPDO_4: 0x1A03
}

RPDO_1 = 0x200
RPDO_2 = 0x300
RPDO_3 = 0x400
RPDO_4 = 0x500

# a list of COB ID's shamelessly taken from
# https://github.com/CANopenNode/CANopenNode/blob/b7166438453beeab84b0e1cf569fa329cb69dd3a/CANopen.h#L67-L91
# /**
# * Default CANopen identifiers.
# *
# * Default CANopen identifiers for CANopen communication objects. Same as
# * 11-bit addresses of CAN messages. These are default identifiers and
# * can be changed in CANopen. Especially PDO identifiers are confgured
# * in PDO linking phase of the CANopen network configuration.
# */
CO_CAN_ID_NMT_SERVICE = 0x000  # /**< 0x000  # Network management */
CO_CAN_ID_SYNC = 0x080  # /**< 0x080  # Synchronous message */
CO_CAN_ID_EMERGENCY = 0x080  # /**< 0x080  # Emergency messages (+nodeID) */
CO_CAN_ID_TIME_STAMP = 0x100  # /**< 0x100  # Time stamp message */
CO_CAN_ID_TPDO_1 = 0x180  # /**< 0x180  # Default TPDO1 (+nodeID) */
CO_CAN_ID_RPDO_1 = 0x200  # /**< 0x200  # Default RPDO1 (+nodeID) */
CO_CAN_ID_TPDO_2 = 0x280  # /**< 0x280  # Default TPDO2 (+nodeID) */
CO_CAN_ID_RPDO_2 = 0x300  # /**< 0x300  # Default RPDO2 (+nodeID) */
CO_CAN_ID_TPDO_3 = 0x380  # /**< 0x380  # Default TPDO3 (+nodeID) */
CO_CAN_ID_RPDO_3 = 0x400  # /**< 0x400  # Default RPDO3 (+nodeID) */
CO_CAN_ID_TPDO_4 = 0x480  # /**< 0x480  # Default TPDO4 (+nodeID) */
CO_CAN_ID_RPDO_4 = 0x500  # /**< 0x500  # Default RPDO5 (+nodeID) */
CO_CAN_ID_TSDO = 0x580  # /**< 0x580  # SDO response from server (+nodeID) */
CO_CAN_ID_RSDO = 0x600  # /**< 0x600  # SDO request from client (+nodeID) */
CO_CAN_ID_HEARTBEAT = 0x700 # /**< 0x700  # Heartbeat message */
#NMT error control, heartbeat and node guarding

canident = {
    CO_CAN_ID_NMT_SERVICE    : "NMT",
    CO_CAN_ID_SYNC  : "SYNC",
    CO_CAN_ID_EMERGENCY : "EMCY",
    CO_CAN_ID_TIME_STAMP : "TIMESTAMP",
    CO_CAN_ID_TPDO_1 : "TPDO1",
    CO_CAN_ID_RPDO_1 : "RPDO1",
    CO_CAN_ID_TPDO_2 : "TPDO2",
    CO_CAN_ID_RPDO_2 : "RPDO2",
    CO_CAN_ID_TPDO_3 : "TPDO3",
    CO_CAN_ID_RPDO_3 : "RPDO3",
    CO_CAN_ID_TPDO_4 : "TPDO4",
    CO_CAN_ID_RPDO_4 : "RPDO4",
    CO_CAN_ID_TSDO  : "SDOreply",
    CO_CAN_ID_RSDO : "SDOrequest",
    CO_CAN_ID_HEARTBEAT : "HEARTBEAT"
}

class CanopenDevice(CanDevice):


    def __init__(self, node_id, parent_bus, timeout=5.0):
        super(CanopenDevice, self).__init__(node_id, parent_bus)
        self.nmt_state = NMT_UNKNOWN
        self.device_type = None  # at first discovery time not yet known
        self.manufacturer = None # so not a sensible creation-time param
        self.name = name = None  # set those later once discovery works
        self.timeout = timeout
        self.heartbeating = False

        # handler dispatch on can identifier
        self.hdlr = {
            CO_CAN_ID_NMT_SERVICE : self.hdl_nmt,
            CO_CAN_ID_SYNC       : self.hdl_sync,
            CO_CAN_ID_EMERGENCY  : self.hdl_emcy,
            CO_CAN_ID_TIME_STAMP : self.hdl_timestamp,
            CO_CAN_ID_TPDO_1 : self.hdl_tpdo,
            CO_CAN_ID_RPDO_1 : self.hdl_rpdo,
            CO_CAN_ID_TPDO_2 : self.hdl_tpdo,
            CO_CAN_ID_RPDO_2 : self.hdl_rpdo,
            CO_CAN_ID_TPDO_3 : self.hdl_tpdo,
            CO_CAN_ID_RPDO_3 : self.hdl_rpdo,
            CO_CAN_ID_TPDO_4 : self.hdl_tpdo,
            CO_CAN_ID_RPDO_4 : self.hdl_rpdo,
            CO_CAN_ID_TSDO   : self.hdl_tsdo,
            CO_CAN_ID_RSDO   : self.hdl_rsdo,
            CO_CAN_ID_HEARTBEAT : self.hdl_heartbeat,
        }

    def hdl_nmt(self, ident, msg):
        if  msg.data[1] != self.node_id:
            return
        print("%d: nmt: msg=%s" % (self.node_id, msg))
        print ("%d: nmt %s -> %s" % (self.node_id,
                                    nmt_states[self.nmt_state],
                                    nmt_states[msg.data[0]]))
        self.nmt_state = msg.data[0]


    def hdl_heartbeat(self, ident, msg):
        print( "%d: heartbeat %s -> %s" % (self.node_id,
                                           nmt_states[self.nmt_state],
                                           nmt_states[msg.data[0]]))
        self.nmt_state = msg.data[0]
        if self.nmt_state == NMT_BOOTUP:
            time.sleep(1.0)
            # set heartbeat to 3000mS
            SDODownloadExp(self.parent_bus.fd, self.node_id, 0x1017, 0, 3000, 2)
            self.heartbeating = True # start monitoring

    def hdl_sync(self, ident, msg):
        print("sync: msg=", msg)

    def hdl_emcy(self, ident, msg):
        print("emcy: msg=", msg)

    def hdl_timestamp(self, ident, msg):
        print("timestamp: msg=", msg)

    def hdl_tpdo(self,ident,  msg):
        print("tpdo: msg=", msg)

    def hdl_rpdo(self, ident, msg):
        print("rpdo: msg=", msg)

    def hdl_tsdo(self,ident,  msg):
        print("tsdo: msg=", msg)

    def hdl_rsdo(self,ident,  msg):
        print("rsdo: msg=", msg)

    def process(self, msg):
        self.last_timestamp = msg.timestamp
        node_id = (msg.arbitration_id & 0x7f)
        ident = (msg.arbitration_id & 0x780)
        self.hdlr[ident](node_id, msg)

    def timer(self):
        if self.nmt_state !=  NMT_UNKNOWN:
            if self.heartbeating and time.time() - self.last_timestamp > self.timeout:
                print("device %d: disappeared" % (self.node_id))
                self.nmt_state =  NMT_UNKNOWN
            # XXX cause an estop
            return

    # string representation of an object:
    def __str__(self):
        s = "CanopenDevice "
        s += "node_id=%d " % self.node_id
        s += "state=%s " % nmt_states[self.nmt_state]
        s += "name=%s " % self.name
        s += "parent=%s " % self.parent_bus.ifname
        s += "device type=%s " % self.device_type
        s += "manufacturer=%s "% self.manufacturer
        return s
