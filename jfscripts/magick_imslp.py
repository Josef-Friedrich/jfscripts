#! /usr/bin/env python3

import multiprocessing
import argparse
import os
import re
import subprocess
from jfscripts._utils import check_bin
import uuid
import shutil


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
        # file.ext
        self.filename = os.path.basename(path)
        # ext
        self.extension = os.path.splitext(self.path)[1][1:]
        # file
        self.basename = self.filename[:-len(self.extension) - 1]
        # /home/file
        self.base = self.path[:-len(self.extension) - 1]

    def __str__(self):
        return self.path

    def __eq__(self, other):
        return self.path == other.path

    def _export(self, path):
        return FilePath(path, self.absolute)

    def new(self, extension=None, append='', del_substring=''):
        if not extension:
            extension = self.extension
        new = '{}{}.{}'.format(self.base, append, extension)
        if del_substring:
            new = new.replace(del_substring, '')
        return self._export(new)

    def remove(self):
        os.remove(self.path)


def check_threshold(value):
    value = re.sub(r'%$', '', str(value))
    value = int(value)
    if value < 0 or value > 100:
        message = '{} is an invalid int value. Should be 0-100'.format(value)
        raise argparse.ArgumentTypeError(message)
    return '{}%'.format(value)


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
        help='Backup original images (add _backup.ext to filename).',
    )

    parser.add_argument(
        '-B',
        '--border',
        action='store_true',
        help='Frame the images with a white border.',
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
        help='Overwrite the target file even if it exists and it seems to be '
        'already converted.',
    )

    parser.add_argument(
        '-j',
        '--join',
        action='store_true',
        help='Join single paged PDF files to one PDF file. This option takes '
        'only effect with the option --pdf.',
    )

    parser.add_argument(
        '-p',
        '--pdf',
        action='store_true',
        help='Generate a PDF file using CCITT Group 4 compression.',
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
        type=check_threshold,
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
        state.tmp_identifier,
    ], cwd=state.pdf_dir)


def collect_images(state):
    out = []
    for input_file in os.listdir(state.pdf_dir):
        if input_file.startswith(state.tmp_identifier) and \
           os.path.getsize(os.path.join(state.pdf_dir, input_file)) > 200:
            out.append(os.path.join(state.pdf_dir, input_file))
    out.sort()
    return out


def cleanup(state):
    for work_file in os.listdir(state.pdf_dir):
        if work_file.startswith(state.tmp_identifier):
            os.remove(os.path.join(state.pdf_dir, work_file))


def enlighten_border(width, height):
    border = int(round(((width + height) / 2) * 0.05))

    # top
    # right
    # bottom
    # left
    r = ('{}x{}'.format(width - border, border),
         '{}x{}+{}'.format(border, height - border, width - border),
         '{}x{}+{}+{}'.format(width - border, border, border, height - border),
         '{}x{}+{}+{}'.format(border, height - border, 0, border))

    out = []
    for region in r:
        out += ['-region', region, '-level', '0%,30%']

    return out


def do_magick(arguments):
    source = arguments[0]
    state = arguments[1]
    cmd_args = ['convert']

    if state.args.resize:
        cmd_args += ['-resize', '200%']

    cmd_args += ['-deskew', '40%']
    cmd_args += ['-threshold', state.args.threshold]
    cmd_args += ['-trim', '+repage']

    if state.args.border:
        cmd_args += ['-border', '5%', '-bordercolor', '#FFFFFF']

    if state.args.pdf:
        cmd_args += ['-compress', 'Group4', '-monochrome']

    cmd_args.append(str(source))

    if state.args.pdf:
        extension = 'pdf'
    else:
        extension = 'png'

    if hasattr(state, 'tmp_identifier') and not state.args.join:
        target = source.new(extension=extension,
                            del_substring='_' + state.uuid)
    else:
        target = source.new(extension=extension)

    cmd_args.append(str(target))

    if source == target:
        info_target = get_image_info(target)
        if info_target['channels'] == 2 and not state.args.force:
            print('The target file seems to be already converted.')
            return target

        if state.args.backup:
            backup = source.new(append='_backup')
            shutil.copy2(str(source), str(backup))

    subprocess.run(cmd_args)
    return target


def threshold(input_file, threshold, state):
    appendix = '_threshold-{}'.format(threshold)
    out = input_file.new(extension='png', append=appendix)
    subprocess.run(['convert',
                    '-threshold',
                    '{}%'.format(threshold),
                    str(input_file),
                    str(out)
                    ])


def threshold_series(input_file, state):
    for number in range(40, 85, 5):
        threshold(input_file, number, state)


def get_image_info(input_file):
    output = subprocess.check_output(['identify', str(input_file)])
    result = re.search(r' (\d+)x(\d+) .* (\d+)c ', output.decode('utf-8'))
    return {
        'width': int(result.group(1)),
        'height': int(result.group(2)),
        'channels': int(result.group(3)),
    }


def do_multiprocessing_magick(input_files, state):
    pool = multiprocessing.Pool()
    data = []
    for input_file in input_files:
        data.append((input_file, state))
    return pool.map(do_magick, data)


def join_to_pdf(images, state):
    cmd = ['pdftk']

    image_paths = map(lambda image: str(image), images)
    cmd += image_paths
    joined = os.path.join(state.pdf_dir, state.pdf_basename + '_joined.pdf')
    cmd += ['cat', 'output', joined]

    subprocess.run(cmd)


class State(object):

    def __init__(self, args):
        self.args = args
        self.identifier_string = '_magick'
        self.uuid = str(uuid.uuid1())
        self.input_is_pdf = False

    def pdf_env(self, pdf):
        self.pdf_dir = os.path.dirname(str(pdf))
        self.pdf_basename = pdf.basename
        self.tmp_identifier = '{}_{}'.format(pdf.basename, self.uuid)
        self.cwd = os.getcwd()


def convert_file_paths(files):
    out = []
    for f in files:
        out.append(FilePath(f, absolute=True))
    return out


def main():
    args = get_args()
    state = State(args)

    check_bin(*dependencies)

    first_input_file = FilePath(state.args.input_files[0], absolute=True)

    if state.args.threshold_series:
        threshold_series(first_input_file, state)

    if first_input_file.extension == 'pdf':
        state.input_is_pdf = True
        if len(state.args.input_files) > 1:
            raise ValueError('Specify only one PDF file.')
        pdf_to_images(first_input_file, state)
        input_files = collect_images(state)
    else:
        input_files = state.args.input_files

    input_files = convert_file_paths(input_files)
    output_files = do_multiprocessing_magick(input_files, state)

    if state.args.join and state.args.pdf:
        join_to_pdf(output_files, state)

    if hasattr(state, 'pdf_dir'):
        cleanup(state)


if __name__ == '__main__':
    main()
