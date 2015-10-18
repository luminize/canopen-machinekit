
import select
import sys

from socketcan import CanBus,CanFrame
from canopen_device import CanopenDevice

# setting up can0
# slcand -f -o -c -s8 /dev/ttyACM0 can0
# ifconfig can0 up

# setting up vcan0
# sudo modprobe vcan
# sudo ip link add dev vcan0 type vcan
# sudo ip link set up vcan0


# see http://bioportal.weizmann.ac.il/course/python/PyMOTW/PyMOTW/docs/select/index.html#poll

# run poller.py
#timeout: vcan0
#timeout: can0
#timeout: vcan0
#timeout: can0
#timeout: vcan0

# power on the trinamic - a bootup message (several?)
#process: can0 1441630096.738198        0701    000    1    00
#process: can0 1441630096.875752        0701    000    1    00
#process: can0 1441630096.965012        0701    000    1    00

# other window: execute cansend vcan0 001#12
# process: vcan0 1441630185.544566        0001    000    1    12

buses = dict() # map socket fd's to CanopenBus objects


class CanBusDispatch(CanBus):
    def __init__(self, *args, **kwargs):
        super(CanBusDispatch, self).__init__(*args, **kwargs)
        self.devices = dict()

    def broadcast(self,cf):
        print("%s broadcast: %s" % (self.ifname, cf))

    def dispatch(self, cf):
        id = cf.arbitration_id & 0x7f

        if id == 0: # broadcast
            # for addr, dev in self.devices.items():
            #     dev.process(cf)
            return

        if not id in self.devices:
            self.devices[id] = CanopenDevice(id, self)
        print("%s: %s" % (self.ifname, cf))
        self.devices[id].process(cf)

    def timer(self):
        for addr, dev in self.devices.items():
            dev.timer()

    def add_device(self,node_id, device):
        self.devices[node_id] = device
        pass #print("%s: timeout" % (self.ifname))



# adapt as needed
can0 = CanBusDispatch(ifname="can0")
buses[can0.fd] = can0

vcan0 = CanBusDispatch(ifname="vcan0")
buses[vcan0.fd] = vcan0

poller = select.poll()
for fd in buses:
    poller.register(fd, select.POLLIN)

# Do not block forever
TIMEOUT = 1000 # milliseconds

try:
    import manhole
    manhole.install(locals={
        'buses' : buses,  # these objects will be visible in manhole-cli
        'can0' : can0,
        'vcan0' : vcan0,
    })
except Exception:
    print("manhole not installed - run 'sudo pip install manhole'")

while True:
    # watches all fd's in poller set
    events = poller.poll(TIMEOUT)
    if events:
        for fd, flag in events:
            if flag == select.POLLIN:
                bus = buses[fd]    # map fd->CanBus object
                cf = CanFrame()
                cf.read(fd)
                #m = canbus.bus.recv() # call its Bus.recv method
                bus.dispatch(cf)     # call the message handler
                    # in that CanopenBus object
    else:
        # nothing received
        for fd in buses:
            # call timeout handler on all bus objects
            buses[fd].timer()
