import can
import sys
import select

from can.interfaces.interface import Bus
from binascii import hexlify
from matilda_class import Robot
from matilda_class import RobotJoints
from canopen_bus import CanopenBus
from canopen_device import CanopenDevice

buses = dict() # map socket fd's to CanopenBus objects

# adapt as needed
can0 = CanopenBus(ifname="can0")
buses[can0.fd()] = can0

poller = select.poll()
for fd in buses:
    poller.register(fd, select.POLLIN)

# Do not block forever ()
TIMEOUT = 1000 # milliseconds


matilda = Robot(name='matilda', bus=can0)
j0 = RobotJoints(node_id=2, name='base_joint', parent_robot=matilda)
j1 = RobotJoints(node_id=3, name='lower_arm', parent_robot=matilda)
j2 = RobotJoints(node_id=4, name='upper_arm', parent_robot=matilda)
j3 = RobotJoints(node_id=5, name='wrist', parent_robot=matilda)
j4 = RobotJoints(node_id=6, name='hand', parent_robot=matilda)

#print matilda

#batch fill joints wits standard values
for item, (field, obj) in enumerate(matilda.joints.iteritems()):
    # grab the object and add object dictionary entries for PID and HOMING settings
    j=obj
    # be smarter later with per joint dictionary
    '''INPUTS'''
    j.add_object('3240sub01', bytearray([0x22, 0x40, 0x32, 0x01, 0x07, 0x00, 0x00, 0x00 ])) #enable bits 0,1 and 2 of 60FD by writing '7' to 3240:01
    j.add_object('3240sub08', bytearray([0x22, 0x40, 0x32, 0x08, 0x01, 0x00, 0x00, 0x00 ])) #enable routing by 3240:08 = 1
    j.add_object('3242sub03', bytearray([0x2F, 0x42, 0x32, 0x03, 0x04, 0x00, 0x00, 0x00 ])) #ref switch is bit 2, must be input 4 so 3242:03=4
    '''PID'''
    j.add_object('3202sub00', bytearray([0x22, 0x02, 0x32, 0x00, 0x01, 0x00, 0x00, 0x00 ])) #closedloop = 1
    j.add_object('3210sub01', bytearray([0x22, 0x10, 0x32, 0x01, 0x00, 0x0E, 0x04, 0x00 ])) #S_P default 2710
    j.add_object('3210sub02', bytearray([0x22, 0x10, 0x32, 0x02, 0x08, 0x00, 0x00, 0x00 ])) #S_I default 0
    j.add_object('3210sub03', bytearray([0x22, 0x10, 0x32, 0x03, 0x00, 0x08, 0x00, 0x00 ])) #V_P default 4E20
    j.add_object('3210sub04', bytearray([0x22, 0x10, 0x32, 0x04, 0x00, 0x00, 0x00, 0x00 ])) #V_I default 64
    j.add_object('3210sub05', bytearray([0x22, 0x10, 0x32, 0x05, 0x00, 0x80, 0x07, 0x00 ])) #P current control field forming comp default 7A120
    j.add_object('3210sub06', bytearray([0x22, 0x10, 0x32, 0x06, 0x00, 0x01, 0x00, 0x00 ])) #I current control field forming comp default 1388
    j.add_object('3210sub07', bytearray([0x22, 0x10, 0x32, 0x07, 0x00, 0x40, 0x07, 0x00 ])) #P current control torque forming comp default 7A120
    j.add_object('3210sub08', bytearray([0x22, 0x10, 0x32, 0x08, 0x00, 0x01, 0x00, 0x00 ])) #I current control torque forming comp default 1388
    '''HOMING'''
    j.add_object('607Csub00', bytearray([0x22, 0x7C, 0x60, 0x00, 0x01, 0x00, 0x00, 0x00 ])) #write '0' to home offset object
    j.add_object('6099sub01', bytearray([0x22, 0x99, 0x60, 0x01, 0x08, 0x00, 0x00, 0x00 ])) #write .. rpm to search for home speed
    j.add_object('6099sub02', bytearray([0x22, 0x99, 0x60, 0x02, 0x04, 0x00, 0x00, 0x00 ])) #write .. rpm to search for index speed
    j.add_object('609Asub00', bytearray([0x22, 0x9A, 0x60, 0x00, 0x80, 0x00, 0x00, 0x00 ])) #.. cnts/sec^2 homing acceleration
    j.add_object('6098sub00', bytearray([0x2F, 0x98, 0x60, 0x00, 0x04, 0x00, 0x00, 0x00 ])) #homing with reference switch method 3 or 4

#    print j.od

''' PID SETTINGS

#set 5V for input pins
# 3240:06 h : This subindex switches the switching thresholds between 5V
#             (value "0" at the bit position) and 24 V (value "1" at the
#             bit position) for each input individually.
# standard all in 0V setup
#  can0  602   [8]  40 40 32 06 00 00 00 00
#  can0  582   [8]  43 40 32 06 00 00 00 00



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

try:
    import manhole
    manhole.install(locals={
        'buses' : buses,  # these objects will be visible in manhole-cli
        'can0' : can0,
        'matilda' : matilda
    })
except Exception:
    print "manhole not installed - run 'sudo pip install manhole'"

while True:
    # watches all fd's in poller set
    events = poller.poll(TIMEOUT)
    if events:
        for fd, flag in events:
            if flag == select.POLLIN:
                canbus = buses[fd]    # map fd->CanopenBus object
                m = canbus.bus.recv() # call its Bus.recv method
                canbus.process(m)     # call the message handler
                                          # in that CanopenBus object
    else:
        # nothing received
        for fd in buses:
            # call timeout handler on all bus objects
            buses[fd].timeout()
