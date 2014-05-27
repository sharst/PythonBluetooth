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
    def createServer(self, port = 5000):
        self.server_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # XXX: Reuse address maybe shouldnt be default?
        self.server_socket.bind(("", port))
        if D: print "This server is now reachable under the name " + socket.gethostname()
        self.server_socket.listen(1)
        
        while True:
            if D: print "Trying to connect.."
            self.client_socket, address = self.server_socket.accept()
            if D: print "Now connected to "+ repr(address)
            self.change_state(ready)
        
            thread = Thread(target=listen_at_socket, args=(self.client_socket, self.byte_callback))
            thread.start()

            if not self.auto_reconnect:
                break
    
    """ Actively connect to another device with an address """
    def createClient(self, address, port = 5000):
        self.client_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # XXX: Reuse address maybe shouldnt be default?
        if D: print "Trying to connect.."
        self.client_socket.connect((address, port))
        if D: print "Connected!"
        self.change_state(ready)
        
        thread = Thread(target=listen_at_socket, args=(self.client_socket, self.byte_callback))
        thread.start()
        #conn_thread = ConnectedThread(self.client_socket, self.byte_callback)
        #conn_thread.run()
        print "Started connected thread"
    
    """ Closes the socket """
    def closeConnection(self):
        if self.server_socket is not None:
            self.server_socket.close()
        
        self.client_socket.close()
        self.change_state(dead)


def listen_at_socket(socket, callback):
    while True:
        dat = socket.recv(1)
        callback(dat)



        