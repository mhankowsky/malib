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
csv_filename = "csv/02_BOS.csv"
sequence = 296

start_layer = 101


#These Can Probably Stay the same
cur_cue = 0
cur_layer = 0
cur_label = 'none'
ma_ip = "192.168.1.92"
ma_port = 30000
ma_user = "hank"
ma_prompt = "[Fixture]>"
eol = b"\r\n"


def enc(var):
    return str(var).encode('ascii')

def ma_Ready(tn):
    tn.read_until(ma_prompt.encode('ascii'))

def setdim(tn, layer, value):
    tn.write(b"At " + str(value).encode('ascii') + eol)
    time.sleep(0.1)

def clearall(tn):
    #tn.write(b"clear" + eol + b"clear" + eol + b"clear" + eol)
    tn.write(b"clearall" + eol)
    time.sleep(0.1)

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
    time.sleep(0.05)
    
def storecue(tn, sequence, cue):
    tn.write(b"Store Sequence " + str(sequence).encode('ascii') + b" Cue " +
    str(cue).encode('ascii') + eol)
    time.sleep(0.1)

def labelcue(tn, sequence, cue, label):
    tn.write(b"Label Sequence " + str(sequence).encode('ascii') + b" Cue " + str(cue).encode('ascii')
            + b"\"" + label.encode('ascii') + b"\"" + eol)
    time.sleep(0.1)
    
def setCueAppearance(tn, sequence, cue, red, green, blue):
    tn.write(b"Appearance Sequence " + str(sequence).encode('ascii') + b" Cue " +
    str(cue).encode('ascii') + b" /red=" + str(red).encode('ascii') + b" /green=" +
    str(green).encode('ascii') + b" /blue=" + str(blue).encode('ascii') + eol)
    time.sleep(0.1)

def offthru(tn, sequence, cue, start_layer, cur_layer):
    tn.write(b"Fixture " + enc(start_layer) + b" thru " + enc(cur_layer) + b" at Preset 1.1" + eol)
    tn.write(b"Store Sequence " + str(sequence).encode('ascii') +b" Cue " + str(cue).encode('ascii')
            + eol)

def atFull(tn, layer):
    tn.write(b"Fixture " + enc(layer) + b" at Preset 1.11" + eol)
    time.sleep(0.05)

def blowoutSequence(tn, sequence):
    tn.write(b"Store Sequence " + enc(sequence) + b" Cue 0.5 /o /nc" + eol)
    tn.write(b"Delete Sequence " + enc(sequence) + b" Cue 1 thru /nc" + eol)
    time.sleep(0.1)

def unBlockSequence(tn, sequence):
    tn.write(b"Unblock Sequence " + enc(sequence) + b" Cue 1 thru" + eol)
    time.sleep(0.1)

tn = Telnet(ma_ip, ma_port) 
line = tn.read_until(b"login !")
time.sleep(0.01)
tn.write(b"Login hank "+eol)

#We have logged in 

#Blow out sequence
blowoutSequence(tn, sequence)

#read some info
with open(csv_filename) as csvfile: 
    reader = csv.reader(csvfile)
    #Skip first 2 lines - Header space
    next(reader)
    next(reader)
    for row in reader: 
        print(row)
        #Grab the new category
        if (row[0] != ''):
            cur_category = row[0]
        #IF we dont have a file name and look we skip!
        if (row[2] == '' and row[1] == ''):
            continue
        #We have a new Cue
        if (row[1] != ''): 
            #Store the old cue, dont store if this is the first time we see a cue
            if(cur_cue > 0):
                storecue(tn, sequence, cur_cue)
                labelcue(tn, sequence, cur_cue, cur_label)
                print('storing cue:'+str(cur_cue)+' called:'+cur_label)
            cur_cue += 1
            offthru(tn, sequence, cur_cue, start_layer, cur_layer)
            cur_layer = start_layer
            cur_label = cur_category[0:3] + " " + row[1]
            #set our layers to 0 in this cue
            
            clearall(tn)

            if(row[6] != ''):#Now put this info in the programmer
                bankslotmap(tn, cur_layer, row[6], row[7], row[8])
                atFull(tn, cur_layer)
                cur_layer += 1
                time.sleep(0.1)
                setCueAppearance(tn, sequence, cur_cue, 0, 0, 0)
            else:
                setCueAppearance(tn, sequence, cur_cue, 100, 50, 0)
            
        else:
            bankslotmap(tn, cur_layer, row[6], row[7], row[8])
            atFull(tn, cur_layer)
            cur_layer += 1
            time.sleep(0.1)
            
#We are at the end but we still have not stored the last cue!
storecue(tn, sequence, cur_cue)
labelcue(tn, sequence, cur_cue, cur_label)

time.sleep(0.1)
clearall(tn)
time.sleep(0.1)
unBlockSequence(tn, sequence)

time.sleep(1)

tn.close()    
