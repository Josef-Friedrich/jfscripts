#! /usr/bin/env python3

import argparse
import subprocess
import uuid
import tempfile
import os

job_identifier = str(uuid.uuid1())
tmp_dir = tempfile.mkdtemp()
cwd = os.getcwd()


def get_args():
    parser = argparse.ArgumentParser(
        description='A wrapper script for imagemagick to process image \
        files suitable for imslp.org (International Music Score Library \
        Project). See also http://imslp.org/wiki/IMSLP:Musiknoten_beisteuern',
    )

    parser.add_argument(
        '-b',
        '--backup',
        action='store_true',
        help='Backup original images (add .bak to filename).',
    )

    parser.add_argument(
        '-c',
        '--compression',
        action='store_true',
        help='Use CCITT Group 4 compression. This options generates a PDF \
        file.',
    )

    parser.add_argument(
        '-e',
        '--enlighten-border',
        action='store_true',
        help='Enlighten the border.',
    )

    parser.add_argument(
        '-f',
        '--force',
        action='store_true',
        help='force',
    )

    parser.add_argument(
        '-i',
        '--imslp',
        action='store_true',
        help='Use the best options to publish on IMSLP. (--compress, \
        --join, --resize)',
    )

    parser.add_argument(
        '-j',
        '--join',
        action='store_true',
        help='Join single paged PDF files to one PDF file.',
    )

    parser.add_argument(
        '-r',
        '--resize',
        action='store_true',
        help='Resize 200 percent.',
    )

    parser.add_argument(
        '-S',
        '--threshold-series',
        action='store_true',
        help='Convert the samge image with different threshold values to \
        find the best threshold value.',
    )

    parser.add_argument(
        '-t',
        '--threshold',
        help='threshold, default 50 percent.',
    )

    parser.add_argument(
        'input_files',
        help='files to process.',
    )

    return parser.parse_args()


def pdf_to_images(pdf_file):
    print(tmp_dir)
    subprocess.run([
        'pdfimages',
        '-tiff',
        os.path.join(cwd, pdf_file),
        job_identifier,
    ], cwd=tmp_dir)


def main():
    args = get_args()
    extension = os.path.splitext(args.input_files)[1][1:]
    if extension.lower() == 'pdf':
        pdf_to_images(args.input_files)


if __name__ == '__main__':
    main()
