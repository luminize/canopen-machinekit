''' canopen bus class '''

from canopen_device import CanopenDevice

import can
from can.interfaces.interface import Bus

class CanopenBus:

    def __init__(self, ifname="can0", bustype="socketcan_ctypes"):
        self.ifname = ifname
        self.bus = Bus(ifname, bustype=bustype)
        if self.bus.socket < 0:
            raise IOError,"could not open %s" % ifname
        self.devices = dict() # node-id -> device object dict

    def fd(self):  # return the SocketCAN file descriptor
        return self.bus.socket

    def process(self, msg):
        # see https://python-can.readthedocs.org/en/latest/message.html
        #print "process: %s node=%d dlc=%d %s" % (self.ifname,
        #                                         msg.arbitration_id & 0x07f,
        #                                         msg.dlc, msg)
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
        # determine node_id
        node_id = msg.arbitration_id & ~0x780 # 0x700 + node is + state set on bootup of device
        if msg.arbitration_id & 0x700: # a NMT error control message
            node_id = msg.arbitration_id & ~0x700 # 0x700 with node nr on bootup
            if self.devices.has_key(node_id):
                #print "node %d heartbeat message heard" % (node_id)
                pass
            else:
                #print "node %d first time heartbeat, creating device" % node_id
                d = CanopenDevice(node_id, self)
                self.devices[node_id] = d

            # and call its message handler
            self.devices[node_id].process(msg)
            return

        if msg.arbitration_id & 0x000: # NMT service message
            pass
            #print "message: NMT service"
        if msg.arbitration_id & 0x080: # Emergency message
            node_id = msg.arbitration_id & ~0x080
            print "message: Emergency on node %d" % node_id

        # a message which has not been identified yet
        if self.devices.has_key(node_id):
            # this device already exists
            self.devices[node_id].process(msg)
            return

        # to add a non-CANOpen device:
        if False: # replace by condition as needed
            d = CanDevice(node_id, self)
            self.devices[node_id] = d

            # and call its message handler
            self.devices[node_id].process(msg)
            return

    def timeout(self):
        for d in self.devices:
            self.devices[d].timeout()

    def add_device(self,node_id, device):
        self.devices[node_id] = device

    def num_devices(self):
        return len(self.devices.keys())

    def __str__(self):
        s = "CanopenBus: name=%s fd=%d" % (self.ifname,self.fd())
        return s

    def send_nmt(self, node_id, nmtcmd):
        m = can.Message(arbitration_id=0,extended_id=False,
                        dlc=2,data=bytearray([nmtcmd,node_id]))
        self.bus.send(m)
