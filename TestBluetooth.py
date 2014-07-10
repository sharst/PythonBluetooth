from BluetoothConnection import BluetoothConnection
from Packet import Packet
import ipdb

class RelayStation():
    def __init__(self):
        self.conn = BluetoothConnection(self.callback)
    
    def connect(self):    
        self.conn.createServer()
        
    def close_conn(self):
        self.conn.closeConnection()

    def callback(self, pck):
        #ipdb.set_trace()
        cont = pck.pop_float_list()
        print "Received new packet: " + repr(cont)
        
        out = Packet()
        out.append_float_list(cont)
        self.conn.sendPacket(out)
    
if __name__=="__main__":
    #try:
    test = RelayStation()
    test.connect()
    #finally:
        #pass
    #    test.close_conn()
    