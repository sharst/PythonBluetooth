from bluetooth import BluetoothSocket, RFCOMM, discover_devices, BluetoothError
from threading import Thread
from Packet import Packet
import ipdb

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
    
class BluetoothConnection(object):
    """
    Creates a new bluetooth connection.
    
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
        self.client_socket = None
        self.server_socket = None
        self.callback = callback
        self.state = disconnected
        self.start_byte = start_byte
        self.end_byte = end_byte
        self.escape_byte = escape_byte
        self.octet_stuff_byte = octet_stuff_byte
        self.curr_packet = Packet()
        self.auto_reconnect = auto_reconnect
        self.framed = framed
    
    """ Open port and wait for other devices to connect """
    def createServer(self, port = 3):
        self.server_socket=BluetoothSocket( RFCOMM )

        self.server_socket.bind(("", port))
        self.server_socket.listen(1)

        while True:
            if D: print "Trying to connect.."
            self.client_socket, _ = self.server_socket.accept()
            if D: print "Connected!"
            self.change_state(ready)
        
            conn_thread = ConnectedThread(self.client_socket, self.byte_callback)
            conn_thread.run()
            if not self.auto_reconnect:
                break
    
    """ Actively connect to another device with an address """
    def createClient(self, address, port = 3):
        if address == "first":
            address = self.searchDevices()[0]
        self.client_socket=BluetoothSocket( RFCOMM )
        if D: print "Trying to connect.."
        self.client_socket.connect((address, port))
        if D: print "Connected!"
        self.change_state(ready)
    
    """ Returns a list of currently discovered devices """
    def searchDevices(self):
        return discover_devices()
    
    """ Change the state of this Bluetooth Connection. Should only be used internally. """
    def change_state(self, new_state):
        if D: print "Changing state to " + repr(new_state)
        self.state = new_state
    
    """ Method to be called when a new byte comes in 
        on the open socket. Parses the bytes into packets. """ 
    def byte_callback(self, dat):
        if self.framed:
            if self.state == ready:
                if dat == self.start_byte:
                    self.curr_packet.set_start_time()
                    self.change_state(incoming)
                
            elif self.state == incoming:
                if dat == self.escape_byte:
                    self.change_state(escaping)
                elif dat == self.end_byte:
                    self.curr_packet.set_end_time()
                    self.change_state(received)
                else:
                    self.curr_packet.put_byte(dat)
                    
            elif self.state == escaping:
                dat = chr(ord(dat)^ord(self.octet_stuff_byte))
                self.curr_packet.put_byte(dat)
                self.change_state(incoming)
            
            if self.state == received:
                self.change_state(ready)
                self.callback(Packet(self.curr_packet))
                self.curr_packet = Packet()
                
        # In unframed mode, 1 byte = 1 packet.         
        else:
            self.change_state(incoming)
            self.curr_packet.put_byte(dat)
            self.change_state(ready)
            self.callback(Packet(self.curr_packet))
            self.curr_packet.set_start_time()
            self.curr_packet = Packet()
            
    
    """ Send raw data (without using packets). This method should only be used internally """
    def sendData(self, data):
        # XXX: This could wait for connection to be ready and then try again
        if self.state == ready:
            self.client_socket.send(data)
        else:
            if D: print "State is:  " + repr(self.state)
            ipdb.set_trace()
            if D: print "Connection is not ready, cannot send packet!"
    
    """ Frames and sends a packet over the connection """
    def sendPacket(self, pck):
        dat = pck.get_data()
        lst = []
        lst.append(self.start_byte)
        
        for i in range(len(dat)):
            if (self.needs_escaping(dat[i])):
                lst.append(self.escape_byte)
                # XXX: Ugly line of code.
                lst.append(chr(ord(dat[i])^ord(self.octet_stuff_byte)))
            else:
                lst.append(dat[i])
        
        lst.append(self.end_byte)
        self.sendData("".join(lst))
    
    """ Closes the bluetooth socket """
    def closeConnection(self):
        if self.server_socket is not None:
            self.server_socket.close()
        
        self.client_socket.close()
        self.change_state(dead)
    
    """ Returns whether a byte needs to be escaped in a packet. """
    def needs_escaping(self, dat):
        return (((dat == self.start_byte) or
                 (dat == self.end_byte)) or
                 (dat == self.escape_byte))
        
        
# A thread that waits on the open socket for incoming bytes
class ConnectedThread(Thread):
    def __init__(self, socket, callback):
        self.callback = callback
        self.socket = socket
        
    def run(self):
        while True:
            try:
                dat = self.socket.recv(1)
                self.callback(dat)
            except BluetoothError:
                if (D): print "Connection lost!"
                return
        
        
        
        