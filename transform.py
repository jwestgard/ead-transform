#!/usr/bin/env python3

import sys
import os
import re
import lxml

# PSEUDOCODE:
#============
# get list of regexes from a file
#
# for each EAD
#   get ead file
#   apply regexes one by one to file
#   store output file
#   report changes to log/screeen
#   move to next ead file
