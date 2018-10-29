#! /usr/bin/env python3

from jfscripts import __version__
from jfscripts import list_files
from jfscripts._utils import check_dependencies, Run, FilePath
import argparse
import multiprocessing
import os
import random
import re
import shutil
import time
import uuid

run = Run()
state = None
"""The global :class:`State` object."""

identifier = 'magick'
"""To allow better assignment of the output files."""

tmp_identifier = '{}_{}'.format(identifier, uuid.uuid1())
"""Used for the identification of temporary files."""

dependencies = (
    ('convert', 'imagemagick'),
    ('identify', 'imagemagick'),
    ('pdfimages', 'poppler'),
    ('pdfinfo', 'poppler'),
    'pdftk',
    'tesseract',
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
        The output files are monochrome bitmap images at a resolution of \
        600 dpi and the compression format CCITT group 4.',
    )

    parser.add_argument(
        '-c',
        '--colorize',
        action='store_true',
        help='Colorize the terminal output.',
    )

    parser.add_argument(
        '-m',
        '--multiprocessing',
        action='store_true',
        default=False,
        help='Use multiprocessing to run commands in parallel.',
    )

    parser.add_argument(
        '-N',
        '--no-cleanup',
        action='store_true',
        help='Don’t clean up the temporary files.',
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

    ##
    # convert
    ##

    convert_parser = subcommand.add_parser(
        'convert',
        aliases=['con', 'c'],
        description='Convert scanned images (can be many image '
        'file formats or a PDF files) in monochrome bitmap images. The '
        'resulting images are compressed using the CCITT group 4 compression.'
    )

    convert_parser_color = convert_parser.add_mutually_exclusive_group()
    convert_parser_compress = convert_parser.add_mutually_exclusive_group()

    convert_parser_color.add_argument(
        '-a',
        '--auto-black-white',
        action='store_true',
        help='The same as --resize --ocr --join --pdf.',
    )

    convert_parser_color.add_argument(
        '-C',
        '--auto-color',
        action='store_true',
        help='The same as --color --resize --ocr --join --pdf.',
    )

    convert_parser.add_argument(
        '-b',
        '--backup',
        action='store_true',
        help='Backup original images (add _backup.ext to filename).',
    )

    convert_parser.add_argument(
        '-B',
        '--border',
        action='store_true',
        help='Frame the images with a white border.',
    )

    convert_parser.add_argument(
        '-c',
        '--color',
        action='store_true',
        help='The input files are colored images.',
    )

    convert_parser.add_argument(
        '-o',
        '--ocr',
        action='store_true',
        default=False,
        help='Perform optical character recognition (OCR) on the input files.'
        'The output format must be PDF.',
    )

    convert_parser.add_argument(
        '-e',
        '--enlighten-border',
        action='store_true',
        help='Enlighten the border.',
    )

    convert_parser.add_argument(
        '-f',
        '--force',
        action='store_true',
        help='Overwrite the output file even if it exists and it seems to be '
        'already converted.',
    )

    convert_parser.add_argument(
        '-j',
        '--join',
        action='store_true',
        help='Join single paged PDF files to one PDF file. This option takes '
        'only effect with the option --pdf.',
    )

    convert_parser.add_argument(
        '-l',
        '--ocr-language',
        nargs='+',
        help='Run tesseract --list-langs to get your installed languages.',
    )

    convert_parser.add_argument(
        '-p',
        '--pdf',
        action='store_true',
        help='Generate a PDF file.',
    )

    convert_parser_compress.add_argument(
        '-q',
        '--quality',
        default=False,
        help='Compress the input images in a specific quality. The command '
        'automatically turns into the color mode.',
    )

    convert_parser.add_argument(
        '-r',
        '--resize',
        action='store_true',
        help='Resize 200 percent.',
    )

    convert_parser_compress.add_argument(
        '-t',
        '--threshold',
        default='50%',
        type=check_threshold,
        help='Threshold for monochrome, black and white images, default 50 \
        percent. Colors above the threshold will be white and below will be \
        black.',
    )

    convert_parser.add_argument(
        'input_files',
        help=list_files.doc_examples('%(prog)s', 'tiff'),
        nargs='+',
    )

    ##
    # extract
    ##

    extract_parser = subcommand.add_parser(
        'extract',
        aliases=['ex', 'e'],
        description='Extract images from a PDF file and export them in the '
        'TIFF format.'
    )

    extract_parser.add_argument(
        'input_files',
        metavar='input_file',
        help='A pdf file',
        nargs='+',
    )

    ##
    # join
    ##

    join_parser = subcommand.add_parser(
        'join',
        aliases=['jn', 'j'],
        description='Join the input files into a single PDF file. If the '
        'input file is not PDF file, it is converted into a monochrome CCITT '
        'Group 4 compressed PDF file.',
    )

    join_parser.add_argument(
        '-o',
        '--ocr',
        action='store_true',
        default=False,
        help='Perform optical character recognition (OCR) on the input files.',
    )

    join_parser.add_argument(
        '-l',
        '--ocr-language',
        nargs='+',
        help='Run tesseract --list-langs to get your installed languages.',
    )

    join_parser.add_argument(
        'input_files',
        help=list_files.doc_examples('%(prog)s', 'png'),
        nargs='+',
    )

    ##
    # samples
    ##

    samples_parser = subcommand.add_parser(
        'samples',
        aliases=['sp', 's'],
        description='Convert the samge image with different threshold values \
        to find the best threshold value.',
    )

    samples_parser.add_argument(
        'input_files',
        metavar='input_file',
        help='A image or a PDF file. The script selects randomly one page of \
        a multipaged PDF to build the series with differnt threshold values.',
    )

    samples_parser.add_argument(
        '-q',
        '--quality',
        action='store_true',
        help='Compress to JPEG2000 images in different quality steps.',
    )

    samples_parser.add_argument(
        '-t',
        '--threshold',
        action='store_true',
        help='Convert images on different threshold values to monochrome \
        black and white images.',
    )

    return parser


###############################################################################
# do_* functions (alphabetically sorted)
###############################################################################

# do_magick_convert
# do_magick_convert_pdf
# do_magick_identify
# do_pdfimages
# do_pdfinfo_page_count
# do_pdftk_cat
# do_tesseract


def _do_magick_command(command):
    """ImageMagick version 7 introduces a new top level command named
    `magick`. Use this newer command if present.

    :return: A list of command segments
    """
    if shutil.which('magick'):
        return ['magick', command]
    else:
        return [command]


def _do_magick_convert_enlighten_border(width, height):
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


def do_magick_convert(input_file, output_file, threshold=None,
                      enlighten_border=False, border=False, resize=False,
                      deskew=False, trim=False, color=False, quality=75):
    """
    Convert a input image file using the subcommand convert of the
    imagemagick suite.

    :return: The output image file.
    :rtype: jfscripts._utils.FilePath
    """

    cmd_args = _do_magick_command('convert')
    cmd_args += ['-units', 'PixelsPerInch']

    if enlighten_border:
        info_input_file = do_magick_identify(input_file)
        cmd_args += _do_magick_convert_enlighten_border(
            info_input_file['width'],
            info_input_file['height'],
        )

    if resize:
        cmd_args += ['-resize', '200%']

    if deskew:
        cmd_args += ['-deskew', '40%']

    if threshold and not color:
        cmd_args += ['-threshold', threshold]

    if trim:
        cmd_args += ['-trim', '+repage']

    if border:
        cmd_args += ['-border', '5%', '-bordercolor', '#FFFFFF']

    if not color:
        cmd_args += ['-compress', 'Group4', '-monochrome']
    else:
        cmd_args += ['-quality', str(quality)]

    if color and output_file.extension == 'pdf':
        cmd_args += ['-compress', 'JPEG2000']

    cmd_args += [str(input_file), str(output_file)]

    return run.run(cmd_args)


def do_magick_identify(input_file):
    """The different informations of an image.

    :param input_file: The input file.
    :type input_file: jfscripts._utils.FilePath

    :return: A directory with the keys `width`, `height` and `colors`.
    :rtype: dict
    """
    def _get_by_format(input_file, format):
        return run.check_output(_do_magick_command('identify') + ['-format',
                                format, str(input_file)]).decode('utf-8')

    return {
        'width': int(_get_by_format(input_file, '%w')),
        'height': int(_get_by_format(input_file, '%h')),
        'colors': int(_get_by_format(input_file, '%k')),
    }


def do_pdfimages(pdf_file, state, page_number=None, use_tmp_identifier=True):
    """Convert a PDF file to images in the TIFF format.

    :param pdf_file: The input file.
    :type pdf_file: jfscripts._utils.FilePath
    :param state: The state object.
    :type state: jfscripts.magick_imslp.State
    :param int page_number: Extract only the page with a specific page number.

    :return: The return value of `subprocess.run`.
    :rtype: subprocess.CompletedProcess
    """
    if use_tmp_identifier:
        image_root = '{}_{}'.format(pdf_file.basename, tmp_identifier)
    else:
        image_root = pdf_file.basename

    command = ['pdfimages', '-tiff', str(pdf_file), image_root]

    if page_number:
        page_number = str(page_number)
        page_segments = ['-f', page_number, '-l', page_number]
        command = command[:2] + page_segments + command[2:]
    return run.run(command, cwd=state.common_path)


def do_pdfinfo_page_count(pdf_file):
    """Get the amount of pages a PDF files have.

    :param str pdf_file: Path of the PDF file.

    :return: Page count
    :rtype: int
    """
    output = run.check_output(['pdfinfo', str(pdf_file)], encoding='utf-8')
    page_count = re.search(r'Pages:\s*([0-9]*)', output)
    return int(page_count.group(1))


def do_pdftk_cat(pdf_files, state):
    """Join a list of PDF files into a single PDF file using the tool `pdftk`.

    :param list pdf_files: a list of PDF files
    :param state: The state object.
    :type state: jfscripts.magick_imslp.State

    :return: None
    """
    cmd = ['pdftk']

    pdf_file_paths = map(lambda pdf_file: str(pdf_file), pdf_files)
    cmd += pdf_file_paths

    output_file_path = os.path.join(
        state.common_path,
        '{}_magick.pdf'.format(state.first_input_file.basename)
    )
    cmd += ['cat', 'output', output_file_path]

    result = run.run(cmd)
    if result.returncode == 0:
        print('Successfully created: {}'.format(output_file_path))


def do_tesseract(input_file, languages=['deu', 'eng']):
    cmd_args = ['tesseract']
    if languages:
        cmd_args += ['-l', '+'.join(languages)]
    cmd_args += [str(input_file), input_file.base, 'pdf']
    return run.run(cmd_args, stderr=run.PIPE, stdout=run.PIPE)


###############################################################################
#
###############################################################################

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
        if tmp_identifier in input_file and \
           os.path.getsize(os.path.join(prefix, input_file)) > 200:
            out.append(os.path.join(prefix, input_file))
    out.sort()
    return out


def cleanup(state):
    """Delete all images using the temporary identifier in a common path.

    :param state: The state object.
    :type state: jfscripts.magick_imslp.State

    :return: None"""

    for work_file in os.listdir(state.common_path):
        if tmp_identifier in work_file:
            os.remove(os.path.join(state.common_path, work_file))


###############################################################################
# subcommand wrapper functions
###############################################################################


def subcommand_convert_file(arguments):
    """Manipulate one input file

    :param tuple arguments: A tuple containing two elements: The first element
      is the input_file file object and the second element is the state object.
    """
    input_file = arguments[0]
    state = arguments[1]

    if state.args.color:
        intermediate_extension = 'jp2'
    else:
        intermediate_extension = 'tiff'

    if state.args.pdf:
        extension = 'pdf'
    else:
        extension = intermediate_extension

    if state.args.ocr:
        extension = intermediate_extension

    if not state.args.join:
        output_file = input_file.new(extension=extension,
                                     del_substring='_' + tmp_identifier)
    else:
        output_file = input_file.new(extension=extension)

    if input_file == output_file:
        info_output_file = do_magick_identify(output_file)
        if info_output_file['colors'] == 2 and not state.args.force:
            print('The output file seems to be already converted.')
            return output_file

        if state.args.backup:
            backup = input_file.new(append='_backup')
            shutil.copy2(str(input_file), str(backup))

    completed_process = do_magick_convert(
        input_file,
        output_file,
        threshold=state.args.threshold,
        enlighten_border=state.args.enlighten_border,
        border=state.args.border,
        resize=state.args.resize,
        deskew=True,
        trim=True,
        color=state.args.color,
        quality=state.args.quality,
    )

    if completed_process.returncode != 0:
        raise('magick convert failed.')

    if state.args.ocr:
        if output_file.extension not in ['tiff', 'jp2']:
            raise('Tesseract needs a tiff or a jp2 file as input.')
        completed_process = do_tesseract(output_file, state.args.ocr_language)
        if completed_process.returncode != 0:
            raise('tesseract failed.')
        os.remove(str(output_file))
        output_file = output_file.new(extension='pdf')

    return output_file


def subcommand_join_convert_pdf(arguments):
    input_file = arguments[0]
    state = arguments[1]
    if state.args.ocr:
        extension = 'tiff'
    else:
        extension = 'pdf'

    output_file = input_file.new(extension=extension)
    process = do_magick_convert(input_file, output_file)
    if process.returncode != 0:
        raise('join: convert to pdf failed.')

    if state.args.ocr:
        process = do_tesseract(output_file)
        if process.returncode != 0:
            raise('join: ocr failed.')
        os.remove(str(output_file))
        output_file = output_file.new(extension='pdf')

    return output_file


def subcommand_samples(input_file, state):
    """Generate a list of example files with different threshold values.

    :param input_file: The input file.
    :type input_file: jfscripts._utils.FilePath
    :param state: The state object.
    :type state: jfscripts.magick_imslp.State

    :return: None
    """
    def fix_output_path(output_file):
        output_file = str(output_file).replace('_-000', '')
        return FilePath(output_file, absolute=True)

    if state.input_is_pdf:
        page_count = do_pdfinfo_page_count(input_file)
        page_number = random.randint(1, page_count)
        print('Used page number {} of {} pages to generate a series of images '
              'with different threshold values.'
              .format(page_number, page_count))
        do_pdfimages(input_file, state, page_number)
        images = collect_images(state)
        input_file = FilePath(images[0], absolute=True)

    if state.args.threshold:
        for threshold in range(40, 100, 5):
            appendix = '_threshold-{}'.format(threshold)
            output_file = input_file.new(extension='tiff', append=appendix,
                                         del_substring=tmp_identifier)
            output_file = str(output_file).replace('_-000', '')
            do_magick_convert(input_file, fix_output_path(output_file),
                              threshold='{}%'.format(threshold))

    if state.args.quality:
        for quality in range(40, 100, 5):
            appendix = '_quality-{}'.format(quality)
            output_file = input_file.new(extension='pdf', append=appendix,
                                         del_substring=tmp_identifier)
            do_magick_convert(input_file, fix_output_path(output_file),
                              color=True, quality=quality)

###############################################################################
#
###############################################################################


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

        self.input_files = []
        """A list of all input files."""
        if isinstance(self.args.input_files, str):
            self.input_files = [self.args.input_files]
        else:
            self.input_files = list_files.list_files(self.args.input_files)

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
    global state
    state = State(args)

    check_dependencies(*dependencies)

    ##
    # convert
    ##

    if args.subcommand in ['convert', 'cv', 'c']:

        if state.args.join and not state.args.pdf:
            state.args.pdf = True

        if state.args.auto_black_white or state.args.auto_color:
            state.args.join = True
            state.args.pdf = True
            state.args.ocr = True

        if state.args.auto_black_white:
            state.args.resize = True

        if state.args.auto_color:
            state.args.color = True

        if state.args.quality and not state.args.color:
            state.args.color = True

        if state.args.color and not state.args.quality:
            state.args.quality = 75

        if state.first_input_file.extension == 'pdf':
            if len(state.input_files) > 1:
                raise ValueError('Specify only one PDF file.')
            do_pdfimages(state.first_input_file, state)
            input_files = collect_images(state)
        else:
            input_files = state.input_files

        input_files = convert_file_paths(input_files)

        if state.args.multiprocessing:
            pool = multiprocessing.Pool()
            data = []
            for input_file in input_files:
                data.append((input_file, state))
            output_files = pool.map(subcommand_convert_file, data)
        else:
            output_files = []
            for input_file in input_files:
                output_files.append(
                    subcommand_convert_file((input_file, state))
                )

        if state.args.join:
            do_pdftk_cat(output_files, state)

        if not state.args.no_cleanup:
            cleanup(state)

    ##
    # extract
    ##

    elif args.subcommand in ['extract', 'ex', 'e']:
        if not state.input_is_pdf:
            raise ValueError('Specify a PDF file.')
        do_pdfimages(state.first_input_file, state, page_number=None,
                     use_tmp_identifier=False)

    ##
    # join
    ##

    elif args.subcommand in ['join', 'jn', 'j']:
        input_files = convert_file_paths(state.input_files)
        if state.args.multiprocessing:
            pool = multiprocessing.Pool()
            data = []
            for input_file in input_files:
                data.append((input_file, state))
            files_converted = pool.map(subcommand_join_convert_pdf, data)
        else:
            files_converted = []
            for input_file in input_files:
                files_converted.append(
                    subcommand_join_convert_pdf((input_file, state))
                )
        do_pdftk_cat(files_converted, state)

    ##
    # samples
    ##

    elif args.subcommand in ['samples', 'sp', 's']:
        if not state.args.threshold and not state.args.quality:
            state.args.threshold = True
            state.args.quality = True

        subcommand_samples(state.first_input_file, state)
        if not state.args.no_cleanup:
            cleanup(state)

    print('Execution time: {}'.format(timer.stop()))


if __name__ == '__main__':
    main()
