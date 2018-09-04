# piTalk
Files for Raspberry Pi to stream Data

This program allows for data to be sent/streamed wirelessly from a Raspberry Pi to a computer. The program can handle any combination of boolean, integer, float, and string data types. Data and can be sent either independently as a single value or in any combination of multi-type n-dimensional lists. 

If sending lists, they must be formatted so that each row has an equal number of elements. For example: 

`[[1, 2, 3, 4], [5, 6, 7, 8]]`

is okay.  However: 

`[[1, 2, 3, 4], [5, 6], [7, 8]]`

is not okay.

---

## How to use
The library contains the functions described below:

### sendData( data, showRawData=False):
Inputs: the data you would like to send, either an individual value or a multi-type n-dimensional list.

Optional: showRawData will print the data of some intermediate steps to help with potential debugging.  Defaults to False.


### sendMap( studentMap):
Inputs: A student map array that is to be plotted by a corresponding program on the recieving computer.

This function is used exclusively with Semester 2 Project 3

### sendMapFile( studentMap, showRawData=False):
Inputs: A student map file that is to be plotted by a corresponding program on the recieving computer.

This function is used exclusively with Semester 2 Project 3
