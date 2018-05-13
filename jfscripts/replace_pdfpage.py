#! /usr/bin/env python3

from jfscripts._utils import check_bin, Run
import argparse
import os
import re
import tempfile

run = Run()


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
    parser = argparse.ArgumentParser(
        description='Replace one page in a PDF file with an image file.',
    )

    parser.add_argument(
        'pdf',
        help='The PDF file',
    )
    parser.add_argument(
        'number',
        type=int,
        help='The page number of the PDF page to replace',
    )
    parser.add_argument(
        'image',
        help='The image file to replace the PDF page with',
    )
    return parser


def main():
    args = get_parser().parse_args()

    run.setup(verbose=args.verbose, colorize=args.colorize)

    check_bin('pdfinfo', 'pdftk', 'convert')

    info = get_pdf_info(args.pdf)
    image_pdf = convert_image_to_pdf_page(args.image, info['width'],
                                          info['height'])
    assemble_pdf(args.pdf, image_pdf, info['page_count'], args.number)


if __name__ == '__main__':
    main()
