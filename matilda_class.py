import time

class RobotJoints(object):

    def __init__(self, node_id, name, parent_robot):
        self.node_id = node_id
        self.name = name
        self.parent_robot = parent_robot
        parent_robot.add_joint(node_id, self)
        # set joint specific objects
        self.od = dict()

    # only add complete SDO bytearray messages. Get smarter later
    def add_object(self, od_val, ba): #od_val = object register, ba = bytearray
        self.od[od_val] = ba
#        print('object %s with value %s added' % (od_val,ba))

    def set_od(self):
        for key, value in self.od.iteritems():
           self.parent_robot.bus.send_sdo(self.node_id, value)
           time.sleep(0.1)


    # string representation of a Joint:
    def __str__(self):
        s = "RobotJoint "
        s += "node_id=%d " % self.node_id
        s += "name=%s " % self.name
        s += "robot=%s " % self.parent_robot.name
        s += "objects=%s " % self.od
        return s

class Robot(object):

    def __init__(self, name, bus):
        self.name = name
        self.bus = bus
        self.joints = dict()
        self.od = dict()

    def add_joint(self, node_id, joint):
        self.joints[node_id] = joint

    def reset_joints(self):
        # iterate over all joints and send reset signal
        for item, (field, obj) in enumerate(self.joints.iteritems()):
            nmt_messages = self.bus.nmt_messages
            self.bus.send_nmt(obj.node_id, nmt_messages['MSG_NMT_RESET_NODE'])
            time.sleep(0.1)

    def set_joints_od(self):
        for item, (field, obj) in enumerate(self.joints.iteritems()):
            # for each joint, set up the object dictionary
            obj.set_od()

    def setup_clockdir(self):
        pass

    def __str__(self):
        s = "Robot "
        s += "name=%s " % self.name
        s += "bus=%s" % self.bus
        s += "joints=%s" % self.joints
        s += "od=%s" % self.od
        return s
