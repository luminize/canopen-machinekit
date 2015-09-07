from canopen_bus import canopen_bus
from canopen_device import canopen_device

canopenbus0 = canopen_bus("fast-bus")
canopenbus1 = canopen_bus("slow-bus")

''' canopenbus2 has 0 devices '''
canopenbus2 = canopen_bus("empty-bus")

print "number of created busses %d" % canopen_bus.buscount
print "first  bus name : ", canopenbus0.name
print "second bus name : ", canopenbus1.name
print "third  bus name : ", canopenbus2.name

device1 = canopen_device("joint1","canopenbus0","ds402","maxon")
device2 = canopen_device("joint2","canopenbus0","ds402","nanotec")
device3 = canopen_device("joint3","canopenbus0","ds402","nanotec")

device4 = canopen_device("device4","canopenbus1","ds402","maxon")

print "number of created devices : %d" % canopen_device.devicecount

device1.displayinfo()
device2.displayinfo()
device3.displayinfo()
device4.displayinfo()
