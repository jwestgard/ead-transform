#!/usr/bin/env python3

import sys
import os
import re
import lxml
import json
import argparse

# parse command line arguments
def get_arguments():
    parser = argparse.ArgumentParser(description='Process and validate EAD.')
    parser.add_argument('-i', '--infile')
    parser.add_argument('-o', '--outfile')
    parser.add_argument('-x', action="store_true")
    return parser.parse_args()

# get list of regexes from a file
def load_transformations(transform_file):
    with open(transform_file, "r") as j:
        return json.load(j)

# get list of EAD files
def get_files(root):
    return [os.path.join(root, f) for f in os.listdir(root) if not f.startswith('.') and \
        os.path.isfile(os.path.join(root, f))]
    
# load EAD file
def load_ead_file(filepath):
    with open(filepath, "rb") as f:
        return f.read().decode('utf8', 'ignore')

# write EAD output to new file
def save_ead_file(filename, output_dir, result):
    outfile = os.path.join(output_dir, filename)
    with open(outfile, 'w') as f:
        f.write(result)

# apply the regexes to the input file
def replace(match, replacement, text):
    return re.sub(match, replacement, text)

# apply transformations to a set of files
def transform(files):
    tf = load_transformations(transform_file)
    files_to_process = get_files(input_dir)
    for filepath in files_to_process:
        filename = os.path.basename(filepath)
        print("Loading EAD file: {0}...".format(filename))
        # get ead file
        ead = load_ead_file(filepath)
        # apply regexes one by one to file
        for t in tf:
            print(t["description"])
            for p in t["patterns"]:
                result = replace(p, t["replacement"], ead)
        # store output file
        save_ead_file(filename, output_dir, result)

def main():
    args = get_arguments()
    print(args.infile)

if __name__ == '__main__':
    main()

