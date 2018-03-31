#! /usr/bin/env python3

import multiprocessing
import argparse
import os
import re
import subprocess
from jfscripts._utils import check_bin

dependencies = (
    ('convert', 'imagemagick'),
    ('identify', 'imagemagick'),
    ('pdfimages', 'poppler'),
    ('pdfinfo', 'poppler'),
    'pdftk',
)


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


def pdf_page_count(pdf_file):
    output = subprocess.check_output(['pdfinfo', pdf_file])
    output = output.decode('utf-8')
    page_count = re.search(r'Pages:\s*([0-9]*)', output)
    return int(page_count.group(1))


def pdf_to_images(pdf_file, state):
    state.pdf_env(pdf_file)
    subprocess.run([
        'pdfimages',
        '-tiff',
        str(pdf_file),
        state.job_identifier,
    ], cwd=state.pdf_dir)


def collect_images(state):
    out = []
    for input_file in os.listdir(state.pdf_dir):
        if input_file.startswith(state.job_identifier) and \
           os.path.getsize(os.path.join(state.pdf_dir, input_file)) > 200:
            out.append(os.path.join(state.pdf_dir, input_file))
    out.sort()
    return out


def do_magick(arguments):
    input_file = arguments[0]
    state = arguments[1]
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


def do_multiprocessing_magick(input_files, state):
    pool = multiprocessing.Pool()
    data = []
    for input_file in input_files:
        data.append((FilePath(input_file, absolute=True), state))
    pool.map(do_magick, data)


def join_to_pdf():
    pass
    # pdftk *.pdf cat output out.pdf


class State(object):

    def __init__(self, args):
        self.args = args

    def pdf_env(self, pdf_file):
        pdf_file = str(pdf_file)
        self.pdf_dir = os.path.dirname(pdf_file)
        self.job_identifier = os.path.basename(pdf_file)
        self.cwd = os.getcwd()


def main():
    args = get_args()
    state = State(args)

    check_bin(*dependencies)

    first_input_file = FilePath(state.args.input_files[0], absolute=True)
    if first_input_file.extension == 'pdf':
        if len(state.args.input_files) > 1:
            raise ValueError('Specify only one PDF file.')
        pdf_to_images(first_input_file, state)
        collected_input_files = collect_images(state)
        do_multiprocessing_magick(collected_input_files, state)
    else:
        do_multiprocessing_magick(state.args.input_files, state)


if __name__ == '__main__':
    main()
