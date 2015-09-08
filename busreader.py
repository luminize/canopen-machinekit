
import select
import sys


# see http://bioportal.weizmann.ac.il/course/python/PyMOTW/PyMOTW/docs/select/index.html#poll

from canopen_bus import CanopenBus
from canopen_device import CanopenDevice

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


# adapt as needed
can0 = CanopenBus(ifname="can0")
buses[can0.fd()] = can0

vcan0 = CanopenBus(ifname="vcan0")
buses[vcan0.fd()] = vcan0

poller = select.poll()
for fd in buses:
    poller.register(fd, select.POLLIN)

# Do not block forever ()
TIMEOUT = 1000 # milliseconds

try:
    import manhole
    manhole.install(locals={
        'buses' : buses,  # these objects will be visible in manhole-cli
        'can0' : can0,
        'vcan0' : vcan0,
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
