from base import BaseNetwork
import serial

class SolRiserDmx(BaseNetwork):

    def __init__(self,serial_port):
        super(SolRiserDmx,self).__init__()
        self.port = serial_port
        self.serial = serial.Serial(serial_port, 115200, timeout=0)
        #ser = serial.Serial("/dev/tty.usbmodemfa131", 57600, timeout=1)

    def send_data(self):
        # print "writing data to Arduino"
        self.update_data()
        print self.data
        #try:
        self.serial.write(self.data);
        #except serial.SerialException, (value,message):
        #    print "Serial Error, continuing: %s" % message
        #    self.wrapper = ClientWrapper()
        #    self.client = self.wrapper.Client()
        #    time.sleep(.5)