#!/usr/bin/env python3
import argparse
import codecs
import json
import os
import re
from io import BytesIO
import sys
import lxml.etree as ET
import xml.parsers.expat.errors as xerr


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
    print(recursive)
    if recursive is True:
        for (root, dir, files) in os.walk(rootdir):
            result.extend(
                [os.path.join(root, f) for f in files if not f.startswith('.')])
    else:
        result = [os.path.join(rootdir, f) for f in os.listdir(
            rootdir) if not f.startswith('.') and os.path.isfile(
            os.path.join(rootdir, f))]
    return result


#================================================
# verify file encoding and return unicode string
#================================================
def verified_decode(f):
    encodings = ['ascii', 'utf-8', 'windows-1252', 'latin-1']
    print("  Checking encoding...")
    for encoding in encodings:
        bytes = codecs.open(f, mode='r', encoding=encoding, errors='strict')
        try:
            b = bytes.read()
            print('    - {0} OK.'.format(encoding))
            return b
        except UnicodeDecodeError:
            print('    - {0} Error!'.format(encoding))
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
def apply_transformations(xml_as_bytes):
    file_like_obj = BytesIO(xml_as_bytes)
    tree = ET.parse(file_like_obj)
    root = tree.getroot()
    
    
# REQUIRED
#---------------------
    # <container> tags
    file_item_level_dids = [d for d in root.iter('did') if d.getparent().get(
        'level') in ['file', 'item']]
    for did in file_item_level_dids:
        container_types = [c.get('type') for c in d if c.tag == 'container']
        if 'box' not in container_types:
            existing_container = d.find('container/[@type="folder"]')
            box_attribute = existing_container.get('parent')
            new_container = ET.SubElement(d, "container")
            new_container.set('type', 'box')
            
        # existing = d.find('container/[@type="folder"]')
        #    m = re.search(r'box(\d+?)\.', value)
        #    if m:
        #       new = m.group(1)
    
    # incorrect box numbers
    # extent tags 
    
    # add title attribute to dao tags
    for dao in root.iter('dao'):
        parent = dao.getparent()
        unittitle = parent.find('unittitle').text
        dao.set('title', unittitle)
        
    # empty paragraph tags -- regex?
    # replace special characters -- corrected by encoding fix
    
    
# OPTIMIZATION
#---------------------
    # date expressions
    # collection titles
    # dates
    # extents
    # scope and content notes
    
    
# OPTIONAL
#---------------------
    # accession numbers
    # handles
    
    
# ADDITIONAL QUIRKS
#---------------------   
    # stack locations
    # language descriptions
    
    return tree


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
        print("Checking files in folder '{0}'...".format(input_dir))
        files_to_check = get_files_in_path(input_dir, recursive=args.recursive)
    # otherwise, use arguments for files to check
    else:
        input_dir = os.path.dirname(args.files[0])
        print(
            "No input path specified; processing files from arguments...")
        files_to_check = [f for f in args.files]
    # set path for output
    output_dir = args.output
    
    # notify that resume flag is set
    if args.resume:
        print("Resume flag (-r) is set, will skip existing files")
    
    # if transform flag is set, load json transform file
    if args.transform:
        print("Loading regex transformations from file ...")
        transformations = load_transformations(args.transform)
    
    # notify that encoding-check-only flag is set
    if args.encoding is True:
        print("Encoding flag (-e) flag is set, will check encoding only...")

    # loop and process each file
    for n, f in enumerate(files_to_check):
        # set up output paths and create directories if needed
        output_path = os.path.join(output_dir, os.path.relpath(f, input_dir))
        parent_dir = os.path.dirname(output_path)
        if not os.path.isdir(parent_dir):
            os.makedirs(parent_dir)
        
        # summarize file paths to screen
        print("\n{0}. Processing EAD file: {1}".format(n+1, f))
        print("  IN  => {0}".format(f))
        print("  OUT => {0}".format(output_path))
        
        # if the resume flag is set, skip files for which output file exists
        if args.resume:
            if os.path.exists(output_path) and os.path.isfile(output_path):
                print("  Skipping {0}: output file exists".format(f))
                continue
        
        # attempt strict decoding of file according to common schemes
        ead_string = verified_decode(f)
        if not ead_string:
            print("  Could not reliably decode file, skipping...".format(f))
            errors.append("{0} could not be decoded.".format(f))
            continue

        if args.encoding is True:
            # skip rest of loop if encoding-only flag is set and write file
            with open(output_path, 'w') as outfile:
                outfile.write(ead_string)
            continue
        else:
            if args.transform is True:
                # regex transformations
                print("  Applying regexes from file...")
                ead_string = apply_regexes(ead, transformations)
            
            # other transformations
            print("  Applying XML transformations...")
            try:
                ead_tree = apply_transformations(ead_string.encode('utf-8'))
            except ET.ParseError as e:
                print("  {0} is malformed; error code {1} ({2}) at {3})".format(
                    f, e.code, xerr[e.code], e.position))
                errors.append(
                    "{0} is malformed; error code {1} ({2}) at {3})".format(
                        f, e.code, xerr[e.code], e.position))
        
            # write out result
            ead_tree.write(output_path)
    
    # write out error log if any errors occurred
    if errors:
        with open('errors.txt', 'w') as errfile:
            errfile.writelines("\n".join(errors))

if __name__ == '__main__':
    main()

