#!/usr/bin/env python3
# -*- coding: utf8 -*-

import argparse
import codecs
import csv
from io import BytesIO
import json
import logging
import lxml.etree as ET
import os
import re
import sys
import xml.parsers.expat as xerr


#========================================
# get list of EAD files (input or output)
#========================================
def get_files_in_path(rootdir, recursive):
    result = []
    
    if recursive is True:
        print('Traversing recursively...')
        for (root, dir, files) in os.walk(rootdir):
            result.extend(
                [os.path.join(root, f) for f in files if not f.startswith('.')])
    else:
        print('Searching top folder only...')
        result = [os.path.join(rootdir, f) for f in os.listdir(
            rootdir) if not f.startswith('.') and os.path.isfile(
            os.path.join(rootdir, f))]

    print('Found {0} files to process.'.format(len(result)))
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


#=========================
# get handles from a file
#=========================
def load_handles(handle_file):
    result = {}
    with open(handle_file, "r") as f:
        for line in csv.DictReader(f):
            id = line['identifier']
            handle = line['handlehttp']
            if id not in result:
                result[id] = handle
    return result


#============================
# fix incorrect box numbers
#===========================
def fix_box_number_discrepancies(root):
    boxes = [c for c in root.iter('container') if c.get('type') == 'box']
    for box in boxes:
        match = re.search(r'^(box)?(\d+).\d+$', box.get('id'))
        if box.text != match.group(2):
            box.text = match.group(2)
            logging.info('Corrected box {0} to {1}'.format(
                ET.tostring(box), match.group(2)))
    return root


#=================================
# add box containers where absent
#=================================
def add_missing_box_containers(root):
    # iterate over item- and file-level containers
    for n, did in enumerate(root.iter('did')):
        print(n, ET.tostring(did))
        parent = did.getparent()
        parent_level = parent.get('level')

        if parent_level in ['file', 'item']:
            # check whether a box container exists already; if so, break out
            for c in did.iterchildren(tag='container'):
                if c.get('type') == 'box':
                    break
            # if not, create a box container
            else:
                box_attribute = c.get('parent')
                print(box_attribute)
                match = re.search(r'^(box)?(\d+).(\d+)$', box_attribute)

                # create attributes corresponding to the parent box
                if match:
                    box_number = match.group(2)
                    box_id = "{0}.{1}".format(match.group(2), match.group(3))
                    new_container = ET.SubElement(did, "container")
                    new_container.set('type', 'box')
                    new_container.set('id', box_id)
                    new_container.text = box_number
                    
    return root


#======================================
# missing extents in physdesc elements
#======================================
def add_missing_extents(root):
    for physdesc in root.findall('physdesc'):
        children = physdesc.getchildren()
        if "extent" not in children:
            ext = ET.SubElement(physdesc, "extent")
            ext.text = physdesc.text
            physdesc.text = ''
            logging.info('Added missing extent element to {0}'.format(physdesc))


#=============================
# add title attribute to dao
#=============================
def add_title_to_dao(root):
    for dao in root.findall('dao'):
        parent = dao.getparent()
        unittitle = parent.find('unittitle').text
        if unittitle:
            dao.set('title', unittitle)
        else:
            print('cannot find unittitle for dao element')


#==================================================
# remove elements containing only empty paragraphs
#==================================================
def remove_empty_elements(root):
    node_types = ['bioghist', 'processinfo', 'scopecontent']
    # check for each of the three elements above
    for node_type in node_types:
        # iterate over instances of the element
        for node in root.findall(node_type):
            parent = node.getparent()
            # find all the paragraphs in the node
            paragraphs = node.findall('p')
            # if any contain text, break the loop
            for p in paragraphs:
                if len(p) > 0 or p.text is not None:
                    break
            # otherwise remove the parent element
            else:
                logging.info(ET.tostring(instance))
                parent.remove(instance)


#==============================
# Remove "Guide to" from title
#==============================
def remove_guide_to_from_title(root):
    titleproper = root.find('titleproper')
    # if title.text begins with "Guide to", remove it and capitalize next word
    if titleproper is not None and titleproper.text is not '':
        titleproper_old = titleproper.text

        if titleproper_old is not None and titleproper_old.startswith(
                                                                "Guide to"):

            titleproper_new = titleproper_old[9].upper() + titleproper_old[10:]

            if len(titleproper_new) > 25:
                new_t = titleproper_new[:25] + "..."
                old_t = titleproper_old[:25] + "..."
            else:
                new_t = titleproper_new
                old_t = titleproper_old
                
            print("  Altered title: {0} => {1}".format(old_t, new_t))


#=================================================
# 
#=================================================
    # scope and content notes
    analyticover = root.xpath('//dsc[@type="analyticover"]')

    for ac in analyticover:
        for sc in ac.iter('scopecontent'):
            paragraphs = [node for node in sc if node.tag is 'p']

            for p in paragraphs:
                if p.text is not None:
                    break # move the content over

        ac.getparent().remove(ac)


#=================================================
# 
#=================================================
    # remove multiple abstracts
    abstracts = [a for a in root.iter('abstract')]

    print("  Found {0} abstracts:".format(len(abstracts)))

    if len(abstracts) > 1:
        for abstract_num, abstract in enumerate(abstracts):
            label = abstract.get('label')

            if label == "Short Description of Collection":
                print("    {0}. Keeping Short Description".format(
                                                    abstract_num +1))
            else:
                print("    {0}. Removing abstract '{1}'...".format(
                                                    abstract_num + 1, label))
                abstract.getparent().remove(abstract)
    else:
        print("  There is only one abstract.")
    

#=================================================
# 
#=================================================
    eadid = root.find('.//eadid')

    eadid.set('url', handle)



#=============================
# unitdate report generation
#============================
def report_dates(root):
    result = []
    
    allowed_patterns = [r'^\d{4}$', 
                        r'^\d{4}-\d{4}$', 
                        r'^[a-zA-Z]+? \d\d?,? \d{4}$',
                        r'^[a-zA-Z]+? \d\d?,? \d{4}-[a-zA-Z]+? \d\d?,? \d{4}$']
    
    unitdates = root.xpath(
        "//archdesc[@level='collection' and @type='combined']/did/unitdate")
    
    for u in unitdates:
        # strip out unitdates that have a null value
        if u.text == "null":
            u.getparent().remove(u)
            continue
    
        for p in allowed_patterns:
            if re.match(p, u.text):
                # print("{0} matches pattern {1}".format(u.text, p))
                break
        else:
            result.append(u.text)
    
    return result


#=============================
# extent report generation
#============================
def report_extents(root):
    result = []
    
    allowed_patterns = [r'^[0-9.]+ linear feet$']
    
    extents = root.find(".//physdesc")
    
    for e in extents:
        for p in allowed_patterns:
            if re.match(p, e.text):
                # print("{0} matches pattern {1}".format(e.text, p))
                break
        else:
            result.append(e.text)
    
    return result


#=================================================
# apply the xml transformations to the input file
#=================================================
def clean_ead(xml_as_bytes):
    # in order to parse string as XML, create file-like object and parse it
    file_like_obj = BytesIO(xml_as_bytes)
    tree = ET.parse(file_like_obj)
    root = tree.getroot()
    
    root = add_missing_box_containers(root)
    root = fix_box_number_discrepancies(root)
    root = add_missing_extents(root)


#================
#  main function
#================
def main(args):
    border = "=" * 19
    print("\n".join(['', border, "| EAD Transformer |", border]))
    errors = []
    dates = []
    extents = []
    deletions = {}
    handles = load_handles('ead_handles_rev.csv')
    
    # set up message logging to record actions on files
    logging.basicConfig(
        filename='data/reports/transform.log', 
        filemode='w', 
        level=logging.INFO)
    
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
        print(files_to_check)
    # set path for output
    output_dir = args.output
    
    # notify that resume flag is set
    if args.resume:
        print("Resume flag (-r) is set, will skip existing files")
    
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
            # other transformations
            print("  Applying XML transformations...")

            try:
                try: 
                    handle = handles[os.path.basename(f)]
                except KeyError:
                    handle = ''

                ead_tree = clean_ead(ead_string.encode('utf-8'), handle)
                bad_dates = report_dates(ead_tree)

                for date in bad_dates:
                    dates.append('{0},"{1}"'.format(f, date))
                
                bad_extents = report_extents(ead_tree)

                for extent in bad_extents:
                    extents.append('{0},"{1}"'.format(f, extent))
                    
            except ET.ParseError as e:
                print("  {0} is malformed; error code {1} ({2}) at {3})".format(
                    f, e.code, xerr.ErrorString(e.code), e.position))

                errors.append(
                    "{0} is malformed; error code {1} ({2}) at {3})".format(
                        f, e.code, xerr.ErrorString(e.code), e.position))
            
            # write out result
            ead_tree.write(output_path)
    
    # write out error log if any errors occurred
    if errors:
        with open('data/reports/errors.txt', 'w') as errfile:
            errfile.writelines("\n".join(errors))
    
    if dates:
        with open('data/reports/unitdates_report.csv', 'w') as datesfile:   
            datesfile.writelines("\n".join(dates))
    
    if extents:
        with open('data/reports/extents_report.csv', 'w') as extentsfile:   
            extentsfile.writelines("\n".join(extents))


#==============================
# parse command line arguments
#==============================
if __name__ == '__main__':
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
    parser.add_argument('files', nargs='*', help='files to check')

    args = parser.parse_args()

    main(args)

#     handles = load_handles('ead_handles.csv')
#     dupes = {k:v for k,v in handles.items() if len(v) > 1}
#     for n,h in enumerate(handles):
#         print("{0}. {1} => {2}".format(n+1, h, handles[h]))
#     for d in dupes:
#         print(d, dupes[d])
