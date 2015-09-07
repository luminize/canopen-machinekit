''' canopen device class '''

class canopen_device:
    devicecount = 0

    def __init__(self, name, parent_bus, device_type, manufacturer):
        self.name = name
        self.parent_bus = parent_bus
        self.device_type = device_type
        self.manufacturer = manufacturer
        canopen_device.devicecount += 1

    def displaycount(self):
        print "number of devices: %d" % canopen_device.devicecount

    def displayinfo(self):
        print ""
        print "name         : ", self.name
        print "parent       : ", self.parent_bus
        print "device type  : ", self.device_type
        print "manufacturer : ", self.manufacturer
