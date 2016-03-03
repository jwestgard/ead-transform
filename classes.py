#!/usr/bin/env python3

import lxml.etree as ET

class ead(object):
    'base class for Encoded Archival Description object'
    
    def __init__(self, xmlfile, handle, id):
        self.name = id
        self.tree = ET.parse(xmlfile)
        self.handle = handle
