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
        print "process: %s node=%d dlc=%d %s" % (self.ifname,
                                                 msg.arbitration_id,
                                                 msg.dlc, msg)
        if self.devices.has_key(msg.arbitration_id):
            # this device already exists
            self.devices[msg.arbitration_id].process(msg)
        else:
            # assume it is a bootup message
            print "no such device yet, creating:", msg.arbitration_id
            d = CanopenDevice(msg.arbitration_id, self)
            self.devices[msg.arbitration_id] = d
            # and call its message handler
            self.devices[msg.arbitration_id].process(msg)

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
