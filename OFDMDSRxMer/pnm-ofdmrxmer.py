#!/usr/bin/env python3

import binascii
from datetime import datetime
import matplotlib.pyplot as plt


typelist, maclist, subczerolist, firstactsubclist, bytelengthlist, timelist, merlist, freqlist = [], [], [], [], [], [], [], []
exp_file_vers = b'50:4e:4e:04'

name = input("Enter location of PNM file:")

if len(name) < 1:
    print("Empty, Incorrect or No PNM file...exiting")
    exit(0)

with open (name, 'rb') as f: 
    bytes = f.read()
    a = binascii.hexlify(bytes, ':')
    b = a.split(b':')

    for number in range(0,4):
        typelist.append(b[number])
    filetype = b":".join(typelist)

    # Major and Minor not supported
    # majvers = b[4]
    # minvers = b[5]
    
    #MAC ADDRESS
    for number in range(9,15):
        maclist.append(b[number])
    macaddress = b":".join(maclist)
   
    for number in range(4,8):
        timelist.append(b[number])
    time = int(b"".join(timelist), 16)
    readabletime = datetime.fromtimestamp(time)

    #subc zero
    for number in range(15,19):
        subczerolist.append(b[number])
    subczero = b"".join(subczerolist)
    
    ##	FIRST ACTIVE SUBCARRIER
    for number in range(19,21):
        firstactsubclist.append(b[number])
    firstactsubc = b"".join(firstactsubclist)

    ##	SUBCARRIER SPACING
    subcarspacing = int(b[21], 16)
    
    ##	EXTRACTING AMOUNT OF BYTES DATA
    for number in range(22,26):
        bytelengthlist.append(b[number])
        
    bytelength = b"".join(bytelengthlist)
    ofdmblocksize = int(bytelength, 16)*50000/1000000
    
    #print(f"Filetype:",filetype)
    
    #Actual MER data in list
    for number in range(25,int(bytelength, 16)+25):
        merlist.append(int(b[number], 16)/4)
    
    #Actuakl Freqs in list
    for number in range(0, int(bytelength, 16)):
        freq = round(((int(subczero, 16)+int(firstactsubc, 16)*subcarspacing) + (number*50000))/1000000, 2)
        freqlist.append(freq)
    
        
## MAIN
#
if filetype == exp_file_vers:
    print("Version compare ok")
        
else:
    print("Version mismatch! expected ",exp_file_vers, ". returned value ",filetype)
                    
print(f"Mac Address DUT:", macaddress,"Timestamp:", time, "==>", readabletime )
print(f"SubCarrier Zero Freq:", int(subczero, 16), "Hz", "; First Active Subcarrier:", int(firstactsubc, 16), "; First Active Subcarrier Frequency:", 
      int(subczero, 16)+int(firstactsubc, 16)*subcarspacing*1000, "Hz","; OFDM BlockSize:", ofdmblocksize, 'MHz', "; SubCarrierSpacing:", subcarspacing, "kHz")
print(f"Amount of data Points:", int(bytelength, 16))

print("MinMER:", min(merlist), " MaxMER:", max(merlist), " AvgMER:", round(sum(merlist)/len(merlist),1))

#print(macaddress, readabletime, int(subczero, 16)+int(firstactsubc, 16)*subcarspacing*1000, ofdmblocksize,subcarspacing, merlist)

newmerlist = [macaddress, time, (int(subczero, 16)+(int(firstactsubc, 16)*subcarspacing*1000))/1000000, ofdmblocksize, ((int(subczero, 16)+(int(firstactsubc, 16)*subcarspacing*1000))/1000000) + ofdmblocksize, int(bytelength, 16)] + merlist
print(newmerlist)


plt.figure().set_figwidth(10)
# plotting a bar chart
plt.bar(freqlist, merlist,
        width = 0.5, color = ['green'])

# naming the x-axis
plt.xlabel('Frequency(MHz)')
# naming the y-axis
plt.ylabel('MER(dB)')
# plot title
plt.title('CMDSOfdmMer ' + str(macaddress))
  
# function to show the plot
filename =  name
plt.savefig(filename, dpi=300)
print("Image saved in", filename)