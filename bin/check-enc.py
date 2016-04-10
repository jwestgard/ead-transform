#!/usr/bin/env python3
import argparse
import codecs
import difflib
from csv import DictWriter
from os.path import basename

parser = argparse.ArgumentParser(description='Test different decodings.')
parser.add_argument('files', nargs='+', help='files to check')
parser.add_argument('-o', '--output', help='output file')
args = parser.parse_args()

print('\n\nFile Encoding Checker')
print('=' * 21)

results = []

for n, f in enumerate(args.files):
    print("{0}. Checking encoding of {1} ...".format(n+1, f))
    encodings = ['utf-8', 'ascii', 'windows-1252', 'latin-1']
    item_report = {'number': n+1, 'filename': basename(f)}
    for encoding in encodings:
        bytes = codecs.open(f, mode='r', encoding=encoding, errors='strict')
        try:
            bytes.read()
            print('  - {0} OK.'.format(encoding))
            item_report.update({encoding: 'OK'})
        except UnicodeDecodeError:
            print('  - {0} Error!'.format(encoding))
            item_report.update({encoding: 'error'})
    results.append(item_report)
    
    possible_encodings = [e for e in item_report if item_report[e] == 'OK']
    versions = []
    if len(possible_encodings) < len(encodings):
        for e in possible_encodings:
            bytestream = codecs.open(f, mode='r', encoding=e, errors='ignore')
            versions.append((e, bytestream.readlines()))
        n = len(versions[0][1])
        for ln, i in enumerate(range(n)):
            if versions[0][1][i] != versions[1][1][i]:
                a = versions[0][1][i].split(' ')
                b = versions[1][1][i].split(' ')
                for wn, word in enumerate(range(len(a))):
                    if a[word] != b[word]:
                        print("  - L{0}.W{1} > {2}:{3}\t{4}:{5}".format(ln, wn,
                            versions[0][0], a[word], versions[1][0], b[word]))

print('')

if args.output:
    with open(args.output, 'w') as csvfile:
        fieldnames = ['number', 'filename']
        fieldnames.extend(encodings)
        writer = DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerows(results)
