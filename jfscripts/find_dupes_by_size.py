#! /usr/bin/env python3

import argparse
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


def get_parser():
    parser = argparse.ArgumentParser(
        description='Find duplicate files by size.',
    )

    parser.add_argument(
        'path',
        help='A directory to recursively search for duplicate files.',
    )

    return parser


def main():
    args = get_parser().parse_args()

    check_for_duplicates(args.path)


if __name__ == '__main__':
    main()
