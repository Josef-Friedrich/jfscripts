#! /usr/bin/env python3

import sys

n = [int(x, 16) for x in sys.argv[1].split(":")]
print('fe80::%02x%02x:%02xff:fe%02x:%02x%02x' % tuple([n[0] ^ 2]+n[1:]))
