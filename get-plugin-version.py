#!/usr/bin/python

import re
import sys

for line in open('__init__.py').readlines():
    line = line.rstrip()
    line = line.replace(' ','')

    m = re.search('version=\((.*)\)$',line)

    if m:
        print m.group(1).replace(',','.')
        sys.exit(0)

sys.exit(1)
