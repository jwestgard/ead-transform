#!/usr/bin/env python3
import argparse
import codecs

parser = argparse.ArgumentParser(description='Test different decodings.')
parser.add_argument('files', nargs='+', help='files to check')
args = parser.parse_args()

print('\n\nFile Encoding Checker')
print('=' * 21)

for n, f in enumerate(args.files):
    print("{0}. Checking encoding of {1} ...".format(n+1, f))
    encodings = ['utf-8', 'ascii', 'windows-1252', 'latin-1']
    
    for encoding in encodings:
        bytes = codecs.open(f, mode='r', encoding=encoding, errors='strict')
        try:
            bytes.read()
            print('  - {0} OK.'.format(encoding))
        except UnicodeDecodeError:
            print('  - {0} Error!'.format(encoding))

print('')
