#! /usr/bin/env python3

from jfscripts import __version__
from jfscripts._utils import check_dependencies, Run, FilePath
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
    cmd_args = ['pdftk', str(pdf_file), 'cat', '1', 'output', output_file]
    run.run(cmd_args)
    return output_file


def do_magick_identify_dimensions(pdf_file):
    """"""
    cmd_args = ['magick', 'identify', '-format', 'w: %w h: %h x: %x y: %y\n',
                str(pdf_file)]
    output = run.check_output(cmd_args, encoding='utf-8')
    dimensions = re.search(r'w: (\d*) h: (\d*) x: (\d*) y: (\d*)', output)

    return {
                'width': int(dimensions.group(1)),
                'height': int(dimensions.group(2)),
                'x': int(dimensions.group(3)),
                'y': int(dimensions.group(4)),
            }


def get_pdf_info(pdf_file):
    output = run.check_output(['pdfinfo', str(pdf_file)])
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

    # pdf_density_x    x
    # -------------  = -----------
    # pdf_width        image_width

    # x = pdf_density_x / pdf_width * image_width

    # image_width: 1024
    # pdf_width: 542
    # pdf_density_x: 72

    # 72 / 542 * 1024 = 136,0295

    dimension = '{}x{}'.format(page_width, page_height)
    density = '{}x{}'.format(density_x, density_y)
    tmp_pdf = os.path.join(tmp_dir, 'tmp.pdf')
    cmd_args = ['convert', str(image_file), '-compress', 'JPEG',
                '-quality', '8',
                '-resize', dimension,
                '-density', density,
                tmp_pdf]
    run.run(cmd_args)
    return FilePath(tmp_pdf)


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

    # add after page 12
    # A1-12 B1 A13-end
    # add before page 12
    # A1-11 B1 A12-end

    # replace page 12
    # A1-11 B1 A13-end

    # page_insert_begin: Page before the insert
    # page_insert_end: Page after the insert

    page_insert_begin = page_number - 1

    # add before page 12
    # A1-11 B1 A12-end
    if position == 'after':
        page_insert_begin = page_number

    page_insert_end = page_insert_begin + 1

    # A1-12 B1 A14-end
    if mode == 'replace':
        page_insert_end += 1

    if mode == 'add' and page_number == 1 and position == 'before':
        cmd_args = [str(insert_pdf), str(main_pdf), 'cat']

    elif mode == 'add' and page_number == page_count and position == 'after':
        cmd_args = [str(main_pdf), str(insert_pdf), 'cat']

    else:

        cmd_args = ['A={}'.format(main_pdf),
                    'B={}'.format(insert_pdf),
                    'cat']

        if page_number > 1:
            pre_insert = 'A1'
            if page_insert_begin >= 2:
                pre_insert += '-{}'.format(page_insert_begin)
            cmd_args.append(pre_insert)

        cmd_args.append('B1')

        if page_insert_end == page_count:
            cmd_args.append('A{}'.format(page_insert_end))

        elif page_insert_end < page_count:
            cmd_args.append('A{}-end'.format(page_insert_end))

    joined_pdf = main_pdf.new(append='_joined')

    cmd_args = ['pdftk'] + cmd_args + ['output', str(joined_pdf)]
    run.run(cmd_args)
    return joined_pdf


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

    convert_parser.add_argument(
        'image',
        help='The image file to convert to the PDF format.',
    )

    convert_parser.add_argument(
        'pdf',
        help='The PDF file (to get the dimensions) .',
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

    main_pdf = FilePath(args.pdf, absolute=True)
    image = FilePath(args.image, absolute=True)
    if hasattr(args, 'number'):
        number = args.number

    identify_pdf = do_pdftk_cat_first_page(main_pdf)
    dimensions = do_magick_identify_dimensions(identify_pdf)
    info = get_pdf_info(main_pdf)
    insert_pdf = convert_image_to_pdf_page(
        image,
        dimensions['width'],
        dimensions['height'],
        dimensions['x'],
        dimensions['y'],
    )

    if args.subcmd_args == 'add':

        if args.after:
            number = int(args.after[0])
            position = 'after'
        elif args.before:
            number = int(args.before[0])
            position = 'before'
        else:
            number = info['page_count']
            position = 'after'

        joined_pdf = assemble_pdf(main_pdf, insert_pdf, info['page_count'],
                                  number, mode='add', position=position)
        message = 'Successfully added the image “{}” {} page {} of the PDF ' \
                  'file “{}”. Result: “{}”'
        print(message.format(image, position, number, main_pdf, joined_pdf))

    elif args.subcmd_args == 'convert':
        result_pdf = main_pdf.new(append='_insert')
        os.rename(str(insert_pdf), str(result_pdf))
        message = 'Successfully converted the image “{}” to the PDF file ' \
                  '“{}” using the dimensions of the PDF “{}”.'
        print(message.format(image, result_pdf, main_pdf))

    elif args.subcmd_args == 'replace':
        joined_pdf = assemble_pdf(main_pdf, insert_pdf, info['page_count'],
                                  args.number, mode='replace')
        message = 'Successfully replaced page {} of the PDF file “{}” with ' \
                  'the image “{}”. Result: “{}”'
        print(message.format(number, main_pdf, image, joined_pdf))


if __name__ == '__main__':
    main()
