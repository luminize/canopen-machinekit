
import sys
import time
import can

from canopen_bus import CanopenBus
from canopen_device import CanopenDevice

# the register adresses for this canopen device
#    RPDO_1: 0x1600,
#    RPDO_2: 0x1601,
#    RPDO_3: 0x1602,
#    RPDO_4: 0x1603,
#    TPDO_1: 0x1A00,
#    TPDO_2: 0x1A01,
#    TPDO_3: 0x1A02,
#    TPDO_4: 0x1A03
#

def sendSDO(node_id,cob_id,databytes):
    #break up byte into bytearray
    m = can.Message(arbitration_id=(cob_id+node_id), extended_id=False,
                    dlc=2,data=bytearray(databytes))
    can0.bus.send(m)
    time.sleep(0.5)         # wait for 0.5 sec
    return;

def readSDO():
    m = can0.bus.recv()
    time.sleep(0.5)
    #d = bytearray(m.data)
    return m;

def iteratePDOmaps(pdoadress, i,):
    return

can0 = CanopenBus(ifname="can0")

cob_id = 0x600
node_id = 5

# manually make the bytearray
databytes=bytearray([0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 ])
databytes[1] = 0x00
databytes[2] = 0x16
databytes[3] = 0x00
subindex = 0x00
databytes[4] = subindex
# the databyte has been manually made

sendSDO(cob_id,node_id,databytes)
msg = readSDO()
retval = msg.data
nr_of_maps = retval[4]
reg = (retval[2] << 8) + retval[1]
print "register %04xh, subindex %02x has value %d" % (reg, subindex, nr_of_maps)
# loop thru the subindexes which have a different bytearray
#databytes[0] = 0x40
databytes[3] = 0x00
databytes[4] = 0x00
for j in range (0, nr_of_maps):
    subindex += 1
    databytes[3] = subindex
    sendSDO(cob_id,node_id,databytes)
    msg2 = readSDO()
    retval2 = msg.data
    nr_of_maps = retval2[4]
    #print "0%04xh" % retval[2]
    #print "0%04xh" % (retval[2] << 8)
    reg2 = (retval2[2] << 8) + retval2[1]
    print "register %04xh, subindex %02x has SDO reply:" % (reg2, subindex)
    print str(msg2)
