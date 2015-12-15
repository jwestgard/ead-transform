#!/usr/bin/env python3

import sys
import os
import re
import lxml
import json
import argparse
import codecs

# parse command line arguments
def get_arguments():
    parser = argparse.ArgumentParser(description='Process and validate EAD.')
    parser.add_argument('-i', '--infile')
    parser.add_argument('-o', '--outfile')
    parser.add_argument('-t', '--transform')
    parser.add_argument('-x', action="store_true")
    return parser.parse_args()

# get list of regexes from a file
def load_transformations(transform_file):
    with open(transform_file, "r") as j:
        return json.load(j)

# get list of EAD files
def get_files(root):
    return [os.path.join(root, f) for f in os.listdir(root) if not f.startswith(
        '.') and os.path.isfile(os.path.join(root, f))]
    
# apply the regexes to the input file
def replace(match, replacement, text):
    return re.sub(match, replacement, text)

def main():
    args = get_arguments()
    files_to_process = get_files(args.infile)
    transformations = load_transformations(args.transform)
    for n, f in enumerate(files_to_process):
        print("{0}. Processing EAD file: {1}".format(n+1,f))
        base = os.path.basename(f)
        outfile = os.path.join(args.outfile, base)
        rc = codecs.open(f, mode='r', encoding='windows-1252', errors='strict')
        with open(outfile, 'w') as of:
            of.write(rc.read())
        

if __name__ == '__main__':
    main()

