#!/usr/bin/env python
#A bit rough , needs to add better error handling.
#This will download e-mails from a gmail account and stuff them into an mbox file
#based on the label.
#It will then take all the mboxs and tar them up into a .tgz file

import email
import gzip
import imaplib
import mailbox
import os
import re
import string
import sys
import tarfile
import zlib

#Sets up a few preliminary variables
#Including the e-mail credentials

folder_list = []
username = ""
password = ""
user = username.split('@')[0]
path = "./"+user+"/"

#Creates a folder, named after the user portion of the e-mail account

try:
    os.makedirs(user)
except Exception as e:
    print e

#Creates a tar file which will also be gzipped compressed
tar = tarfile.open(user +".tgz", "w:gz")

#loggs into the gmail account
mail = imaplib.IMAP4_SSL("imap.gmail.com")
mail.login(username, password)

#Creates a list, 'folder_list' with the names of all the labels in the account.
#Later we'll walk through the list and download e-mails based on the labels
folders = mail.list()
for i in folders[1]:
    folder_list.append(i.split('"/"')[-1].strip())

#magic
for j in  folder_list:
    print j
    status, data =  mail.select(j,readonly=True)
    j = j.replace('/', '-')
    print status
    if status == "OK":
        print data
        resp, items = mail.search(None, "All")
        if resp == "OK":
            items[0] = items[0].split()
            print len(items[0])
            if len(items[0]) > 0:
                print "Mailbox name: " + j
                mbox_file = path+j.strip('"')
                mail_items = mailbox.mbox(mbox_file)
                mail_items.lock()
                for i in items[0]:
                    response, message = mail.fetch(i, '(RFC822)')
                    if response == "OK":
                        msg = email.message_from_string(message[0][1])
                        print str(i)+" of "+ str(len(items[0])) 
                        mail_items.add(msg)
                mail_items.close()
                tar.add(mbox_file)
                os.remove(mbox_file)
            else:
                print "No messages here"
    else:
        print "Not a valid mailbox"

tar.close()
mail.logout()
os.removedirs(user)
