#! /usr/bin/env python3

from jfscripts._utils import check_bin, FilePath, Run
import argparse
import os
import re
import tempfile
import textwrap

run = Run()

line_length = 72

tmp_dir = tempfile.mkdtemp()
output_file = open('export.txt', 'w')
dependencies = (
    ('pdftotext', 'poppler'),
    ('pdfinfo', 'poppler'),
)


class Txt(object):

    def __init__(self, path):
        self.path = path
        self.file = open(str(path), 'w')

    def add_line(self, line):
        self.file.write(line + '\n')
        print(line)


def get_page_count(pdf):
    pdfinfo_stdout = run.check_output(['pdfinfo', str(pdf)])
    match = re.search('Pages:\s*(.*)\n', pdfinfo_stdout.decode('utf-8'))
    if match:
        return int(match.group(1))


def get_text_per_page(pdf, page, txt_file):
    page = str(page)
    tmp_txt_path = os.path.join(tmp_dir, page + '.txt')
    run.check_output([
        'pdftotext',
        '-f', page,
        '-l', page,
        str(pdf),
        tmp_txt_path
    ])

    tmp_txt_file = open(tmp_txt_path, 'r')
    lines = tmp_txt_file.read().splitlines()
    full_lines = []
    for line in lines:
        if len(line) > 20:
            full_lines.append(line)

    text_of_page = ' '.join(full_lines)
    text_of_page = text_of_page.replace("'", u'’')
    text_of_page = re.sub(r'[^a-zäöüA-ZÄÖÜß0-9 ]', '', text_of_page)
    text_of_page = re.sub(r'\s+', ' ', text_of_page)

    wrapped_lines = textwrap.wrap(text_of_page, line_length)
    for line in wrapped_lines:
        txt_file.add_line(line)


def get_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'file',
        help='A PDF file containing text',
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

    return parser


def main():
    args = get_parser().parse_args()

    run.setup(verbose=args.verbose, colorize=args.colorize)

    check_bin(*dependencies)

    pdf = FilePath(args.file, absolute=True)
    txt_path = pdf.new(extension='txt')
    txt_file = Txt(txt_path)

    page_count = get_page_count(pdf)

    txt_file.add_line('# ' + pdf.basename)

    for i in range(1, page_count + 1):
        txt_file.add_line('')
        txt_file.add_line('-' * line_length)
        txt_file.add_line('')
        txt_file.add_line('## Seite ' + str(i))
        txt_file.add_line('')
        get_text_per_page(pdf, i, txt_file)


if __name__ == '__main__':
    main()
