#! /usr/bin/env python3

from jfscripts import __version__
from jfscripts._utils import check_bin, Run
import argparse
import os
import re
import tempfile

run = Run()

dependencies = ('pdfinfo', 'pdftk', 'convert')

# magick identify -verbose -format "x: %x y: %y h: %h w: %w\n" pdf/scans.pdf


def get_pdf_info(pdf_file):
    output = run.check_output(['pdfinfo', pdf_file])
    output = output.decode('utf-8')
    # Page size:      522.249 x 644.573 pts
    dimension = re.search(r'Page size:\s*([0-9.]*) x ([0-9.]*)\s*pts', output)
    page_count = re.search(r'Pages:\s*([0-9]*)', output)

    return {
                'width': dimension.group(1),
                'height': dimension.group(2),
                'page_count': int(page_count.group(1)),
            }


def convert_image_to_pdf_page(image_file, page_width, page_height):
    # convert image.jpg -page 540x650\! image.pdf
    tmp_dir = tempfile.mkdtemp()
    tmp_pdf = os.path.join(tmp_dir, 'tmp.pdf')
    command = ['convert',
               image_file,
               '-page',
               '{}x{}'.format(page_width, page_height),
               tmp_pdf]
    print(' '.join(command))
    run.run(command)
    return tmp_pdf


def assemble_pdf(main_pdf, insert_pdf, page_count, page_number):
    # pdftk A=book.pdf B=image.pdf cat A1-12 B3 A14-end output out.pdf

    command = ['pdftk',
               'A={}'.format(main_pdf),
               'B={}'.format(insert_pdf),
               'cat']

    if page_number > 1:
        pre_insert = 'A1'
        if page_number > 2:
            pre_insert += '-{}'.format(page_number - 1)
        command.append(pre_insert)

    command.append('B1')

    if page_number < page_count:
        command.append('A{}-end'.format(page_number + 1))

    command += ['output', 'out.pdf']
    print(' '.join(command))
    run.run(command)


def get_parser():
    """The argument parser for the command line interface.

    :return: A ArgumentParser object.
    :rtype: argparse.ArgumentParser
    """
    parser = argparse.ArgumentParser(
        description='Add or replace one page in a PDF file with an image '
        'file of the same page size.',
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

    ##
    # add
    ##

    add_parser = subcommand.add_parser(
        'add', description=''
    )

    add_parser.add_argument(
        '-a, --after', help=''
    )

    add_parser.add_argument(
        '-b, --before', help=''
    )

    ##
    # replace
    ##

    replace_parser = subcommand.add_parser(
        'replace', description=''
    )

    replace_parser.add_argument(
        'pdf',
        help='The PDF file',
    )

    replace_parser.add_argument(
        'number',
        type=int,
        help='The page number of the PDF page to replace',
    )

    replace_parser.add_argument(
        'image',
        help='The image file to replace the PDF page with',
    )

    return parser


def main():
    args = get_parser().parse_args()

    run.setup(verbose=args.verbose, colorize=args.colorize)

    check_bin(*dependencies)

    if args.subcommand == 'replace':

        info = get_pdf_info(args.pdf)
        image_pdf = convert_image_to_pdf_page(args.image, info['width'],
                                              info['height'])
        assemble_pdf(args.pdf, image_pdf, info['page_count'], args.number)


if __name__ == '__main__':
    main()
