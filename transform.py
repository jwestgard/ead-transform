#!/usr/bin/env python3
import sys
import os
import re
import xml.etree.ElementTree as ET
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
    parser.add_argument('-i', '--input', 
        help='input path of files to be transformed')
    parser.add_argument('-o', '--output', required=True,
        help='ouput path for transformed files')
    parser.add_argument('-r', '--resume', action='store_true', 
        help='resume job, skipping files that already exist in outpath')
    parser.add_argument('-R', '--recursive', action='store_true', 
        help='recursively process files starting at rootdirectory')
    parser.add_argument('-t', '--transform', 
        help="file containing regex transformations to apply")
    parser.add_argument('files', nargs='*', help='files to check')
    return parser.parse_args()


#========================================
# get list of EAD files (input or output)
#========================================
def get_files_in_path(rootdir, recursive):
    result = []
    if recursive is True:
        for (root, dir, files) in os.walk(rootdir):
            result.extend(
                [os.path.join(root, f) for f in files if not f.startswith('.')])
    else:
        result = [f for f in os.listdir(rootdir) if not f.startswith(
            '.') and os.path.isfile(os.path.join(rootdir, f))]
    return result


#================================================
# verify file encoding and return unicode string
#================================================
def verified_decode(f):
    encodings = ['ascii', 'utf-8', 'windows-1252', 'latin-1']
    print("Checking encoding...")
    for encoding in encodings:
        bytes = codecs.open(f, mode='r', encoding=encoding, errors='strict')
        try:
            b = bytes.read()
            print('  - {0} OK.'.format(encoding))
            return b
        except UnicodeDecodeError:
            print('  - {0} Error!'.format(encoding))
    return False


#=================================
# get list of regexes from a file
#=================================
def load_transformations(transform_file):
    with open(transform_file, "r") as f:
        return json.load(f)


#==================================
# apply an individual find/replace
#==================================
def replace(match, replacement, text):
    return re.sub(match, replacement, text)


#==============================================
# apply the batch of regexes to the input file
#==============================================
def apply_regexes(text, transformations):
    for t in transformations:
        print(t['description'])
        match = t['pattern']
        replacement = t['replacement']
    return re.sub(match, replacement, text)


#=================================================
# apply the xml transformations to the input file
#=================================================
def apply_transformations(text):
    root = ET.fromstring(text)
    unitdates = root.findall('.//archdesc/did/unitdate')
    for u in unitdates:
        print(u.tag, u.attrib, u.text)
    result = ET.tostring(root, encoding='utf-8')
    return result


#================
#  main function
#================
def main():
    args = get_arguments()
    border = "=" * 19
    print("\n".join(['', border, "| EAD Transformer |", border]))
    errors = []
    
    # get files from inpath
    if args.input:
        input_dir = args.input
        print("Checking files in {0}...".format(input_dir))
        files_to_check = get_files_in_path(input_dir, recursive=args.recursive)
    # otherwise, use arguments for files to check
    else:
        input_dir = os.path.dirname(args.files[0])
        print(
            "No input path specified; processing files from arguments...")
        files_to_check = [os.path.basename(f) for f in args.files]
    # set path for output
    output_dir = args.output
    
    # if resume flag set, remove files in outpath from files to check
    if args.resume:
        existing_files = get_files_in_path(output_dir, recursive=args.recursive)
        files_to_check = [f for f in files_to_check if os.path.join(
            os.path.relpath(f, input_dir), output_dir) not in existing_files]
    
    # if transform flag is set, load json transform file
    if args.transform:
        print("Loading regex transformations from file ...")
        transformations = load_transformations(args.transform)
    
    # if encoding flag is set
    if args.encoding is True:
        print("-e flag set, will check encoding only...")

    # loop and process each file
    for n, f in enumerate(files_to_check):
        # set up output paths and create directories if needed
        output_path = os.path.join(output_dir, os.path.relpath(f, input_dir))
        parent_dir = os.path.dirname(output_path)
        if not os.path.isdir(parent_dir):
            os.makedirs(parent_dir)
        
        # summarize file paths to screen
        print("\n{0}. Processing EAD file: {1}".format(n+1, f))
        print("   IN => {0}".format(f))
        print("   OUT => {0}".format(output_path))
        
        # attempt strict decoding of file according to common schemes
        ead = verified_decode(f)
        if not ead:
            print("Could not reliably decode file, skipping...".format(f))
            errors.append("{0} could not be decoded.".format(f))
            continue

        if args.encoding is True:
            # skip rest of loop if encoding-only flag is set
            continue
        else:
            if args.transform is True:
                # regex transformations
                print("Applying regexes...")
                ead = apply_regexes(ead, transformations)
            else:
                # other transformations
                print("Applying XML transformations...")
                try:
                    ead = apply_transformations(ead)
                except ET.ParseError as e:
                    errors.append("{0} malformed ({1} at {2})".format(
                        f, e.code, e.position))
                        
        # write out result
        with open(output_path, 'w') as outfile:
            outfile.write(str(ead))

if __name__ == '__main__':
    main()

