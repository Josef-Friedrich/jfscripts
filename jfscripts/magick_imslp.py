#! /usr/bin/env python3

import multiprocessing
import argparse
import os
import re
import subprocess
import tempfile
import uuid
from jfscripts._utils import check_bin


class FilePath(object):

    def __init__(self, path, absolute=False):
        self.absolute = absolute
        if self.absolute:
            self.path = os.path.abspath(path)
        else:
            self.path = os.path.relpath(path)
        self.extension = os.path.splitext(self.path)[1][1:]

    def __str__(self):
        return self.path

    def change_extension(self, extension):
        return FilePath(re.sub(
            '\.{}$'.format(self.extension),
            '.{}'.format(extension),
            self.path
        ), self.absolute)

    def get_backup_path(self):
        return FilePath(re.sub(
            '\.{}$'.format(self.extension),
            '_backup.{}'.format(self.extension),
            self.path
        ), self.absolute)


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


def pdf_to_images(pdf_file, state):
    state.setup_tmp_dir()
    subprocess.run([
        'pdfimages',
        '-tiff',
        str(pdf_file),
        state.job_identifier,
    ], cwd=state.tmp_dir)


def collect_images(state):
    out = []
    for input_file in os.listdir(state.tmp_dir):
        if input_file.startswith(state.job_identifier) and \
           os.path.getsize(input_file) > 0:
            out.append(os.path.join(state.tmp_dir, input_file))

    out.sort()
    return out


def do_magick(input_file, state):
    cmd_args = ['convert']
    # cmd_args += ['-fuzz', '98%']

    if state.args.border:
        cmd_args += ['-border', '100x100', '-bordercolor', '#FFFFFF']

    if state.args.resize:
        cmd_args += ['-resize', '200%']

    cmd_args += ['-deskew', '40%']
    cmd_args += ['-threshold', state.args.threshold]
    cmd_args += ['-trim', '+repage']

    if state.args.compression:
        cmd_args += ['-compress', 'Group4', '-monochrome']

    cmd_args.append(str(input_file))

    if state.args.compression:
        extension = 'pdf'
    else:
        extension = 'png'

    target = input_file.change_extension(extension)
    cmd_args.append(str(target))

    subprocess.run(cmd_args)
    return target


def join_to_pdf():
    pass
    # pdftk *.pdf cat output out.pdf


def per_file(arguments):
    input_file = arguments[0]
    state = arguments[1]
    input_file = FilePath(input_file, absolute=True)
    print(str(input_file))
    if input_file.extension == 'pdf':
        pdf_to_images(input_file, state)
    else:
        do_magick(input_file, state)


class State(object):

    def __init__(self, args):
        self.args = args

    def setup_tmp_dir(self):
        self.job_identifier = str(uuid.uuid1())
        self.tmp_dir = tempfile.mkdtemp()
        self.cwd = os.getcwd()


def main():
    args = get_args()
    state = State(args)

    check_bin(
        ('convert', 'imagemagick'),
        ('identify', 'imagemagick'),
        ('pdfimages', 'poppler'),
        'pdftk',
    )

    mp_data = []
    for input_file in state.args.input_files:
        mp_data.append((input_file, state))

    # for input_file in args.input_files:
    #     per_file(input_file, args)

    p = multiprocessing.Pool()
    p.map(per_file, mp_data)


if __name__ == '__main__':
    main()
