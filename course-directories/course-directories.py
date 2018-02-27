#!/usr/bin/env python

import os
import argparse

def create_dirs(sections, base):
    for i in range(1, sections+1):
        suffix = ""
        if len(str(i))<2:
            suffix = "0"+str(i)
        else:
            suffix = str(i)
        os.makedirs(base+"/section-"+suffix)
        os.mknod(base+"/section-"+suffix+"/.gitkeep")

parser = argparse.ArgumentParser()
parser.add_argument("sections", help="The number of section directories to create", type=int)
parser.add_argument("base", nargs = '?', default=os.getcwd(), help="The directory to start from.", type=str)
args = parser.parse_args()

if args.sections:
    create_dirs(args.sections, args.base)
