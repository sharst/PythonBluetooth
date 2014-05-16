from BluetoothConnection import BluetoothConnection
from Packet import Packet

class ConnectionTest():
    def __init__(self):
        self.conn = BluetoothConnection(self.callback)
    
    def connect(self):    
        self.conn.createServer()
        
    def close_conn(self):
        self.conn.closeConnection()

    def callback(self, pck):
        print "Received new packet: " + repr(pck.read_float_list())
        
        out = Packet()
        out.put_float_list(pck.read_float_list())
        self.conn.sendPacket(out)
    
if __name__=="__main__":
    #try:
    test = ConnectionTest()
    test.connect()
    #finally:
        #pass
    #    test.close_conn()
    