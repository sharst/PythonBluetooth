import struct
from time import time

# XXX: This class still needs more functions for adding data (also, importantly, at specific 
# byte positions!)

class Packet(object):
    """
    This class represents a single packet that can be sent over bluetooth.
    It also supports parsing various types directly into a package. 
    Packet framing is done directly by the bluetooth connection.
    
    Parameters
    ----------
    
    copy: Packet
        If specified, the given packet is cloned.
    littleendian: boolean
        Defines whether the bytes in this packet are in little or big endian order.
    """
         
    def __init__(self, copy = None, littleendian = True):
        if copy is not None:
            self.data = copy.data
            self.start_time = copy.start_time
            self.end_time = copy.end_time
            self.endian = copy.endian
        else:
            self.data = ""
            self.start_time = 0
            self.end_time = 0
            if littleendian: self.endian = "<"
            else: self.endian = ">"
    
    
    """ Sets the time in ms when the first byte of the packet was received. If no time is given, 
        the current time is used."""
    def set_start_time(self, t = None):
        if t is None: 
            self.start_time = time()
        else:
            self.start_time = t
    
    """ Sets the time in ms when the last byte of the packet was received. If no time is given, 
        the current time is used."""
    def set_end_time(self, t = None):
        if t is None: 
            self.end_time = time()
        else:
            self.end_time = t
    
    """ Swap the bytes of this packet for the bytes given in data """
    def put_data(self, data):
        self.data = data
    
    """ Get the bytes currently stored in this packet """
    def get_data(self):
        return self.data
    
    """ Appends a byte to the current data stored in this packet. 
        The byte should be given in string form, e.g. '\xef' """
    def put_byte(self, b):
        self.data += b
    
    """ Parse the data in this packet into a list of floats """
    def read_float_list(self):
        if not (len(self.data) == 0): 
            if len(self.data)%4 == 0:
                return [struct.unpack(self.endian+"f", self.data[i*4:i*4+4])[0] for i in range(len(self.data)/4)]
            else:
                print "The stored data cannot be parsed into a list of floats."
    
    """ Store a list of floats in this packet """
    def put_float_list(self, lst):
        if type(lst)==list:
            self.data = "".join([struct.pack(self.endian+"f", lst[i]) for i in range(len(lst))])
        else:
            print "arg lst may only be of type list!"

    """ Parse the data in this packet into a list of ints """
    def read_int_list(self):
        if not (len(self.data) == 0): 
            if len(self.data)%4 == 0:
                return [struct.unpack(self.endian+"i", self.data[i*4:i*4+4])[0] for i in range(len(self.data)/4)]
            else:
                print "The stored data cannot be parsed into a list of ints."
    
    """ Store a list of ints in this packet """      
    def put_int_list(self, lst):
        if type(lst)==list:
            self.data = "".join([struct.pack(self.endian+"i", lst[i]) for i in range(len(lst))])
        else:
            print "arg lst may only be of type list!"
    
    """ Store an int in this packet """     
    def put_int(self, integer):
        self.data = struct.pack("<i", integer)
    
    """ Get an int from this packet """     
    def get_int(self):
        self.data = struct.unpack("<i", int)[0]