from base import BaseNetwork
import serial

class SolRiserDmx(BaseNetwork):

    def __init__(self,serial_port):
        super(SolRiserDmx,self).__init__()
        self.port = serial_port
        self.serial = serial.Serial(serial_port, 115200, timeout=0)

    def send_data(self):
        
        self.update_data()

        #print self.data

        # use a hack to convert the binary array to a string to satisfy the Yun's pyserial implementation
        self.serial.write("".join(map(chr, self.data)));
        