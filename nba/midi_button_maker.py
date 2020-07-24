# ----------------------------------------------
# Michael Hankowsky  -- 7/22/2020
# midi_button_maker.py 
#

import csv
from telnetlib import Telnet
import time
import struct

# HEY! Change These per team!
csv_filename = "csv/20_TOR.csv"
start_sequence = 2000

start_layer = 413


#These Can Probably Stay the same
cur_button = 0
cur_cue = 0
cur_layer = start_layer
cur_label = 'none'
ma_ip = "192.168.1.141"
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
    tn.write(b"Store Sequence " + enc(sequence) + b" Cue " +str(cue).encode('ascii') + eol)
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

def offthru(tn, sequence, cue):
    tn.write(b"Fixture " + enc(start_layer) + b" thru " +enc(cur_layer) + b"at Preset 1.1" + eol)
    tn.write(b"Store Sequence " + str(sequence).encode('ascii') +b" Cue " + str(cue).encode('ascii')
            + eol)
    time.sleep(0.05)

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

#Assuming all of the values are in the programmer
def saveButton(tn, cur_button, start_sequence, cur_layer, start_layer):
    tn.write(b"Fixture " + enc(start_layer) + b" thru " + enc(cur_layer-1) + b" at Preset 1.12" + eol)
    time.sleep(0.05)
    tn.write(b"Fixture " + enc((((start_layer/100)*100))+91) + b" at Preset 9.1901" + eol)
    time.sleep(0.05)
    tn.write(b"Store Sequence " + enc(int(cur_button) + int(start_sequence)) + b" Cue 0.5" + eol)
    time.sleep(0.1)
    tn.write(b"Fixture " + enc(start_layer) + b" thru " + enc(cur_layer-1) + b" at Preset 1.11" + eol)
    time.sleep(0.05)
    tn.write(b"Store Sequence " + enc(int(cur_button) + int(start_sequence)) + b" Cue 1 " + eol)
    time.sleep(0.1)
    tn.write(b"Fixture " + enc(start_layer) + b" thru " + enc(cur_layer-1) + b" at Preset 1.1" + eol)
    time.sleep(0.05)
    tn.write(b"Fixture " + enc((((start_layer/100)*100))+91) + b" at Preset 9.1902" + eol)
    time.sleep(0.05)
    tn.write(b"Store Sequence " + enc(int(cur_button) + int(start_sequence)) + b" Cue 2 " + eol)
    time.sleep(0.1)
    
def cleanoutCues(tn, sequence, start_layer):
    tn.write(b"Remove Fixture " + enc(start_layer) + b" thru " + enc(start_layer + 5) + eol)
    time.sleep(0.2)
    tn.write(b"Store Sequence " + enc(sequence) + b" Cue 0.5 thru" + eol)
    time.sleep(0.5)
    


tn = Telnet(ma_ip, ma_port) 
line = tn.read_until(b"login !")
time.sleep(0.01)
tn.write(b"Login hank "+eol)

#We have logged in 


#read some info
with open(csv_filename) as csvfile: 
    reader = csv.reader(csvfile)
    #Skip first 2 lines - Header space
    next(reader)
    next(reader)
    for row in reader: 
        #print(row)

        #Is there Midi info? 
        if(row[13] != ''):
            #is it the cur button?  Then just map that bitch 
            if(row[13] == cur_button):
                bankslotmap(tn, cur_layer, row[6], row[7], row[8])
                cur_layer += 1
            #New button! Save the old one first
            if(row[13] != cur_button):
                if(cur_button > 0):
                    saveButton(tn, cur_button, start_sequence, cur_layer, start_layer)
                    print("Stored Button " + cur_button)
                cur_button = row[13]
                cleanoutCues(tn, (int(cur_button)+int(start_sequence)), start_layer)
                cur_layer = start_layer
                clearall(tn)
                bankslotmap(tn, cur_layer, row[6], row[7], row[8])
                cur_layer += 1

#still have one last button to save!
saveButton(tn, cur_button, start_sequence, cur_layer, start_layer)
clearall(tn)

tn.close()    
