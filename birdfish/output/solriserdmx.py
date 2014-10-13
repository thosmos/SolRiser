from base import BaseNetwork
import serial

class SolRiserDmx(BaseNetwork):

    def __init__(self,serial_port):
        super(SolRiserDmx,self).__init__()
        self.port = serial_port
        self.serial = serial.Serial(serial_port, 115200, timeout=0)
        self.updated = False

    def update_data(self):
        [e.update_data(self.data) for e in self.elements]
        self.updated = True

    def send_data(self):

        if not self.updated:
            self.update_data()
            self.updated = False

        #print self.data

        # use a hack to convert the binary array to a string to satisfy the Yun's pyserial implementation
        #self.serial.write("".join(map(chr, self.data)));
        self.serial.write(self.data.tostring())
