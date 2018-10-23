#! /usr/bin/env python3

from jfscripts import __version__
from jfscripts._utils import check_dependencies, Run
import argparse
import os
import re
import tempfile

run = Run()

dependencies = ('pdfinfo', 'pdftk', 'convert')

tmp_dir = tempfile.mkdtemp()


def do_pdftk_cat_first_page(pdf_file):
    """The cmd_args magick identify is very slow on page pages hence it
    examines every page. We extract the first page to get some informations
    about the dimensions of the PDF file."""

    output_file = os.path.join(tmp_dir, 'identify.pdf')

    cmd_args = ['pdftk', pdf_file, 'cat', '1', 'output', output_file]
    run.run(cmd_args)
    return output_file


def do_magick_identify_dimensions(pdf_file):
    """"""
    cmd_args = ['magick', 'identify', '-format', 'w: %w h: %h x: %x y: %y\n',
                pdf_file]
    output = run.check_output(cmd_args, encoding='utf-8')
    dimensions = re.search(r'w: (\d*) h: (\d*) x: (\d*) y: (\d*)', output)

    return {
                'width': int(dimensions.group(1)),
                'height': int(dimensions.group(2)),
                'x': int(dimensions.group(3)),
                'y': int(dimensions.group(4)),
            }


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


def convert_image_to_pdf_page(image_file, page_width, page_height, density_x,
                              density_y):
    # convert image.jpg -page 540x650\! image.pdf
    dimension = '{}x{}'.format(page_width, page_height)
    density = '{}x{}'.format(density_x, density_y)
    tmp_pdf = os.path.join(tmp_dir, 'tmp.pdf')
    cmd_args = ['convert', image_file, '-compress', 'JPEG', '-quality', '8',
                '-resize', dimension,
                '-density', density,
                tmp_pdf]
    run.run(cmd_args)
    return tmp_pdf


def assemble_pdf(main_pdf, insert_pdf, page_count, page_number, mode='add',
                 position='before'):
    """
    :param str main_pdf: Path of the main PDF file.
    :param str insert_pdf: Path of the PDF file to insert into the main PDF
      file.
    :param int page_count: Page count of the main PDF file.
    :param int page_number: Page number in the main PDF file to add / to
      replace the insert PDF file.
    :param string mode: Mode how the PDF to insert is treated. Possible choices
      are: `add` or `replace`.
    :param str position: Possible choices: `before` and `after`
    """
    # pdftk A=book.pdf B=image.pdf cat A1-12 B3 A14-end output out.pdf

    # add
    # A1-12 B1 A13-end

    # add after page 12
    # A1-12 B1 A13-end
    # add before page 12
    # A1-11 B1 A12-end

    # replace
    # A1-12 B1 A14-end

    if mode == 'replace':

        cmd_args = ['A={}'.format(main_pdf),
                    'B={}'.format(insert_pdf),
                    'cat']

        if page_number > 1:
            pre_insert = 'A1'
            if page_number > 2:
                pre_insert += '-{}'.format(page_number - 1)
            cmd_args.append(pre_insert)

        cmd_args.append('B1')

        if page_number < page_count:
            cmd_args.append('A{}-end'.format(page_number + 1))

    elif mode == 'add':

        if page_number == 1 and position == 'before':
            cmd_args = [insert_pdf, main_pdf, 'cat']

        elif page_number == page_count and position == 'after':
            cmd_args = [main_pdf, insert_pdf, 'cat']

    cmd_args = ['pdftk'] + cmd_args + ['output', 'out.pdf']
    run.run(cmd_args)


def get_parser():
    """The argument parser for the cmd_args line interface.

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
        help='Make the cmd_args line output more verbose.',
    )

    parser.add_argument(
        '-V',
        '--version',
        action='version',
        version='%(prog)s {version}'.format(version=__version__),
    )

    subcmd_args = parser.add_subparsers(
        dest='subcmd_args',
        help='Subcmd_args',
    )
    subcmd_args.required = True



    ##
    # add
    ##

    add_parser = subcmd_args.add_parser(
        'add',
        description='Add one image to an PDF file.'
    )

    add_parser.add_argument(
        '-a', '--after',
        nargs=1,
        help='Place image after page X.'
    )

    add_parser.add_argument(
        '-b', '--before',
        nargs=1,
        help='Place image before page X.'
    )

    add_parser.add_argument(
        'image',
        help='The image file to add to the PDF page.',
    )

    add_parser.add_argument(
        'pdf',
        help='The PDF file.',
    )

    ##
    # convert
    ##

    convert_parser = subcmd_args.add_parser(
        'convert',
        description='Convert a image file into a PDF file with the same '
        'dimensions.'
    )

    add_parser.add_argument(
        '-a', '--after',
        nargs=1,
        help='Place image after page X.'
    )

    ##
    # replace
    ##

    replace_parser = subcmd_args.add_parser(
        'replace',
        description='Replace one page in a PDF file with an image file.'
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

    check_dependencies(*dependencies)

    output_file = do_pdftk_cat_first_page(args.pdf)
    dimensions = do_magick_identify_dimensions(output_file)
    info = get_pdf_info(args.pdf)
    image_pdf = convert_image_to_pdf_page(
        args.image,
        dimensions['width'],
        dimensions['height'],
        dimensions['x'],
        dimensions['y'],
    )
    if args.subcmd_args == 'add':
        print(dimensions)

    elif args.subcmd_args == 'replace':

        assemble_pdf(args.pdf, image_pdf, info['page_count'], args.number)


if __name__ == '__main__':
    main()
