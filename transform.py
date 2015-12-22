#!/usr/bin/env python3
import sys
import os
import re
import lxml
import json
import argparse
import codecs


#==============================
# parse command line arguments
#==============================
def get_arguments():
    parser = argparse.ArgumentParser(description='Process and validate EAD.')
    parser.add_argument('-e', '--encoding', action='store_true',
        help='check encoding only of files in input path')
    parser.add_argument('-i', '--inpath', 
        help='input path of files to be transformed')
    parser.add_argument('-o', '--outpath', required=True,
        help='ouput path for transformed files')
    parser.add_argument('-r', '--resume', action='store_true', 
        help='resume job, skipping files that already exist in outpath')
    parser.add_argument('-t', '--transform', 
        help="file containing regex transformations to apply")
    parser.add_argument('files', nargs='*', help='files to check')
    return parser.parse_args()


#=================================
# get list of regexes from a file
#=================================
def load_transformations(transform_file):
    with open(transform_file, "r") as j:
        return json.load(j)


#=======================
# get list of EAD files
#=======================
def get_files_in_path(root):
    return [f for f in os.listdir(root) if not f.startswith(
        '.') and os.path.isfile(os.path.join(root, f))]


#=====================================
# apply the regexes to the input file
#=====================================
def replace(match, replacement, text):
    return re.sub(match, replacement, text)


def foo():
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
        

'''
1. arguments and options:
    a. input file or path
    b. output path (filename is the same)
    c. option to resume if files exist or overwrite
    d. load regex transformations from external file 
    e. rules for xml transform and validation of EAD
    
2. if file exists, 
3. check encoding and convert if necessary
4. apply regexes from file (if specified)
5. apply transformations
6. write to outfile 

'''

#================
#  main function
#================
def main():
    args = get_arguments()
    outpath = args.outpath
    # get files from inpath
    if args.inpath:
        print("Checking files in {0}...".format(args.inpath))
        files_to_check = get_files_in_path(args.inpath)
        print(files_to_check)
    # otherwise, use arguments as files to check
    else:
        print("No input path specified; processing files passed as arguments...")
        files_to_check = args.files
        print(files_to_check)
    
    # if resume flag set, remove files in outpath from files to check
    if args.resume:
        complete = get_files_in_path(outpath)
        files_to_check = [f for f in files_to_check if f not in complete]
        print(files_to_check)
    
    if args.encoding:
        print("I'm gonna check encoding only.")




if __name__ == '__main__':
    main()

