#!/usr/bin/env python3

import sys
import os
import re
import lxml
import json

input_dir = sys.argv[2]
output_dir = sys.argv[3]
transform_file = sys.argv[1]

# get list of regexes from a file
def load_transformations(transform_file):
    with open(transform_file, "r") as j:
        return json.load(j)

# get list of EAD files
def list_files(root):
    return [os.path.join(root, f) for f in os.listdir(root) if not f.startswith('.') and \
        os.path.isfile(os.path.join(root, f))]
    
# load EAD file
def load_ead_file(filepath):
    with open(filename, "r") as f:
        return f.read()

# write EAD output to new file
def save_ead_file(filename, output_dir, result):
    outfile = os.path.join(output_dir, filename)
    with open(outfile, 'w') as f:
        f.write(result)

# apply the regexes to the input file
def replace(match, replacement, text):
    return re.sub(match, replacement, text)

def main():
    transformations = load_transformations(transform_file)
    files_to_process = list_files(input_dir)
    for filepath in files_to_process:
        filename = os.path.basename(filepath)
        print("Loading EAD file: {0}...".format(filename))
        # get ead file
        ead = load_ead_file(filepath)
        # apply regexes one by one to file
        for tr in transformations:
            print(tr["description"])
            for p in tr["patterns"]:
                result = replace(p, tr["replacement"], ead)
        # store output file
        outpath = os.path.join(output_dir, filename)
        save_ead_file(filename, outpath, result)

if __name__ == '__main__':
    main()
    
