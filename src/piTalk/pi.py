import socket 
import struct
import time
import sys
from numpy import array, zeros
from binascii import crc_hqx

class PiTalk():

  # The init function will create the socket connection with the computer
  def __init__(self, host):
    # The packet size of each packet sent can easily be adjusted with this variable
    # This much match the buffer size declared in the program recieving the message
    self.buffer = 1024
    self.checkCode = struct.pack('H', 0x55AA)
    self.resendCount = 0
    
    port = 12345 #Arbitrary, will be reassigned
    print('Attempting to connect to ', host)
    sys.stdout.flush()
  
    try:
      self.userSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.userSocket.connect((host, port))
    except KeyboardInterrupt:
      sys.exit("\nUser terminated connection attempt.")
  
    print('\r', '\bConnected to:  ', host)
    print('Press [ctrl + C] to stop\n')
    
  
  # Returns the letter that represents the data type passed to it
  def _getFormat( self, x):
    if (type(x) is int):
      return 'i'
    elif (type(x) is float):
      return 'f'
    elif (type(x) is str):
      return 's'
    elif (type(x) is bool):
      return '?'
    else:
      return 's'
  

  # Takes a multi-dimensional list and flattens it sequentially to a 1D list
  def _flatten( self, array):
    return sum( ([x] if not isinstance(x, list) else self._flatten(x) for x in array), [] )
  
  
  # Generates the format string, a symbolic representation of the data
  # based on the data type of teach element
  def _getFmtStr( self, data):
    npy = data
    fmtString = ""
    
    # If it's a list, must get dimensions then flatten and analyze array
    if ( type(data) is list):
      dim = array(npy).shape
      # Record a space for the number of dimensions
      fmtString += 'i'

      # Record a space for the size of each dimension
      for i in dim:
        fmtString += 'i'
        
      # Dimensions have been recorded, can now flatten and analyze the data sequentiall
      d = self._flatten(data)
      prevType  = self._getFormat(d[0])
      count = 1 # Records the number of consecutive occurances of a data type
      first = True
      
      # Iterate through the data record the data types
      for i in d:
        if (first):
          first = False
          # Initial values have already been recorded, simply continue
          if (prevType == 's'):
            count = len(i)
          continue

        if (self._getFormat(i) == 's'):
          # if the element is a string, must record the length of the string for this element (already recorded in prev iteration)
          pass
        elif (self._getFormat(i) == prevType):
          # Sequential data types are counted together to reduce the length of the format string for large lists
          count += 1
          continue

        # append the number of occurances of the type
        fmtString += str(count) + prevType

        # Record the current data format for comparison of the next data
        prevType  = self._getFormat(i)

        # If a string, record the length
        if (prevType == 's'):
          count = len(i)
        else:
          count = 1

      # At the very end, add the last remaining data format
      fmtString += str(count) + prevType

    # If the data is not a list, do not include integers in the format string
    elif (type(data) is str):
      for l in range(len(data)):
        fmtString += self._getFormat(data)
    else:
      fmtString = self._getFormat(data)

    return fmtString
  
  
  # Uses the format string to determine where to split the data based on packet size
  # Splits the data into a list with each element as a packet.
  # Also converts the data into binary format for sending
  def _defineSendPkts( self, formatStr, inpt):
    # Look-up table for data size
    dataSize = { 'i':4 , 'f':4, 's':1, '?':1 }
    npy = inpt
    send = bytes() # Defines an empty binary send array
    if (type(inpt) is list):
      inpt = self._flatten(inpt)
    else:
      return [formatStr], [[inpt]], send
    
    message = []
    format = []
    length = 0
    dataIndex = 0
    dataStart = 0
    fmtStart = 0
    fmtEnd = 1
    startMsg = []
    i = 0
    size = 0
    strcnct = ''

    # Record how many dimensions the array has and add to the send byte array
    dim = array(npy).shape
    send += struct.pack('i', len(dim))
    size += dataSize['i']
    i += 1

    # Record the length of each dimension and add to the send byte array
    for k in dim:
      send += struct.pack('i', k)
      size += dataSize['i']
      fmtEnd += 1
      i += 1

    # Begin iterating through the format string to determine how to pack the data
    while (i < len(formatStr)):

      # Since analyzed 1 digit at a time, this accounts for 2+ digit numbers
      if (formatStr[i].isdigit()):
        length = 10 * length + int(formatStr[i])

      # If not a number, then a data type with which package the data is found
      else:
        if (length == 0):
          length = 1

        # Incriment the size of the packet so far according to the data type
        size += length * dataSize[ formatStr[i] ]

        # If this size exceeds the buffer size, it must be split into a new packet.
        if (size > self.buffer):
          if (length > 1):
            firstPacket  = int( (length * dataSize[formatStr[i]] - (size - self.buffer)) / dataSize[formatStr[i]])
            if ((formatStr[i] == 's') and (firstPacket != 0)):
                # If the data is a string, we cut the string so that it fills up the packet.
                # This ensures that even if a string is longer than the buffer it can still be split up and sent.
                message.append(self._flatten([inpt[dataStart:dataIndex], str(inpt[dataIndex][:firstPacket])]))
                #print('message appended! 1-> ', message)
                strcnct = '-'

                # Insert the second part of the string as a new element so that it is the next element evaluated
                inpt.insert(dataIndex+1, inpt[dataIndex][firstPacket:])
                
                # Set the start of the next packet to be at this next element
                dataStart = dataIndex+1
                # If you don't have this here, it doesn't always work
                if (formatStr[-1] != 's'):
                  dataIndex = dataIndex - length + 1

            else:
                # If the data is not a string, it shouldn't be split in half and it is simply split between the whole inpt elements
                message.append(self._flatten(inpt[dataStart:(dataIndex + firstPacket)]))
                #print('message appended! 2-> ', message)
                strcnct = ''
                
                # Set the start of the next packet to be sent from the end of the first packet
                dataStart = dataIndex + firstPacket
                if (formatStr[-1] == 's'):
                  dataIndex = dataIndex + firstPacket - 1
                else:
                  dataIndex = dataIndex + firstPacket - length
                
            # Reset the size to 0 for the next packet since the remaining data is still to come
            size = 0

            # Also save the format of the new packet so that it may be packaged correctly
            format.append( str(formatStr[fmtStart:fmtEnd] + str(firstPacket) + formatStr[i] + strcnct))
            # Re-define the format string so that it only contains the remaining data
            formatStr = str( str(length - firstPacket) + formatStr[i] + formatStr[i+1:])
            fmtStart = 0
            i = -1
            
          else:
            # If length is only 1, simply divide right before the current element.  No computations on where to split are necessary.
            message.append(self._flatten(inpt[dataStart:dataIndex]))
            #print('message appended! 3-> ', message)

            dataStart = dataIndex

            # append until 1 before the current element to account for the digit stating a length of 1
            format.append( str(formatStr[fmtStart:i-1]))

            # The next iteration will start on the next data element, so update the size
            size = dataSize[formatStr[i]]
            fmtStart = i-1
            
        if ((formatStr[i] == 's')):
            # If a string, only incriment by 1 as a string is only 1 element in an array regardless of the length
            dataIndex += 1
        else:
            dataIndex += length

        # Reset the length
        length = 0
        # set the last valid fmt character to be i (ending list index ranges are non-inclusive, so i+1)
        fmtEnd = i+1
  
      i += 1

    # finally, append the remaining message and format
    message.append(self._flatten(inpt[dataStart:]))
    #print('message appended! 4-> ', message)
    format.append(str(formatStr[fmtStart:]))

    return format, message, send


  # Combines the format defined by _defineSendPkts() and combines and send it
  def _packNsendFormat(self, formatList):
    fmt = ','.join(str(x) for x in formatList)
    
    # Change the fmtString to a byte string and pack it
    send = fmt.encode()
    size = int(((len(send)+4) / self.buffer) + 1)   # number of packets the format string requires with the given buffer size

    i = 0
    message = bytes()
    message += struct.pack("I", size)
    first = 1
    # iterate through all but the last packet
    while (size > 1):
      # pack up one packet's worth of data (leaving room for the packed 'size' for the first round through)
      message += struct.pack("%ds" %(self.buffer-first*4), send[i:i+self.buffer- first*4])
      message += self.checkCode
      
      self.userSocket.sendall(message)
      recvMsg = self.userSocket.recv(self.buffer)
      if (recvMsg != b"Valid."):
        raise packetException("Communication Error: Packet was not validated by client.")
      
      i += self.buffer -first*4
      size -= 1
      first = 0
      message = bytes()
      
    message += struct.pack("%ds" %len(send[i:]), send[i:])
    message += self.checkCode

    # Send to the client
    self.userSocket.sendall(message)
    recvMsg = self.userSocket.recv(self.buffer)
    if (recvMsg != b"Valid."):
      raise packetException("Communication Error: Packet was not validated by client.")
    
    return fmt
    
  
  # Takes predefined data packets and sends them to the client
  def _packNsendData( self, dataPkts, send):
    # Iterate through the format/message list. Each element is a packet
    for i in range(len(dataPkts)):
      # Iterate throgh the message (data) to sequentially pack and append it to a byte object to send
      for msg in dataPkts[i]:
        if (self._getFormat(msg) == 's'):
          # If a string, must find the length and first convert to a byte string before packing
          l = len(msg)
          msg = msg.encode()
          send += struct.pack("%ds" %l, msg)
        else:
          send += struct.pack(self._getFormat(msg), msg)

      # Append a check byte to assure successful delivery
      send += self.checkCode
      # Send to client
      self.userSocket.sendall(send)
      recvMsg = self.userSocket.recv(self.buffer)
      if (recvMsg != b"Valid."):
        raise packetException("Communication Error: Packet was not validated by client.")
      
      # Reset the send varaible to an empty byte object
      send = bytes()
    
  
  # The main function used to send data. Combines all of the above private functions into
  # one easy to use function.
  def sendData( self, data, showRawData=False):
    try:
      if (showRawData):
        print("\n\nBuffer Size: ", self.buffer, "\nSending: ")
        try:
          [print(r) for r in data]
        except:
          print(data)
          
      # Find the format string for the given data
      formatStr = self._getFmtStr( data)
      # Using the format string, split and define the packets that will be sent
      formatStr, sendData, begin = self._defineSendPkts( formatStr, data)
      
      if (showRawData):
        print("Final Format: ")
        [print(f) for f in formatStr]
        print("Final Message: ")
        try:
          [print(m) for m in sendData]
        except:
          print(sendData)

      # Encode and send the data
      self._packNsendFormat( formatStr)
      self._packNsendData( sendData, begin)
      return 1
    
    except BrokenPipeError:
      self.userSocket.close()
      sys.exit('Connection has been lost.')
    except ConnectionResetError:
      self.userSocket.close()
      sys.exit('Connection closed by peer.')
    except KeyboardInterrupt:
      self.userSocket.close()
      sys.exit('User terminated connection during send attempt.')
    #except packetException:
    #  print("Resending...")
    #  self.resendCount += 1
    #  if (self.resendCount < 10):
    #    self.sendData( data, showRawData=showRawData)
    #    self.resendCount = 0
    #  else:
    #    print('Connection with client lost.')
    #    return 0
  
  
  # Used for sending map arrays in association with Sem 2 Proj 3
  def sendMap( studentMap):
    if not(type(studentMap) is list) and not(type(studentMap[0]) is list):
      print("ERROR: Map must be of 2D list type.")
      return -1
  
    send = [zeros(len(studentMap[0])).tolist()]
    send[0][1] = 'Sample Header - Team_99'
    for row in studentMap:
      send.append(row)
    
    sendData( send)
  
  
  # Used for sending map files in association with Sem 2 Proj 3
  def sendMapFile( studentMap, showRawData=False):
    mapLength = len(studentMap[-1])
    sendMap = []  
  
    for i in range(len(studentMap)):
      if (i < 6):
        temp = zeros(mapLength).tolist()
        temp = [int(t) for t in temp]
        if (i == 4):
          try:
            temp[0] = str(studentMap[i][0] + studentMap[i][1])
          except:
            temp[0] = studentMap[i][0]
        else:
          temp[0] = studentMap[i][0]
        sendMap.append(temp)
      else:
        if (len(studentMap[i]) != mapLength):
          print("MAP ERROR: Map data must have rows that are all the same length")
          return 0
        sendMap.append(studentMap[i])
  
    sendData( sendMap, showSendData=showData)
    return 1


class packetException(Exception):
  pass