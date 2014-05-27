from TCPConnection import TCPConnection
from Packet import Packet
import time
import random


class RelayStation():
    def __init__(self):
        self.conn = TCPConnection(self.callback)
    
    def connect(self):    
        self.conn.createServer(port = 4000)
        
    def close_conn(self):
        self.conn.closeConnection()

    def callback(self, pck):
        print "Received new packet: " + repr(pck.read_float_list())
        raw_input()
        out = Packet()
        out.put_float_list(pck.read_float_list())
        print "Sending packet back "
        self.conn.sendPacket(out)
        print "Done."
        
class SendingStation():
    def __init__(self):
        self.conn = TCPConnection(self.callback)
    
    def connect(self):    
        address = "192.168.235.6"
        self.conn.createClient(address, 5000)
        while True:
            pck = Packet()
            dat = [random.random() for _ in range(10)]
            pck.put_float_list(dat)
            print "Sending: " + repr(dat)
            self.conn.sendPacket(pck)
            raw_input()
        
    def close_conn(self):
        self.conn.closeConnection()

    def callback(self, pck):
        print "Received!"
        print "Received new packet: " + repr(pck.read_float_list())
           
    
if __name__=="__main__":
    #try:
    test = RelayStation()
    test.connect()
    #finally:
        #pass
    #    test.close_conn()
    