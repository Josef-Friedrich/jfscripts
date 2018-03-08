#! /usr/bin/env python3

import sys
import os

from fuzzywuzzy import process


def main(path):

    names = []
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            names.append(filename.decode('utf8'))

    names = tuple(names)

    for name in names:
        print('')
        print(name)
        result = process.extract(name, names)
        for match in result:
            if match[1] > 90 and match[1] != 100:
                print(match[0])


if sys.argv[1:]:
    main(sys.argv[1])
