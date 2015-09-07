from canopen_bus import CanopenBus
from canopen_device import CanopenDevice

buses = []
canopenbus0 = CanopenBus("fast-bus")
canopenbus1 = CanopenBus("slow-bus")

buses.append(canopenbus0)
buses.append(canopenbus1)

''' canopenbus2 has 0 devices '''
canopenbus2 = CanopenBus("empty-bus")
buses.append(canopenbus2)

#print "number of created busses %d" % canopen_bus.buscount
print "first  bus  : ", str(canopenbus0)
print "second bus  : ", str(canopenbus1)
print "third  bus  : ", str(canopenbus2)

device1 = CanopenDevice(2, canopenbus0)
device2 = CanopenDevice(5, canopenbus0)
device3 = CanopenDevice(8, canopenbus0)
device4 = CanopenDevice(22,canopenbus1)

print "number of buses:", len(buses)

for b in buses:
    print "bus %s: %d devices" % (b.name, b.num_devices())
    for id in b.devices:
        print "device %s" % str(b.devices[id])

print str(device1)
print str(device2)
print str(device3)
print str(device4)

