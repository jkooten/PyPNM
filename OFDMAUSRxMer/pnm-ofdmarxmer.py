#!/usr/bin/env python3


import binascii
import os
import pandas as pd
from datetime import datetime
import plotly.express as px

typelist, maclist, subczerolist, firstactsubclist, bytelengthlist, timelist, merlist, freqlist = ([], [], [], [],
                                                                                                  [], [], [], [])
exp_file_vers = b'50:4e:4e:69'

directory = "data/"
name = input("Enter name of PNM file (in data directory): ")

if len(name) < 1:
    print("Empty, Incorrect or No PNM file...exiting")
    exit(0)

with open(directory+name, 'rb') as f:
    bytes = f.read()
    a = binascii.hexlify(bytes, ':')
    print(a)
    b = a.split(b':')

    for number in range(0, 4):
        typelist.append(b[number])
    filetype = b":".join(typelist)

    # Major and Minor not supported
    majvers = b[4]
    minvers = b[5]

    # MAC ADDRESS
    for number in range(277, 283):
        maclist.append(b[number])
    macaddress = b":".join(maclist)
    decoded_macaddress = macaddress.decode("utf-8")

    # Timestamp measurement
    for number in range(6, 10):
        timelist.append(b[number])
    time = int(b"".join(timelist), 16)
    readabletime = datetime.fromtimestamp(time)

    # subc zero
    for number in range(286, 290):
        subczerolist.append(b[number])
    subczero = b"".join(subczerolist)

    ##	FIRST ACTIVE SUBCARRIER
    for number in range(290, 292):
        firstactsubclist.append(b[number])
    firstactsubc = b"".join(firstactsubclist)

    ##	SUBCARRIER SPACING
    subcarspacing = int(b[292], 16)

    ##	EXTRACTING AMOUNT OF BYTES DATA
    for number in range(293, 297):
        bytelengthlist.append(b[number])

    bytelength = b"".join(bytelengthlist)
    ofdmblocksize = int(bytelength, 16) * 50000 / 1000000

    # print(f"Filetype:",filetype)

    # Actual MER data in list
    print(int(bytelength, 16))
    for number in range(297, int(bytelength, 16) + 297):
        #print(number)
        #print(int(b[number], 16) / 4)
        merlist.append(int(b[number], 16) / 4)

    # Actual Freqs in list
    for number in range(0, int(bytelength, 16)):
        freq = round(((int(subczero, 16) + int(firstactsubc, 16) * subcarspacing) + (number * 50000)) / 1000000, 2)
        #print(freq)
        freqlist.append(freq)

## MAIN
#
if filetype == exp_file_vers:
    print("Version compare ok")

else:
    print("Version mismatch! expected ", exp_file_vers, ". returned value ", filetype)

print(f"Mac Address DUT:", macaddress, "Timestamp:", time, "==>", readabletime)
print(f"SubCarrier Zero Freq:", int(subczero, 16), "Hz", "; First Active Subcarrier:", int(firstactsubc, 16),
      "; First Active Subcarrier Frequency:",
      int(subczero, 16) + int(firstactsubc, 16) * subcarspacing * 1000, "Hz", "; OFDM BlockSize:", ofdmblocksize, 'MHz',
      "; SubCarrierSpacing:", subcarspacing, "kHz")
print(f"Amount of data Points:", int(bytelength, 16))

print("MinMER:", min(merlist), " MaxMER:", max(merlist), " AvgMER:", round(sum(merlist) / len(merlist), 1),
      " DeltaMER: ", max(merlist) - min(merlist))

# print(macaddress, readabletime, int(subczero, 16)+int(firstactsubc, 16)*subcarspacing*1000, ofdmblocksize,subcarspacing, merlist)

newmerlist = [macaddress, time, (int(subczero, 16) + (int(firstactsubc, 16) * subcarspacing * 1000)) / 1000000,
              ofdmblocksize,
              ((int(subczero, 16) + (int(firstactsubc, 16) * subcarspacing * 1000)) / 1000000) + ofdmblocksize,
              int(bytelength, 16)] + merlist
print(newmerlist)

#print(len(freqlist))
#print(len(merlist))

df = pd.DataFrame({'Frequency': freqlist, 'dB': merlist})
fig = px.bar(df, x='Frequency', y='dB', title=decoded_macaddress + " " + str(readabletime))

fig.update_traces(dict(marker_line_width=0))
# fig.add_hline(y=min(merlist), line_dash="dash", line_color="red")
# fig.add_hline(y=max(merlist), line_dash="dash", line_color="red")
# fig.add_vline(x="992.16")


# fig.add_hrect(y0=max(merlist)-5 , y1= max(merlist)+5, width = 10)
fig.add_hrect(y0=min(merlist), y1=max(merlist), line_width=10, fillcolor="magenta", opacity=0.2,
              annotation_text="DeltaMER: " + str(max(merlist) - min(merlist)) + " dB, Min MER: " + str(
                  min(merlist)) + "dB" + " Max MER: " + str(max(merlist)) + "dB", annotation_position="top left")

#fig.add_vrect(
#    x0=freqlist[merlist.index(min(merlist))] - 5, x1=freqlist[merlist.index(min(merlist))] + 5,
#    label=dict(
#        text="MinMER area",
#        textposition="top center",
#        font=dict(size=10, family="Verdana"),
#    ),
#    fillcolor="turquoise", opacity=0.5,
#    line_width=0,
#)

#fig.add_vrect(
#    # x0=freqlist[merlist.index(max(merlist))]-5, x1=freqlist[merlist.index(max(merlist))]+5,
##    x0=freqlist[merlist.index(max(merlist))], x1=freqlist[merlist.index(max(merlist))] + 5,
 #   label=dict(
#        text="MaxMER area",
#        textposition="top center",
#        font=dict(size=10, family="Verdana"),
#    ),
#    fillcolor="turquoise", opacity=0.5,
##    line_width=0,
#)

fig.write_html(os.getcwd() + name + ".html")
fig.write_image(os.getcwd() + name + ".png")
