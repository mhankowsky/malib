# ----------------------------------------------
# Michael Hankowsky  -- 7/15/2020
# sequence_maker.py 
#
# Create MA Sequence based on CSV file containting looks. 
# Uses Telnet to program. Need MA Up and running. 

import csv
from telnetlib import Telnet
import time
import struct

# HEY! Change These per team!
csv_filename = "10_MIA.csv"
sequence = 1096

start_layer = 101


#These Can Probably Stay the same
cur_cue = 0
cur_layer = 0
cur_label = 'none'
ma_ip = "192.168.1.89"
ma_port = 30000
ma_user = "hank"
ma_prompt = "[Fixture]>"
eol = b"\r\n"



def ma_Ready(tn):
    tn.read_until(ma_prompt.encode('ascii'))

def setdim(tn, layer, value):
    tn.write(b"At " + str(value).encode('ascii') + eol)
    time.sleep(0.1)

def clearall(tn):
    #tn.write(b"clear" + eol + b"clear" + eol + b"clear" + eol)
    tn.write(b"clearall" + eol)

def bankslotmap(tn, layer, bank, slot, mapping):
    tn.write(b"Fixture " + str(layer).encode('ascii') + eol)
    ma_Ready(tn)
    #Bank
    bank = int(bank) + 3000
    tn.write(b"At Preset 9." + str(bank).encode('ascii') + eol)
    #slot
    tn.write(b"Attribute \"Clip Slot\" \r\n")
    tn.write(b"Attribute \"Clip Slot\" At " + str(slot).encode('ascii') + eol)
    #Mapping
    mapping = int(mapping) + 2000
    tn.write(b"At Preset 9." + str(mapping).encode('ascii') + eol)
    time.sleep(0.1)
    
def storecue(tn, sequence, cue):
    tn.write(b"Store Sequence " + str(sequence).encode('ascii') + b" Cue " +
    str(cue).encode('ascii') + eol)
    time.sleep(0.1)

def labelcue(tn, sequence, cue, label):
    tn.write(b"Label Sequence " + str(sequence).encode('ascii') + b" Cue " + str(cue).encode('ascii')
            + b"\"" + label.encode('ascii') + b"\"" + eol)
    
def setCueAppearance(tn, sequence, cue, red, green, blue):
    tn.write(b"Appearance Sequence " + str(sequence).encode('ascii') + b" Cue " +
    str(cue).encode('ascii') + b" /red=" + str(red).encode('ascii') + b" /green=" +
    str(green).encode('ascii') + b" /blue=" + str(blue).encode('ascii') + eol)
    time.sleep(0.1)

def offthru(tn, sequence, cue):
    tn.write(b"Fixture 101 thru 106 at 0" + eol)
    tn.write(b"Store Sequence " + str(sequence).encode('ascii') +b" Cue " + str(cue).encode('ascii')
            + eol)

tn = Telnet(ma_ip, ma_port) 
line = tn.read_until(b"login !")
time.sleep(0.01)
tn.write(b"Login hank "+eol)

#We have logged in 

#read some info
with open(csv_filename) as csvfile: 
    reader = csv.reader(csvfile)
    for row in reader: 
        print(row)
        #We have a new Cue
        if (row[0] != ''): 
            #Store the old cue, dont store if this is the first time we see a cue
            if(cur_cue > 0):
                storecue(tn, sequence, cur_cue)
                labelcue(tn, sequence, cur_cue, cur_label)
                print('storing cue:'+str(cur_cue)+' called:'+cur_label)
            cur_cue += 1
            cur_layer = start_layer
            cur_label = row[0]
            #set our layers to 0 in this cue
            offthru(tn, sequence, cur_cue)
            
            clearall(tn)

            if(row[3] != ''):#Now put this info in the programmer
                bankslotmap(tn, cur_layer, row[2], row[3], row[4])
                setdim(tn, cur_layer, 255)
                cur_layer += 1
                time.sleep(0.1)
                setCueAppearance(tn, sequence, cur_cue, 0, 0, 0)
            else:
                setCueAppearance(tn, sequence, cur_cue, 100, 50, 0)
            
        else:
            bankslotmap(tn, cur_layer, row[2], row[3], row[4])
            setdim(tn, cur_layer, 255)
            cur_layer += 1
            time.sleep(0.1)
            
#We are at the end but we still have not stored the last cue!
storecue(tn, sequence, cur_cue)
labelcue(tn, sequence, cur_cue, cur_label)

time.sleep(0.1)
clearall(tn)

time.sleep(1)

tn.close()    
