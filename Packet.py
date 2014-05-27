import struct
from time import time


class Packet(object):
    """
    This class represents a single packet that can be sent over bluetooth.
    It also supports parsing various types directly into a package. 
    
    The methods for adding data are ordered into put, get, append and pop methods:
        * put-methods swap the bytes currently maintained in the packets for bytes representing 
          the given data. E.g. put_int(4) makes the data in this packet represent only the integer "4"
          and discards any data that was previously stored.
        * get-methods do the opposite: They assume that the packet contains only one datum of the given
          type. E.g. get_int() takes all the data in the packet and parses it into a single int. 
        * append-methods parse the given data into byte format and add it to the current position in the packet
          this way, several types can be added to a packet. 
        * pop-methods read data from the current position and parse it into an instance of the given type 
    
    Packet framing is done independently by the bluetooth connection.
    
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
        self.position = 0 # Read/write byte position
    
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
    
    """
    Returns whether there are still bytes left to be read via the pop-methods
    """
    def has_next(self):
        if self.position < len(self.data):
            return True
        else:
            return False
    
    """ Swap the bytes of this packet for the bytes given in data """
    def put_data(self, data):
        self.data = data
    
    """ Get the bytes currently stored in this packet """
    def get_data(self):
        return self.data
    
    """ Appends a byte to the current data stored in this packet. 
        The byte should be given in string form, e.g. '\xef' """
    def append_byte(self, b):
        self.data += b
        self.position += 1
    
        
    ### Ints ###
    
    """ Store an int in this packet """     
    def put_int(self, integer):
        self.data = struct.pack(self.endian + "i", integer)

    
    """ Get an int from this packet """     
    def get_int(self):
        if len(self.data)==4:
            return struct.unpack(self.endian + "i", self.data)[0]#
        else:
            print "Only 4-byte packets can be parsed into ints."
    
    """ Parse the next bytes into an int. """
    def pop_int(self):
        val = struct.unpack(self.endian+"i", self.data[self.position:self.position+4])[0]
        self.position += 4
        return val
        
    """ Append an int to this packet """     
    def append_int(self, integer):
        self.data += struct.pack(self.endian+"i", integer)
        self.position += 4
    
    ### Chars ###
    """ Store a char in this packet """
    def put_char(self, char):
        self.data = struct.pack(self.endian + "c", char)

    """ Get a char from this packet """     
    def get_char(self):
        return struct.unpack(self.endian + "c", self.data)[0]
    
    """ Parse the next byte into a char. """
    def pop_char(self):
        val = struct.unpack(self.endian+"c", self.data[self.position])[0]
        self.position += 1
        return val
        
    """ Append a char to this packet """     
    def append_char(self, char):
        self.data += struct.pack(self.endian+"c", char)
        self.position += 1
    
    ### Strings ###
    """ Store a string in this packet """     
    def put_string(self, string):
        for character in string:
            self.append_char(character)

    """ Get a string from this packet """     
    def get_string(self):
        res = ""
        for _ in range(len(self.data)):
            res += self.pop_char()
        return res
    
    """ Parse the next bytes into a string. """
    def pop_string(self):
        length = self.pop_int()
        res = ""
        for _ in range(length):
            res += self.pop_char()
        return res
        
    """ Append a string to this packet """     
    def append_string(self, string):
        self.append_int(len(string))
        for ch in string:
            self.append_char(ch)
        
    ### Floats ###
    """ Store a float in this packet """
    def put_float(self, val):
        self.data = ""
        self.append_float(val)
    
    def get_float(self):
        self.position = 0
        return self.pop_float()
    
    """
    Pop a float from the current position
    """            
    def pop_float(self):
        val = struct.unpack(self.endian+"f", self.data[self.position:self.position+4])[0]
        self.position += 4
        return val 
    
    """
    Append a float to this packet
    """
    def append_float(self, val):
        self.data += struct.pack(self.endian+"f", val)
        self.position += 4
        
    
    ### Float lists ###
    
    """
    Pop a float list from the current position
    """
    def pop_float_list(self):
        if not len(self.data) < 4:
            if len(self.data)%4 == 0:  
                # First is the length of the list as an int         
                length = self.pop_int()
                val = [self.pop_float() for _ in range(length)]
                return val
            else:
                print "The stored data cannot be parsed into a list of floats."
    
    """ Append a list of floats to this packet """
    def append_float_list(self, lst):
        if type(lst)==list:
            # First append the length of the list
            self.append_int(len(lst))
            for val in lst:
                self.append_float(val)
        else:
            print "arg lst may only be of type list!"
        
        
    """ Parse the data in this packet into a list of floats """
    def read_float_list(self):
        if not (len(self.data) == 0): 
            if len(self.data)%4 == 0:
                val = []
                self.position = 0
                while self.position<len(self.data):
                    val.append(self.pop_float())
                return val
            else:
                print "The stored data cannot be parsed into a list of floats."
    

    """ Store a list of floats in this packet """
    def put_float_list(self, lst):
        if type(lst)==list:
            for val in lst:
                self.append_float(val)
        else:
            print "arg lst may only be of type list!"


    ### Int lists ###
    
        
    """ Parse the data in this packet into a list of ints """
    def read_int_list(self):
        if not (len(self.data) == 0): 
            if len(self.data)%4 == 0:
                val = []
                self.position = 0
                while self.position<len(self.data):
                    val.append(self.pop_int())
                return val
            else:
                print "The stored data cannot be parsed into a list of ints."
    

    """ Store a list of ints in this packet """
    def put_int_list(self, lst):
        if type(lst)==list:
            for val in lst:
                self.append_int(val)
        else:
            print "arg lst may only be of type list!"
    
    
    """
    Pop an int list from the current position
    """
    def pop_int_list(self):
        if not len(self.data) < 4:
            if len(self.data)%4 == 0:  
                # First is the length of the list as an int         
                length = self.pop_int()
                val = [self.pop_int() for _ in range(length)]
                return val
            else:
                print "The stored data cannot be parsed into a list of ints."
    
    """ Append a list of ints to this packet """
    def append_int_list(self, lst):
        if type(lst)==list:
            # First append the length of the list
            self.append_int(len(lst))
            for val in lst:
                self.append_int(val)
        else:
            print "arg lst may only be of type list!"
        
    
        