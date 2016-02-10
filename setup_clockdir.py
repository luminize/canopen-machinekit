'''
send some simple commands to get a CANopen
device in clock/dir mode
'''

import can
import sys
import time
from can.interfaces.interface import Bus
from binascii import hexlify

def send_nmt(nmtcmd,node_id):
    m = can.Message(arbitration_id=0,
                    extended_id=False,
                    dlc=2,
                    data=bytearray([nmtcmd,node_id]))
    bus.send(m)

def send_sdo(messagedata, node_id):
    #doesnt work, need to convert register to bytearray yet
    #hardcoded for now
    # https://en.wikipedia.org/wiki/CANopen#Service_Data_Object_.28SDO.29_protocol
    m = can.Message(arbitration_id=(0x600+node_id) ,extended_id=False,
                    dlc=2,data=messagedata)
    bus.send(m)

NMT_BOOTUP  = 0x00
NMT_PREOP   = 0x7f
NMT_OP      = 0x05
NMT_STOPPED = 0x04

nmt_states = {
    NMT_BOOTUP  : 'BOOTUP',
    NMT_PREOP   : 'PRE-OPERATIONAL',
    NMT_OP      : 'OPERATIONAL',
    NMT_STOPPED : 'STOPPED'
}

MSG_NMT_START_REMOTE = 0x01
MSG_NMT_STOP_REMOTE  = 0x02
MSG_NMT_PRE_OP       = 0x80
MSG_NMT_RESET_NODE   = 0x81
MSG_NMT_RESET_COM    = 0x82


TSDO = 0x580 # /**< 0x580, SDO response from server (+nodeID) */
RSDO = 0x600 # /**< 0x600, SDO request from client (+nodeID) */
################################################################################
if len(sys.argv) == 2:
    # get the node address from the first command-line argument
    node = int(sys.argv[1])
else:
    print("usage: %s NODE" % sys.argv[0])
    exit(1)
################################################################################
ifname="can0"
bustype="socketcan_ctypes"
bus = Bus(ifname, bustype=bustype)
if (bus.socket < 0):
    raise IOError,"could not open %s" % ifname

# reset node and start
send_nmt(MSG_NMT_RESET_NODE,node)
time.sleep(3)
send_nmt(MSG_NMT_START_REMOTE,node)
time.sleep(0.5)
# we can now receive PDO's etc.

#value = canopen.SDODownloadExp(node, 0x6040, 0, 0x06, 2)
data=bytearray([0x2B,0x40, 0x60, 0x00, 0x06, 0x00, 0x00, 0x00 ])
send_sdo(data, node)
time.sleep(0.5)
#  can0  605   [8]  2B 40 60 00 06 00 00 00
#  can0  585   [8]  60 40 60 00 00 00 00 00

#closed loop mode 0x3202 = 1
#2F = 1 byte
#2B = 2 byte
#22 = 4 byte
data=bytearray([0x22,0x02, 0x32, 0x00, 0x01, 0x00, 0x00, 0x00 ])
send_sdo(data, node)
time.sleep(0.5)


#get info from 320A:04 and 320B:04
data=bytearray([0x40,0x0A, 0x32, 0x04, 0x00, 0x00, 0x00, 0x00 ])
send_sdo(data, node)
time.sleep(0.5)
data=bytearray([0x40,0x0B, 0x32, 0x04, 0x00, 0x00, 0x00, 0x00 ])
send_sdo(data, node)
time.sleep(0.5)
#get info from 2057 and 2058
data=bytearray([0x40,0x57, 0x20, 0x00, 0x00, 0x00, 0x00, 0x00 ])
send_sdo(data, node)
time.sleep(0.5)
data=bytearray([0x40,0x58, 0x20, 0x00, 0x00, 0x00, 0x00, 0x00 ])
send_sdo(data, node)
time.sleep(0.5)

'''
#get info from 320A:04 and 320B:04 after setting values
data=bytearray([0x40,0x0A, 0x32, 0x04, 0x00, 0x00, 0x00, 0x00 ])
send_sdo(data, node)
time.sleep(0.5)
data=bytearray([0x40,0x0B, 0x32, 0x04, 0x00, 0x00, 0x00, 0x00 ])
send_sdo(data, node)
time.sleep(0.5)
'''

#set 320A:04 and 320A:04 to -1 (FFFFFFFF)
data=bytearray([0x22, 0x0A, 0x32, 0x04, 0xFF, 0xFF, 0xFF, 0xFF ])
send_sdo(data, node)
time.sleep(0.5)
#  can0  605   [8]  22 0A 32 04 FF FF FF FF
#set 320B:04 and 320B:04 to -1 (FFFFFFFF)
data=bytearray([0x22, 0x0B, 0x32, 0x04, 0xFF, 0xFF, 0xFF, 0xFF ])
send_sdo(data, node)
time.sleep(0.5)
#  can0  605   [8]  22 0A 32 04 FF FF FF FF

'''
#set 320A:04 and 320A:04 to 0
data=bytearray([0x22, 0x0A, 0x32, 0x04, 0x00, 0x00, 0x00, 0x00 ])
send_sdo(data, node)
time.sleep(0.5)
#  can0  605   [8]  22 0A 32 04 FF FF FF FF
#set 320B:04 and 320B:04 to 0
data=bytearray([0x22, 0x0B, 0x32, 0x04, 0x00, 0x00, 0x00, 0x00 ])
send_sdo(data, node)
time.sleep(0.5)
#  can0  605   [8]  22 0A 32 04 FF FF FF FF
'''
#get info from 320A:04 and 320B:04 after setting values
data=bytearray([0x40,0x0A, 0x32, 0x04, 0x00, 0x00, 0x00, 0x00 ])
send_sdo(data, node)
time.sleep(0.5)
data=bytearray([0x40,0x0B, 0x32, 0x04, 0x00, 0x00, 0x00, 0x00 ])
send_sdo(data, node)
time.sleep(0.5)

#setup for clock/dir mode. Do stupid for now
#value = canopen.SDODownloadExp(node, 0x6060, 0, 0xFF, 1)
data=bytearray([0x2F,0x60, 0x60, 0x00, 0xFF, 0x00, 0x00, 0x00 ])
send_sdo(data, node)
time.sleep(0.5)
#  can0  605   [8]  2F 60 60 00 FF 00 00 00
#  can0  585   [8]  60 60 60 00 00 00 00 00

#value = canopen.SDODownloadExp(node, 0x6040, 0, 0x07, 2)
data=bytearray([0x2B,0x40, 0x60, 0x00, 0x07, 0x00, 0x00, 0x00 ])
send_sdo(data, node)
time.sleep(0.5)
#value = canopen.SDODownloadExp(node, 0x6040, 0, 0x07, 2)
#  can0  605   [8]  2B 40 60 00 07 00 00 00
#  can0  585   [8]  60 40 60 00 00 00 00 00

#value = canopen.SDODownloadExp(node, 0x6040, 0, 0x0F, 2)
data=bytearray([0x2B,0x40, 0x60, 0x00, 0x0F, 0x00, 0x00, 0x00 ])
send_sdo(data, node)
time.sleep(0.5)
#value = canopen.SDODownloadExp(node, 0x6040, 0, 0x0F, 2)
#  can0  605   [8]  2B 40 60 00 0F 00 00 00
#  can0  585   [8]  60 40 60 00 00 00 00 00
