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
#send_nmt(MSG_NMT_START_REMOTE,node)
#time.sleep(0.5)
# we can now receive PDO's etc.
'''
The following objects are required to control this mode:
Version 1.2.0 / 02.10.2015 / FIR-v1540
58Manual CL3-E (CAN/USB/Modbus)
8 Operating modes, page 58 CL3-E manual
    607C h (Home Offset): Specifies the difference between the zero position
            of the application and the reference point of the machine.
    6098 h (Homing Method):
            Method used for referencing (see "Reference run method")
    6099 h :01 h (Speed During Search For Switch):
            The speed for the search for the switch
    6099 h :02 h (Speed During Search For Zero):
            The speed for the search for the index
    609A h (Homing Acceleration):
            Acceleration and deceleration for the reference run
    2056 h (Limit Switch Tolerance Band):
            After moving to the positive or negative limit switch, the motor
            controller permits a tolerance range that the motor may not further
            travel. If this tolerance range is exceeded, the motor stops and the
            motor controller changes to the "Fault" state. If limit switches
            can be activated during the reference run, the tolerance range
            selected should be sufficiently large so that the motor does not
            leave the tolerance range when braking. Otherwise, the reference
            run cannot be completed successfully. After completion of the
            reference run, the tolerance range can be set back to "0" if this
            is required by the application.
    203A h :01 h (Minimum Current For Block Detection):
            Minimum current threshold that, when exceeded, detects blocking of
            the motor at a block.
    203A h :02 h (Period Of Blocking):
            Specifies the time in ms that the motor is nevertheless still to
            travel against the block after block detection.
    203A h :03 h (Block Detection Time)
            Specifies the time in ms that the current has to be at least above
            the minimum current threshold in order to detect a block
'''

'''
    most simple example is reference on index pulde, method 1 or 2
'''

'''
cansend can0 602#2202320001000000 set closed loop to '1'
cansend can0 602#2200180181010000 TPDO1 COB_id
cansend can0 602#2F001802FF000000 TPDO1 trigger immediate
cansend can0 602#227C600000000000 write '0' to home offset object
cansend can0 602#2299600122000000 write 34 rpm to search for home speed
cansend can0 602#2299600222000000 write 34 rpm to search for index speed
cansend can0 602#229A600037894100 10^5 cnts/sec^2 homing acceleration
cansend can0 602#2F98600022000000 set homing method 34 (22h)
cansend can0 602#2F60600006000000 set drive in homing mode
cansend can0 000#0205             start comm. state engine
cansend can0 602#2B40600006000000 node n shutdown (power) -> ready to switch on
cansend can0 602#2B40600007000000 node 1 ready to switch on -> operation disabled
cansend can0 602#2B4060000F000000 node 1 operation disabled -> operation enabled
cansend can0 602#2B4060001F000000 start homing (homing mode only)
'''

#make sure we're in closed loop mode 0x3202 = 1
#2F = 1 byte
#2B = 2 byte
#22 = 4 byte
#cansend can0 602#2202320001000000 set closed loop to '1'
data=bytearray([0x22, 0x02, 0x32, 0x00, 0x01, 0x00, 0x00, 0x00 ])
send_sdo(data, node)
time.sleep(0.5)

''' PID SETTINGS '''
#cansend can0 602#2210320500000000 3210:01 S_P default 2710
data=bytearray([0x22, 0x10, 0x32, 0x01, 0x00, 0x0E, 0x04, 0x00 ])
send_sdo(data, node)
time.sleep(0.5)

#cansend can0 602#2210320500000000 3210:02 S_I default 0
data=bytearray([0x22, 0x10, 0x32, 0x02, 0x08, 0x00, 0x00, 0x00 ])
send_sdo(data, node)
time.sleep(0.5)

#cansend can0 602#2210320500000000 3210:03 V_P default 4E20
data=bytearray([0x22, 0x10, 0x32, 0x03, 0x00, 0x08, 0x00, 0x00 ])
send_sdo(data, node)
time.sleep(0.5)

#cansend can0 602#2210320500000000 3210:04 V_I default 64
data=bytearray([0x22, 0x10, 0x32, 0x04, 0x00, 0x00, 0x00, 0x00 ])
send_sdo(data, node)
time.sleep(0.5)

#cansend can0 602#2210320500000000 3210:05 P current control field forming comp default 7A120
data=bytearray([0x22, 0x10, 0x32, 0x05, 0x00, 0x80, 0x07, 0x00 ])
send_sdo(data, node)
time.sleep(0.5)

#cansend can0 602#2210320500000000 3210:06 I current control field forming comp default 1388
data=bytearray([0x22, 0x10, 0x32, 0x06, 0x00, 0x01, 0x00, 0x00 ])
send_sdo(data, node)
time.sleep(0.5)

#cansend can0 602#2210320500000000 3210:07 P current control torque forming comp default 7A120
data=bytearray([0x22, 0x10, 0x32, 0x07, 0x00, 0x40, 0x07, 0x00 ])
send_sdo(data, node)
time.sleep(0.5)

#cansend can0 602#2210320500000000 3210:07 I current control torque forming comp default 1388
data=bytearray([0x22, 0x10, 0x32, 0x08, 0x00, 0x01, 0x00, 0x00 ])
send_sdo(data, node)
time.sleep(0.5)

#cansend can0 602#2200180181010000 TPDO1 COB_id
#cansend can0 602#2F001802FF000000 TPDO1 trigger immediate

#cansend can0 602#227C600000000000 write '0' to home offset object
data=bytearray([0x22, 0x7C, 0x60, 0x00, 0x01, 0x00, 0x00, 0x00 ])
send_sdo(data, node)
time.sleep(0.5)

#cansend can0 602#2299600122000000 write 34 (22) rpm to search for home speed
data=bytearray([0x22, 0x99, 0x60, 0x01, 0x08, 0x00, 0x00, 0x00 ])
send_sdo(data, node)
time.sleep(0.5)

#cansend can0 602#2299600222000000 write 34 rpm to search for index speed
data=bytearray([0x22, 0x99, 0x60, 0x02, 0x04, 0x00, 0x00, 0x00 ])
send_sdo(data, node)
time.sleep(0.5)

#cansend can0 602#229A600037894100 10^5 cnts/sec^2 homing acceleration
#data=bytearray([0x22, 0x9A, 0x60, 0x00, 0x37, 0x89, 0x41, 0x00 ])
data=bytearray([0x22, 0x9A, 0x60, 0x00, 0x88, 0x00, 0x00, 0x00 ])
send_sdo(data, node)
time.sleep(0.5)

#set 5V for input pins
# 3240:06 h : This subindex switches the switching thresholds between 5V
#             (value "0" at the bit position) and 24 V (value "1" at the
#             bit position) for each input individually.
# standard all in 0V setup
#  can0  602   [8]  40 40 32 06 00 00 00 00
#  can0  582   [8]  43 40 32 06 00 00 00 00

#enable bits 0,1 and 2 of 60FD by writing '7' to 3240:01
#cansend can0 602#2240320107000000
data=bytearray([0x22, 0x40, 0x32, 0x01, 0x07, 0x00, 0x00, 0x00 ])
send_sdo(data, node)
time.sleep(0.5)

#invert logic bit 0 by writing '1' to 3240:02
#cansend can0 602#2240320107000000
#data=bytearray([0x22, 0x40, 0x32, 0x02, 0x01, 0x00, 0x00, 0x00 ])
#send_sdo(data, node)
#time.sleep(0.5)

#do input routing

#setup special function enable 3240:01 = 1
#cansend can0 602#2240320101000000

#enable routing:
#3240:08 = 1
#cansend can0 604#2240320801000000
data=bytearray([0x22, 0x40, 0x32, 0x08, 0x01, 0x00, 0x00, 0x00 ])
send_sdo(data, node)
time.sleep(0.5)

#ref switch is bit 2, must be input 4:
#3242:03=4
#cansend can0 604#2F42320304000000
data=bytearray([0x2F, 0x42, 0x32, 0x03, 0x04, 0x00, 0x00, 0x00 ])
send_sdo(data, node)
time.sleep(0.5)

#cansend can0 602#2F98600022000000 set homing method 34 (22h)
#data=bytearray([0x2F, 0x98, 0x60, 0x00, 0x22, 0x00, 0x00, 0x00 ])
#reference switch method 3 or 4
data=bytearray([0x2F, 0x98, 0x60, 0x00, 0x04, 0x00, 0x00, 0x00 ])
#reference switch method 1 or 2
#data=bytearray([0x2F, 0x98, 0x60, 0x00, 0x01, 0x00, 0x00, 0x00 ])
send_sdo(data, node)
time.sleep(0.5)

#cansend can0 602#2F60600006000000 set drive in homing mode
data=bytearray([0x2F, 0x60, 0x60, 0x00, 0x06, 0x00, 0x00, 0x00 ])
send_sdo(data, node)
time.sleep(0.5)

#cansend can0 000#0205             start comm. state engine
send_nmt(MSG_NMT_START_REMOTE,node)
time.sleep(0.5)

#cansend can0 602#2B40600006000000 node n shutdown (power) -> ready to switch on
data=bytearray([0x2B, 0x40, 0x60, 0x00, 0x06, 0x00, 0x00, 0x00 ])
send_sdo(data, node)
time.sleep(0.5)

#cansend can0 602#2B40600007000000 node 1 ready to switch on -> operation disabled
data=bytearray([0x2B, 0x40, 0x60, 0x00, 0x07, 0x00, 0x00, 0x00 ])
send_sdo(data, node)
time.sleep(0.5)

#cansend can0 602#2B4060000F000000 node 1 operation disabled -> operation enabled
data=bytearray([0x2B, 0x40, 0x60, 0x00, 0x0F, 0x00, 0x00, 0x00 ])
send_sdo(data, node)
time.sleep(0.5)

#cansend can0 602#2B4060001F000000 start homing (homing mode only)
data=bytearray([0x2B, 0x40, 0x60, 0x00, 0x1F, 0x00, 0x00, 0x00 ])
send_sdo(data, node)
time.sleep(0.5)

'''
#get info from 320A:04 and 320B:04 after setting values
data=bytearray([0x40,0x0A, 0x32, 0x04, 0x00, 0x00, 0x00, 0x00 ])
send_sdo(data, node)
time.sleep(0.5)
'''
