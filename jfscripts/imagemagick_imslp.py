#! /usr/bin/env python3

import argparse


def get_args():
    parser = argparse.ArgumentParser(
        description='A wrapper script for imagemagick to process image \
        files suitable for imslp.org (International Music Score Library \
        Project). See also http://imslp.org/wiki/IMSLP:Musiknoten_beisteuern',
    )

    parser.add_argument(
        '-b',
        '--backup',
        help='Backup original images (add .bak to filename).',
    )

    parser.add_argument(
        '-c',
        '--compression',
        help='Use CCITT Group 4 compression. This options generates a PDF \
        file.',
    )

    parser.add_argument(
        '-e',
        '--enlighten-border',
        help='Enlighten the border.',
    )

    parser.add_argument(
        '-f',
        '--force',
        help='force',
    )

    parser.add_argument(
        '-i',
        '--imslp',
        help='Use the best options to publish on IMSLP. (--compress, \
        --join, --resize)',
    )

    parser.add_argument(
        '-j',
        '--join',
        help='Join single paged PDF files to one PDF file.',
    )

    parser.add_argument(
        '-r',
        '--resize',
        help='Resize 200 percent.',
    )

    parser.add_argument(
        '-S',
        '--threshold-series',
        help='Convert the samge image with different threshold values to \
        find the best threshold value.',
    )

    parser.add_argument(
        '-t',
        '--threshold',
        help='threshold, default 50 percent.',
    )

    parser.add_argument(
        'files',
        help='files to process.',
    )

    return parser.parse_args()


def main():
    args = get_args()
    print(args)


if __name__ == '__main__':
    main()
