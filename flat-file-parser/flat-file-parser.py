#!/usr/bin/env python

#Usage:
# ./flat-file-parser.py <keyfile> <sourceFile>
#That is all

#This will parse a flat-fixed-length-field field into a CSV.
#You will need a keyfile, in CSV form in order to do so.
#The keyfile should have 2 columns, one for the field name
#and another for the length of the field.
#Creating the keyfile is up to you.
#However once completed it's can be easily modified if needed.
#You may or may not need to add a carriage return or new line at the end of the record.
#I should've defined that part as a function to make it easier to do so, 
#but I think most people like a challenge. 
#
#This was written and tested to work with Python 2.7.2


from sys import argv
import codecs
import os
import re

script, keyfile, sourceFile = argv
placeholder = 0
end = 0
count = 0
field = ""
line = []
wild = "a"

#We'll use this function later to read the keyfile into an array
def keylist(infile):
        key = []
        with codecs.open(infile, 'r', encoding="utf-8") as f:
            for i in f:
                i = i.strip()
                i = i.split(',')
                key.append(i)
        return key

#Give the output file a name, with a 'csv' extension
outFile = sourceFile + ".csv"


#If the output file already exists, add another character
#and increment if necessary
while os.path.isfile(outFile):
    wild = chr(ord(wild)+1)
    outFile = sourceFile + wild + ".csv"

#Feed the keyfile into a key list array, should be a bit faster
k = keylist(keyfile)

#Ok, write out the header row, so your CSV can be somewhat intelligible
for i in k:
    with open(outFile,'a') as csv:
        csv.write(i[0]+",")

#Add a new line so your records start on a new row
with open(outFile,'a') as csv:
    csv.write("\n")

#Now we can read the source flat-file and parse the fields as defined in the
#keyfile.
with open(sourceFile) as er8:
        for line in er8:
            for j in k:
                end = placeholder + int(k[count][1])
                field = field + line[(int(placeholder)):(int(end))] + ","
                placeholder = end
                count += 1
            field = field[0:-1]
            #You may or may not need to add the newline character at the end
            #of the field
            #I'll just leave this here in case you need it:
            #
            #field =  field + '\n'
            placeholder = 0
            count = 0
            with open(outFile,'a') as csv:
                csv.write(field)
            field = ""

#Indicate the job is done and tell us the name of the file
print "Completed, please see: ", outFile
