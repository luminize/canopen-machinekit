''' canopen device class '''
from candevice import CanDevice
import hal

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
        name = str(self.parent_bus.ifname)+".node"+str(self.node_id)
        self.h = hal.component(name)
        print self.h
        self.h.newpin("tpdo1", hal.HAL_S32, hal.HAL_OUT)
        print self.h
#        self.h.ready()

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
                #print "heartbeat with %d byte" % msg.dlc
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

    def set_hal_tpdo1(self, value):
        self.h['tpdo1'] = value

    def readPDOsetup(self):
        # OD means Object Dictionary
        # SDO means Service Data Object
        # TPDO means Transmit Process Data Object
        # RPDO meand Receive Process Data Object
        #
        #
        # only do for TPDO1 for now, expand for later
        # this method will ask which registers are mapped to the specific PDO
        #
        # in the OD the Index area from 1400h to 15FFh is for RPDO communication
        # parameters. The first RPDO is at 1400h, the second at 1401h, the third
        # at 1402h and so on.
        #
        # in the OD the Index area from 1800h to 19FFh is for TPDO communication
        # parameters. The first TPDO is at 1800h, the second at 1801h, the third
        # at 1802h and so on.
        #
        # PDO COMMUNICATION parameters:
        # each PDO has subindexes for example 1800h subindex 0
        # which will tell:
        # subindex 0: u8 , nr of entries (the parameters, max 5, 0-2 mandatory)
        # subindex 1: u32, COB_id (the COB to send/listen to, like 180h + node_id)
        # subindex 2: u8 , transmission type, the trigger behaviour
        # subindex 3: u16, inhibit time, the minimum time in which not to send
        #                  not used in an RPDO
        # subindex 4: u8 , reserved, legacy value, do not use
        # subindex 5: u16, event time, when time driven sending (see subindex 2)
        #                  RPDO can generate an error if this timer expires
        #
        # PDO MAPPING parameters:
        # in the OD the Index area from 1600h to 17FFh is for RPDO mapping
        # in the OD the Index area from 1A00h to 1BFFh is for TPDO mapping
        #
        # There can be no more than 64 bits in the PDO, this means that there
        # are max 64 1-bit mappings
        # subindex 0: which is max 64 of 1 bit values.
        # subindex 1: which is the register where it points to, plus the
        #             subindex of that register PLUS the size of that subindex
        #
        # EXAMPLE:
        # TPDO1, index 1A00h subindex 0 is 2
        #                    subindex 1: 2010 01 08 (OD 2010, sub1, 8  bit)
        #                    subindex 2: 2010 02 10 (OD 2010, sub2, 16 bit)
        # this will then result in a 3 byte message which has to be decoded
        # by a master, or a directly linked RPDO of another node.
        # For example:
        # node5 is set up so that an TPDO1 of node 5 will send the COB_id 185h
        # node8 is set up that RPDO1 listens directly to a COB_id 185 by setting
        # RPDO1, subindex 1 to 185h and "decodes" this information into the
        # OD registers that have been set-up

        # reading the above parameters will be done with SDO's
        # focus on the TPDO1 for now:
        # master sends SDO read request -> node
        # node replies with SDO response and the data

        # KISS by requesting the MAPPING parameters only for now
        self.sendSDO(tpdo_mapping_registers[TPDO_1], 0)


    def sendSDO(self, register, sub):
        self.parent_bus.send_sdo(self.node_id, register, sub)
        pass

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
