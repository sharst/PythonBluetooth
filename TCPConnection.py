import socket
from threading import Thread
import ipdb
from PacketConnection import FramedPacketConnection

def_start_byte = '\xfc'
def_end_byte = '\xfd'
def_escape_byte = '\xfe'
def_octet_stuff_byte = '\x20'
def_max_packet_size = 232

# States
connected = 1
disconnected = 2
ready = 3
incoming = 4
escaping = 5
received = 6
dead = 7

D = True
    
class TCPConnection(FramedPacketConnection):
    """
    Creates a new framed TCP connection based on packet communication.
    
    Parameters
    ----------
    callback : function
       The function that newly arrived packets should be passed to. Should have exactly one argument. 
    auto_reconnect: boolean
       Defines whether the socket should be automatically reopened after connection loss.
    framed: boolean
       Defines whether packets used in this connection are framed by start and end bytes. If false, each packet
       will contain exactly 1 byte.
    start_byte: byte
       If framed = True, use this as the start byte of a packet (default: '\xfc')
    end_byte: byte
       If framed = True, use this as the end byte of a packet (default: '\xfd')
    escape_byte: byte
       If framed = True, use this as the escape character. (default: '\xfe')
    octet_stuff_byte: byte
       If framed = True, use this byte to do octet stuffing and unstuffing on escaped characters. 
       
    """
    def __init__(self, callback, auto_reconnect = True, framed = True, start_byte = def_start_byte, end_byte = def_end_byte, 
                 escape_byte = def_escape_byte, octet_stuff_byte = def_octet_stuff_byte):
        FramedPacketConnection.__init__(self, callback, auto_reconnect, framed, start_byte, end_byte, escape_byte, octet_stuff_byte)
        self.client_socket = None
        self.server_socket = None
        self.state = disconnected
        
    """ Open port and wait for other devices to connect """
    def createServer(self, port = 3):
        self.server_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((socket.gethostname(), 5000))
        if D: print "This server is now reachable under the name " + socket.gethostname()
        self.server_socket.listen(1)
        
        while True:
            if D: print "Trying to connect.."
            self.client_socket, address = self.server_socket.accept()
            if D: print "Now connected to "+ repr(address)
            self.change_state(ready)
        
            conn_thread = ConnectedThread(self.client_socket, self.byte_callback)
            conn_thread.run()
            if not self.auto_reconnect:
                break
    
    """ Actively connect to another device with an address """
    def createClient(self, address, port = 3000):
        self.client_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if D: print "Trying to connect.."
        self.client_socket.connect((address, port))
        if D: print "Connected!"
        self.change_state(ready)

    
    """ Closes the bluetooth socket """
    def closeConnection(self):
        if self.server_socket is not None:
            self.server_socket.close()
        
        self.client_socket.close()
        self.change_state(dead)

        
# A thread that waits on the open socket for incoming bytes
class ConnectedThread(Thread):
    def __init__(self, socket, callback):
        self.callback = callback
        self.socket = socket
        
    def run(self):
        while True:
            #try:
            dat = self.socket.recv(1)
            self.callback(dat)
            #except BluetoothError:
            #    if (D): print "Connection lost!"
            #    return


        