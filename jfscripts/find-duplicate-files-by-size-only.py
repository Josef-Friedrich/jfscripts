#! /usr/bin/env python3

import sys
import os


def check_for_duplicates(path):
    print(path)
    sizes = {}
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            full_path = os.path.join(dirpath, filename)
            size = os.path.getsize(full_path)
            if size in sizes:
                sizes[size].append(full_path)
            else:
                sizes[size] = [full_path]

    count = 0
    duplicate_paths = {}
    for size, full_paths in sizes.items():
        if len(full_paths) > 1:
            count += 1
            full_paths.sort()
            duplicate_paths[full_paths[0]] = full_paths

    for key, full_paths in sorted(duplicate_paths.items()):
        print('-----------------------------------------')
        for full_path in full_paths:
            print('rm -f "' + full_path + '"')

    print('Duplicates found: ' + str(count))


if sys.argv[1:]:
    check_for_duplicates(sys.argv[1])
else:
    print('Please pass the path to check as parameters to the script')
