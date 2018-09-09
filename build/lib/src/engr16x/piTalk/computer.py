# Library file on the Computer.
# Must be in the same directory as any file using it's functions.

import socket
import struct
import sys
from threading import Thread, Event
from binascii import crc_hqx


class CompTalk:
  def __init__(self, host):
    # Variables that define the communication
    self.buffer = 1024
    self.CRCValue = 0x61
    
    # The __init__ mainly searches for and establishes the connection
    port = 12345  # Arbitrary, will be reassigned by the connection.
    print('Attempting to connect using ', host)
    try:
      soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      soc.bind((host, port))
    except:
      sys.exit('Client IP Address was not valid. Check that the correct IP address was entered')
    
    try:
      print('Waiting for connection from host')
      soc.listen(1)
      self.conn, addr = soc.accept()
    except:
      print('Conneciton request timed out.')
    
    print('Connected by ', addr[0])
    print('Press [ctrl + C] on Pi to stop\n')
    
    self.dataStream = []
    
  
  
  def _flatten( self, array):
    # Takes a multi-dimensional array and flattens it to 1 dimension
    return sum( ([x] if not isinstance(x, list) else self._flatten(x) for x in array), [] )
    
  def _convert2list( self, list):
    # Unpacks and structures the sent data into a list of the correct number of rows/columns/dimensions
    dim = []
    
    # Extract the dimensions of the array
    # Format: [Number of Dimensions, Length of Dim1, Length of Dim2, ...Length of DimN, ...Data to be unpacked...]
    dimLength = list[0]
    for i in range(dimLength):
      # Add 1 to skip the first element which defines dim length
      dim.append(list[i + 1])
    
    values = list[dimLength+1:]
    
    # Define an interator and build structure the remaining data based on the dimensions extracted
    self._iterator = 0
    return self._recursiveBuild( dim, values)
  
  
  def _recursiveBuild( self, dimensions, data):
    final = []
    
    # If there's still remaining dimensions, must continue unpacking
    if (len(dimensions) > 1):
      for i in range(dimensions[0]):
        final.append(self._recursiveBuild( dimensions[1:], data))
    # If you have all the dimensions, begin building the data
    else:
      self._iterator += dimensions[0]
      return data[self._iterator-dimensions[0]:self._iterator]
    
    # Once finished, return the resulting array
    return final
      
  
  def _unpackFmt( self, data):
    # Unpacks the format string for a packet
    fmtString = ""
    numPackets = struct.unpack("I", data[:4])[0]
    
    # Wait to recieve all of the packets
    while(numPackets > 1):
      d = self._recvAndCheck()
      if not data: return 0
      
      data = data + d
      numPackets -= 1
    
    # combine the data into one string
    for i in range(4, len(data)):
      fmtString = str(fmtString + chr(data[i]))
    
    # Comma's will denote new packets, so split based on those
    return fmtString.split(',')
  
    
  def _unpackData( self, formatStr, data):
    # Unpacks the recieved raw data based on the format string
    dataSize = { 'i':4, 'f':4, 's':1, '?':1 }
    
    numPackets = len(formatStr)
    
    content = []
    p = 0 # Packet number 
    d = 0
    
    while(p < numPackets):
      length = 0
      firstElement = True
      isList = False
      isString = False
      i = 0 # index in format string
      d = 0 # index in data recieved
      
      # Iterate through all expected packets
      while (i < len(formatStr[p])):
        
        # Since anayzed 1 digit at a time, this accounts for 2+ digit numbers
        if (formatStr[p][i] == '-'):
          break
        if (formatStr[p][i] == '0'):
          break
        if (formatStr[p][i].isdigit()):
          length = 10 * length + int(formatStr[p][i])
          isList = True
        
        # If not a digit then a data type was identified and something needs to be unpacked
        else:
          if (length == 0):
            length = 1
          
          if (formatStr[p][i] == 's'):
            isString = True
            string = ''
            # append all of the characters for this entry to 1 string variable
            for temp in range(length):
              string = str(string + chr(data[p][d]))
              d += 1 # move to next data entry
            if (isList and firstElement and (formatStr[p-1][-1] == '-')):
              content[-1] = str(content[-1] + string)
            else:
              content.append(string)
            
          else:
            # Append the next length of data to the resulting content
            for temp in range(length):
              content.append( struct.unpack(formatStr[p][i], data[p][d:(d+dataSize[formatStr[p][i]])])[0])
              d += dataSize[formatStr[p][i]]
        
          length = 0
          firstElement = False
          
        i += 1
      p += 1
    
    if (isList):
      final = self._convert2list(content)
    elif isString:
      final = ''
      for t in content:
        final += t
    else:
        final = content[0]
    
    return final
    
  
  def _recvAndCheck( self):
    # Check's the sync byte to make sure the packet was fully recieved.
    # Send a response accordingly
    d = self.conn.recv(self.buffer + 2)
    
    if (struct.unpack('H', d[-2:])[0] == 0x55AA):
      self.conn.sendall(b"Valid.")
      return d[:-2]
    else:
      self.conn.sendall(b"Invalid.")
      raise packetException('Communication Error: Packed could not be validated')
  
  
  def getData( self, showRawData=False):
    # Waits for and recieves all data in a communication attempt
    #try:
      # Wait for the data
      data = self._recvAndCheck()
      
      # Get the format string
      if not data: return 0
      formatString = self._unpackFmt( data)
      
      # Recieve the rest of the packets if any, as identified in the format string
      payload = []
      for i in range(len(formatString)):
        d = self._recvAndCheck()
        if not data: return 0
        
        payload.append( d)
      
      # Unpack the data
      content = self._unpackData( formatString, payload)
      
      # Print raw data if requested by the user
      if (showRawData):
        print("\nBuffer Size: ", self.buffer, "\nFormat: ")
        try:
          [print(f) for f in formatString]
        except:
          print(formatString)
          
        print("Recieved:")
        try:
          [print(str(c)) for c in content]
        except:
          print(content)
      
      return content
      
    #except packetException:
    #  print('Listening for resent data...')
    #  self.getData( showRawData=showRawData)

  
  def streamData( self, showRawData=False):
    # Creates a continuously refreshing data stream
    self.dataBuffer = []
    self.dataStream = []
    self.receiveEvt = Event()
    self.streaming = True
    
    self.listen = Thread(target=self._waitForStream)
    self.listen.daemon = True
    self.listen.start()
    
    return 1


  def _waitForStream( self):
    # Waits for the next communication in a data stream
    print('Listening for data...')
    try:
      while self.streaming:
        d = self.getData()
        # print(d)
        self.dataStream.append(d)
        
    except KeyboardInterrupt:
      thread.exit()
      return
    except BrokenPipeError:
      thread.exit()
      return

class packetException(Exception):
  pass