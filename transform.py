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
    parser.add_argument('-t', '--transform', 
        help="file containing regex transformations to apply")
    parser.add_argument('files', nargs='*', help='files to check')
    return parser.parse_args()


#========================================
# get list of EAD files (input or output)
#========================================
def get_files_in_path(root):
    return [f for f in os.listdir(root) if not f.startswith(
        '.') and os.path.isfile(os.path.join(root, f))]


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
def xml_transformations(filepath):
    tree = ET.parse(filepath)
    root = tree.getroot()
    dsc = root.find('.//archdesc/dsc/[@type="in-depth"]')
    
    result = ET.tostring(root, encoding='utf-8')
    return result


#================
#  main function
#================
def main():
    border = "=" * 19
    print("\n".join(['', border, "| EAD Transformer |", border]))
    args = get_arguments()
    output_dir = args.output
    # get files from inpath
    if args.input:
        input_dir = args.input
        print("Checking files in {0}...".format(input_dir))
        files_to_check = get_files_in_path(input_dir)
    # otherwise, use arguments for files to check
    else:
        print(
            "No input path specified; processing files from arguments...")
        files_to_check = [os.path.basename(f) for f in args.files]
        input_dir = os.path.dirname(args.files[0])
    # if resume flag set, remove files in outpath from files to check
    if args.resume:
        complete = get_files_in_path(output_dir)
        files_to_check = [f for f in files_to_check if f not in complete]
    # if transform flag is set, load json transform file
    if args.transform:
        print("Loading regex transformations from file ...")
        transformations = load_transformations(args.transform)
    # if encoding flag is set
    if args.encoding:
        print("-e flag set, will check encoding only...")

    # loop and process each file
    for n, f in enumerate(files_to_check):
        print("\n{0}. Processing EAD file: {1}".format(n+1,f))
        input_path = os.path.join(input_dir, f)
        print("   IN => {0}".format(input_path))
        output_path = os.path.join(output_dir, f)
        print("   OUT => {0}".format(output_path))
        decoded_text = verified_decode(input_path)
        if not decoded_text:
            print("Could not reliably decode file, skipping...".format(f))
            continue
        if not args.encoding:
            # regex transformations
            print("Applying regexes...")
            decoded_text = apply_regexes(decoded_text, transformations)
            # other transformations
            print("Applying XML transformations...")
            # write out the decoded text to the output file
            with codecs.open(output_path, 'w', encoding='utf8') as outfile:
                outfile.write(decoded_text)
            transformed_text = xml_transformations(output_path)

        else:
            # write out result
            with codecs.open(output_path, 'w', encoding='utf8') as outfile:
                outfile.write(decoded_text)


if __name__ == '__main__':
    main()

