#! /usr/bin/env python3

from jfscripts import __version__
from jfscripts import list_files
from jfscripts._utils import check_bin, Run, FilePath
import argparse
import multiprocessing
import os
import random
import re
import shutil
import time
import uuid

run = Run()

dependencies = (
    ('convert', 'imagemagick'),
    ('identify', 'imagemagick'),
    ('pdfimages', 'poppler'),
    ('pdfinfo', 'poppler'),
    'pdftk',
)


def check_threshold(value):
    """
    Check if `value` is a valid threshold value.

    :param value:
    :type value: integer or string

    :return: A normalized threshold string (`90%`)
    :rtype: string
    """
    value = re.sub(r'%$', '', str(value))
    value = int(value)
    if value < 0 or value > 100:
        message = '{} is an invalid int value. Should be 0-100'.format(value)
        raise argparse.ArgumentTypeError(message)
    return '{}%'.format(value)


def get_parser():
    """The argument parser for the command line interface.

    :return: A ArgumentParser object.
    :rtype: argparse.ArgumentParser
    """
    parser = argparse.ArgumentParser(
        description='A wrapper script for imagemagick to process image \
        files suitable for imslp.org (International Music Score Library \
        Project). See also http://imslp.org/wiki/IMSLP:Musiknoten_beisteuern. \
        The target files are monochrome bitmap images at a resolution of \
        600 dpi and the compression format CCITT group 4.',
    )

    parser.add_argument(
        '-c',
        '--colorize',
        action='store_true',
        help='Colorize the terminal output.',
    )

    parser.add_argument(
        '-v',
        '--verbose',
        action='store_true',
        help='Make the command line output more verbose.',
    )

    parser.add_argument(
        '-V',
        '--version',
        action='version',
        version='%(prog)s {version}'.format(version=__version__),
    )

    subcommand = parser.add_subparsers(
        dest='subcommand',
        help='Subcommand',
    )
    subcommand.required = True

    bitmap_parser = subcommand.add_parser('bitmap')

    bitmap_parser.add_argument(
        '-b',
        '--backup',
        action='store_true',
        help='Backup original images (add _backup.ext to filename).',
    )

    bitmap_parser.add_argument(
        '-B',
        '--border',
        action='store_true',
        help='Frame the images with a white border.',
    )

    bitmap_parser.add_argument(
        '-e',
        '--enlighten-border',
        action='store_true',
        help='Enlighten the border.',
    )

    bitmap_parser.add_argument(
        '-f',
        '--force',
        action='store_true',
        help='Overwrite the target file even if it exists and it seems to be '
        'already converted.',
    )

    bitmap_parser.add_argument(
        '-j',
        '--join',
        action='store_true',
        help='Join single paged PDF files to one PDF file. This option takes '
        'only effect with the option --pdf.',
    )

    bitmap_parser.add_argument(
        '-N',
        '--no-cleanup',
        action='store_true',
        help='Don’t clean up the temporary files.',
    )

    bitmap_parser.add_argument(
        '-n',
        '--no-multiprocessing',
        action='store_true',
        help='Disable multiprocessing.',
    )

    bitmap_parser.add_argument(
        '-p',
        '--pdf',
        action='store_true',
        help='Generate a PDF file using CCITT Group 4 compression.',
    )

    bitmap_parser.add_argument(
        '-r',
        '--resize',
        action='store_true',
        help='Resize 200 percent.',
    )

    bitmap_parser.add_argument(
        '-S',
        '--threshold-series',
        action='store_true',
        help='Convert the samge image with different threshold values to \
        find the best threshold value.',
    )

    bitmap_parser.add_argument(
        '-t',
        '--threshold',
        default='50%',
        type=check_threshold,
        help='threshold, default 50 percent.',
    )

    bitmap_parser.add_argument(
        'input_files',
        help=list_files.doc_examples('%(prog)s', 'tiff'),
        nargs='+',
    )

    extract_parser = subcommand.add_parser('extract')

    extract_parser.add_argument(
        'input_files',
        help=list_files.doc_examples('%(prog)s', 'tiff'),
        nargs='+',
    )

    join_parser = subcommand.add_parser(
        'join',
        description='Join the input files into a single PDF file. If the '
        'input file is not PDF file, it is converted into a monochrome CCITT '
        'Group 4 compressed PDF file.',
    )

    join_parser.add_argument(
        'input_files',
        help=list_files.doc_examples('%(prog)s', 'png'),
        nargs='+',
    )

    return parser


def pdf_page_count(pdf_file):
    """Get the amount of pages a PDF files have.

    :param str pdf_file: Path of the PDF file.

    :return: Page count
    :rtype: int
    """
    output = run.check_output(['pdfinfo', str(pdf_file)]).decode('utf-8')
    page_count = re.search(r'Pages:\s*([0-9]*)', output)
    return int(page_count.group(1))


def pdf_to_images(pdf_file, state, page_number=None):
    """Convert a PDF file to images in the TIFF format.

    :param pdf_file: The input file.
    :type pdf_file: jfscripts._utils.FilePath
    :param state: The state object.
    :type state: jfscripts.magick_imslp.State
    :param int page_number: Extract only the page with a specific page number.

    :return: The return value of `subprocess.run`.
    :rtype: subprocess.CompletedProcess
    """
    image_root = '{}_{}'.format(pdf_file.basename, state.tmp_identifier)

    command = ['pdfimages', '-tiff', str(pdf_file), image_root]

    if page_number:
        page_number = str(page_number)
        page_segments = ['-f', page_number, '-l', page_number]
        command = command[:2] + page_segments + command[2:]
    return run.run(command, cwd=state.common_path)


def collect_images(state):
    """Collection all images using the temporary identifier in a common path.

    :param state: The state object.
    :type state: jfscripts.magick_imslp.State

    :return: A sorted list of image paths.
    :rtype: list
    """
    prefix = state.common_path
    out = []
    for input_file in os.listdir(prefix):
        if state.tmp_identifier in input_file and \
           os.path.getsize(os.path.join(prefix, input_file)) > 200:
            out.append(os.path.join(prefix, input_file))
    out.sort()
    return out


def cleanup(state):
    """Delete all images  using the temporary identifier in a common path.

    :param state: The state object.
    :type state: jfscripts.magick_imslp.State

    :return: None"""

    for work_file in os.listdir(state.common_path):
        if state.tmp_identifier in work_file:
            os.remove(os.path.join(state.common_path, work_file))


def enlighten_border(width, height):
    """
    Build the command line arguments to enlighten the border in four regions.

    :param int width: The width of the image.
    :param int height: The height of the image.

    :return: Command line arguments for imagemagicks’ `convert`.
    :rtype: list


    """
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


def convert_executable():
    """ImageMagick version 7 introduces a new top level command named
    `magick`. Use this newer command if present.

    :return: A list of command segments
    """
    if shutil.which('magick'):
        return ['magick', 'convert']
    else:
        return ['convert']


def do_magick(arguments):
    """
    Convert a source image file using the subcommand convert of the
    imagemagick suite.

    :param tuple arguments: A tuple containing two elements: The first element
      is the source file object and the second element is the state object.

    :return: The target image file.
    :rtype: jfscripts._utils.FilePath
    """
    source = arguments[0]
    state = arguments[1]

    cmd_args = convert_executable()

    if state.args.enlighten_border:
        info_source = get_image_info(source)
        cmd_args += enlighten_border(info_source['width'],
                                     info_source['height'])

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

    if not state.args.join:
        target = source.new(extension=extension,
                            del_substring='_' + state.tmp_identifier)
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

    run.run(cmd_args)
    return target


def convert_to_pdf(source):
    """

    :return: The target image file.
    :rtype: jfscripts._utils.FilePath
    """

    cmd_args = convert_executable()

    cmd_args += ['-compress', 'Group4', '-monochrome']

    cmd_args.append(str(source))

    target = source.new(extension='pdf')

    cmd_args.append(str(target))

    run.run(cmd_args)
    return target


def threshold(input_file, threshold, state):
    """Convert a image to a given threshold value.

    :param input_file: The input file.
    :type input_file: jfscripts._utils.FilePath
    :param int threshold: A integer number between 0 - 100.
    :param state: The state object.
    :type state: jfscripts.magick_imslp.State

    :return: None
    """
    appendix = '_threshold-{}'.format(threshold)
    output_file = input_file.new(extension='png', append=appendix,
                                 del_substring=state.tmp_identifier)
    output_file = str(output_file).replace('_-000', '')
    run.run(convert_executable() + ['-threshold', '{}%'.format(threshold),
            str(input_file), output_file])


def threshold_series(input_file, state):
    """Generate a list of example files with different threshold values.

    :param input_file: The input file.
    :type input_file: jfscripts._utils.FilePath
    :param state: The state object.
    :type state: jfscripts.magick_imslp.State

    :return: None
    """
    if state.input_is_pdf:
        page_count = pdf_page_count(input_file)
        page_number = random.randint(1, page_count)
        print('Used page number {} of {} pages to generate a series of images '
              'with different threshold values.'
              .format(page_number, page_count))
        pdf_to_images(input_file, state, page_number)
        images = collect_images(state)
        input_file = FilePath(images[0], absolute=True)

    for number in range(40, 100, 5):
        threshold(input_file, number, state)


def get_image_info(input_file):
    """The different informations of an image.

    :param input_file: The input file.
    :type input_file: jfscripts._utils.FilePath

    :return: A directory with the keys `width`, `height` and `channels`.
    :rtype: dict
    """
    def _get_by_format(input_file, format):
        return run.check_output(['identify', '-format', format,
                                 str(input_file)]).decode('utf-8')

    return {
        'width': int(_get_by_format(input_file, '%w')),
        'height': int(_get_by_format(input_file, '%h')),
        'channels': int(_get_by_format(input_file, '%k')),
    }


def do_multiprocessing_magick(input_files, state):
    """Run the function `do_magick` in a multiprocessing environment.

    :param state: The state object.
    :type state: jfscripts.magick_imslp.State
    """
    pool = multiprocessing.Pool()
    data = []
    for input_file in input_files:
        data.append((input_file, state))
    return pool.map(do_magick, data)


def join_to_pdf(pdf_files, state):
    """Join a list of PDF files into a single PDF file using the tool `pdftk`.

    :param list pdf_files: a list of PDF files
    :param state: The state object.
    :type state: jfscripts.magick_imslp.State

    :return: None
    """
    cmd = ['pdftk']

    pdf_file_paths = map(lambda pdf_file: str(pdf_file), pdf_files)
    cmd += pdf_file_paths

    target_path = os.path.join(
        state.common_path,
        '{}_magick.pdf'.format(state.first_input_file.basename)
    )
    cmd += ['cat', 'output', target_path]

    result = run.run(cmd)
    if result.returncode == 0:
        print('Successfully created: {}'.format(target_path))


class Timer(object):
    """Class to calculate the execution time. Mainly to test the speed
    improvements of the multiprocessing implementation."""

    def __init__(self):
        self.end = None
        """UNIX timestamp the execution ended."""
        self.begin = self.end = time.time()
        """UNIX timestamp the execution began."""

    def stop(self):
        """Stop the time calculation and return the formated result.

        :return: The result
        :rtype: str
        """
        self.end = time.time()
        return '{:.1f}s'.format(self.end - self.begin)


class State(object):
    """This object holds runtime data for the multiprocessing environment."""

    def __init__(self, args):
        self.args = args
        """argparse arguments"""

        self.cwd = os.getcwd()
        """The current working directory"""

        self.input_files = list_files.list_files(self.args.input_files)
        """A list of all input files."""

        self.common_path = \
            list_files.common_path(self.input_files)
        """The common path prefix of all input files."""

        if self.common_path == '':
            self.common_path = self.cwd
        self.first_input_file = FilePath(self.input_files[0], absolute=True)
        """The first input file."""

        self.input_is_pdf = False
        """Boolean that indicates if the first file is a pdf."""

        if self.first_input_file.extension.lower() == 'pdf':
            self.input_is_pdf = True

        self.identifier = 'magick'
        """To allow better assignment of the output files."""

        self.uuid = str(uuid.uuid1())
        """A random string used for the identification of temporarily
        generated files."""

        self.tmp_identifier = '{}_{}'.format(self.identifier, self.uuid)
        """Used for the identification of temporary files."""


def convert_file_paths(files):
    """Convert a list of file paths in a list of
    :class:`jfscripts._utils.FilePath` objects.

    :param list files: A list of file paths

    :return: a list of  :class:`jfscripts._utils.FilePath` objects.
    """
    out = []
    for f in files:
        out.append(FilePath(f, absolute=True))
    return out


def main():
    """Main function.

    :return: None
    """
    timer = Timer()
    args = get_parser().parse_args()

    run.setup(verbose=args.verbose, colorize=args.colorize)
    state = State(args)

    check_bin(*dependencies)

    if args.subcommand == 'bitmap':

        if state.args.join and not state.args.pdf:
            state.args.pdf = True

        if state.args.threshold_series:
            threshold_series(state.first_input_file, state)
            if not state.args.no_cleanup:
                cleanup(state)
            return

        if state.first_input_file.extension == 'pdf':
            if len(state.input_files) > 1:
                raise ValueError('Specify only one PDF file.')
            pdf_to_images(state.first_input_file, state)
            input_files = collect_images(state)
        else:
            input_files = state.input_files

        input_files = convert_file_paths(input_files)

        if state.args.no_multiprocessing:
            output_files = []
            for input_file in input_files:
                pack = (input_file, state)
                output_files.append(do_magick(pack))
        else:
            output_files = do_multiprocessing_magick(input_files, state)

        if state.args.join:
            join_to_pdf(output_files, state)

        if not state.args.no_cleanup:
            cleanup(state)

    elif args.subcommand == 'join':
        input_files = convert_file_paths(state.input_files)
        pdf_files = []
        for input_file in input_files:
            if input_file.extension != 'pdf':
                pdf_files.append(convert_to_pdf(input_file))
            else:
                pdf_files.append(input_file)
        join_to_pdf(pdf_files, state)

    print('Execution time: {}'.format(timer.stop()))


if __name__ == '__main__':
    main()
