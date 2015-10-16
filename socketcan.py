import struct
import socket
import select
import sys,os
import time

can_frame_fmt = "=IB3x8s"
assert struct.calcsize(can_frame_fmt) == 16

class CanFrame(object):

    def __init__(self, arbitration_id=0, dlc=0, data=None):
        self.arbitration_id = arbitration_id
        if data:
            if dlc:
                self.dlc = dlc
            else:
                self.dlc = len(data)
            self._data = bytearray(data).ljust(8, b'\x00')
        else:
            self.dlc = dlc
            self._data = []
        self.can_frame = bytearray(16)
        self.timestamp = 0

    @property
    def data(self):
        return self._data[:self.dlc]

    def write(self, fd):
        self._build()
        if type(fd) == CanBus:
            fd = fd.fd
        os.write(fd, self.can_frame)

    def read(self, fd, timeout=0): # msec
        if type(fd) == CanBus:
            fd = fd.fd
        if timeout:
            poller = select.poll()
            poller.register(fd, select.POLLIN)
            events = poller.poll(timeout)
            if events:
                for rfd, flag in events:
                    if flag == select.POLLIN:
                        self.can_frame = os.read(rfd, 16)
                        if len(self.can_frame) != 16:
                            raise IOError("invalid can_frame length %d" % len(self.frame))
                        self.timestamp = time.time()
                        return self._dissect()
            else:
                raise TimeoutError("read timed out after %d mS" % timeout)
        else:
            self.can_frame = os.read(fd, 16)
            if len(self.can_frame) != 16:
                raise IOError("invalid can_frame length %d" % len(self.can_frame))
            self.timestamp = time.time()
            return self._dissect()

    def _build(self):
        self.can_frame = struct.pack(can_frame_fmt, self.arbitration_id, self.dlc, self._data)
        return self.can_frame

    def __call__(self):
        return (self.arbitration_id, self.dlc, self._data[:self.dlc])

    def _dissect(self):
        (self.arbitration_id,
         self.dlc,
         self._data) = struct.unpack(can_frame_fmt, self.can_frame)
        return self()

  
    def __str__(self):
        s = "CanFrame("
        s += "id=%x dlc=%d data=%s)" % (self.arbitration_id, self.dlc, self._data[:self.dlc])
        return s

class CanBus(object):

    def __init__(self, ifname="can0",loopback=0,recv_own_msgs=0):
        self.s = socket.socket(socket.AF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
        self.ifname = ifname
        self.s.setsockopt(socket.SOL_CAN_RAW,
                          socket.CAN_RAW_LOOPBACK,
                          loopback)
        self.s.setsockopt(socket.SOL_CAN_RAW,
                          socket.CAN_RAW_RECV_OWN_MSGS,
                          recv_own_msgs)
        self.s.bind((ifname,))

        #
        #setsockopt(s, SOL_CAN_RAW, CAN_RAW_LOOPBACK, &loopback, sizeof(loopback));
# +    def testFilter(self):
# +        can_id, can_mask = 0x200, 0x700
# +        can_filter = struct.pack("=II", can_id, can_mask)
# +        with socket.socket(socket.PF_CAN, socket.SOCK_RAW, socket.CAN_RAW) as s:
# +            s.setsockopt(socket.SOL_CAN_RAW, socket.CAN_RAW_FILTER, can_filter)
# +            self.assertEqual(can_filter,
# +                    s.getsockopt(socket.SOL_CAN_RAW, socket.CAN_RAW_FILTER, 8))

    @property
    def fd(self):  # return the SocketCAN file descriptor
        return self.s.fileno()

    def __str__(self):
        s = "CanBus("
        s += "interface=%s fd=%d)" % (self.ifname, self.fd)
        return s



def SDOUploadExp(node,index, subindex):
    pass

CANOPEN_FC_NMT_MC        = 0x00
CANOPEN_FC_EMERGENCY     = 0x01
CANOPEN_FC_SYNC          = 0x01
CANOPEN_FC_TIMESTAMP     = 0x02
CANOPEN_FC_PDO1_TX       = 0x03
CANOPEN_FC_PDO1_RX       = 0x04
CANOPEN_FC_PDO2_TX       = 0x05
CANOPEN_FC_PDO2_RX       = 0x06
CANOPEN_FC_PDO3_TX       = 0x07
CANOPEN_FC_PDO3_RX       = 0x08
CANOPEN_FC_PDO4_TX       = 0x09
CANOPEN_FC_PDO4_RX       = 0x0A
CANOPEN_FC_SDO_TX        = 0x0B
CANOPEN_FC_SDO_RX        = 0x0C
CANOPEN_FC_NMT_NG        = 0x0E

CANOPEN_SDO_CS_RX_IDD = 0x20
CANOPEN_SDO_CS_ID_N_MASK  =   0x0C
CANOPEN_SDO_CS_ID_N_SHIFT =   0x02
CANOPEN_SDO_CS_ID_E_FLAG  =   0x02
CANOPEN_SDO_CS_ID_S_FLAG  =   0x01

def SDODownloadExp(fd, node, index, subindex, data, len, timeout=500):
    sdo = [CANOPEN_SDO_CS_RX_IDD|
           CANOPEN_SDO_CS_ID_E_FLAG|
           CANOPEN_SDO_CS_ID_S_FLAG|
           (((4-len) & 0x03) << CANOPEN_SDO_CS_ID_N_SHIFT),
           (index&0x00FF),
           (index&0xFF00)>>8,
           subindex,
           data & 0x000000FF,
           (data&0x0000FF00)>>8,
           (data&0x00FF0000)>>16,
           (data&0xFF000000)>>24]
    txcf = CanFrame(arbitration_id=node|(CANOPEN_FC_SDO_RX<<7), dlc=8, data=sdo)
    print("--> SDO Download: ",str(txcf))
    txcf.write(fd)
    rxcf = CanFrame()
    rxcf.read(fd, timeout=timeout)
    print("<-- SDO Download: ", str(rxcf))


# usage:
def main():
    canif = CanBus(ifname="can0")
    print(canif)
    print(CanFrame()) # the empty frame
    cf = CanFrame(arbitration_id=0,
                 data=[0x81,00])
    print(cf)
    cf.write(canif)
    for i in range(3):
        (id, dlc, data) = cf.read(canif, timeout=2500)
        print(id,dlc,data, str(cf))
    cf.arbitration_id = 0x42
    cf.write(canif)
    print(cf())

if __name__ == '__main__':
    main()
