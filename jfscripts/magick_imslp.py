#! /usr/bin/env python3

import argparse
import os
import re
import subprocess
import tempfile
import uuid


job_identifier = str(uuid.uuid1())
tmp_dir = tempfile.mkdtemp()
cwd = os.getcwd()


class FilePath(object):

    def __init__(self, path, absolute=False):
        if absolute:
            self._path = os.path.abspath(path)
        else:
            self._path = os.path.relpath(path)
        self._extension = os.path.splitext(self._path)[1][1:]

    def extension(self, extension):
        return re.sub(
            '\.{}$'.format(self._extension),
            '.{}'.format(extension),
            self._path
        )

    def backup(self):
        return re.sub(
            '\.{}$'.format(self._extension),
            '_backup.{}'.format(self._extension),
            self._path
        )

    def get(self):
        return self._path


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
        '-B',
        '--border',
        action='store_true',
        help='Add a white border',
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
        default='50%',
        help='threshold, default 50 percent.',
    )

    parser.add_argument(
        'input_files',
        help='files to process.',
        nargs='+',
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


def do_magick(input_file, args):
    cmd_args = ['convert']
    # cmd_args += ['-fuzz', '98%']

    if args.border:
        cmd_args += ['-border', '100x100', '-bordercolor', '#FFFFFF']

    if args.resize:
        cmd_args += ['-resize', '200%']

    cmd_args += ['-deskew', '40%']
    cmd_args += ['-threshold', args.threshold]
    cmd_args += ['-trim', '+repage']

    if args.compression:
        cmd_args += ['-compress', 'Group4', '-monochrome']

    cmd_args.append(input_file)
    cmd_args.append(input_file + '.pdf')
    subprocess.run(cmd_args)


def per_file(input_file):
    extension = os.path.splitext(input_file)[1][1:]
    if extension.lower() == 'pdf':
        pdf_to_images(input_file)


def main():
    args = get_args()

    for input_file in args.input_files:
        per_file(input_file)


if __name__ == '__main__':
    main()
