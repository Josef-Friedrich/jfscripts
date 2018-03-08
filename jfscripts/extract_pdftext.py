#! /usr/bin/env python3

import argparse
from subprocess import check_output
import os
import re
import tempfile
import textwrap

tmp_dir = tempfile.mkdtemp()

output_file = open('export.txt', 'w')

parser = argparse.ArgumentParser()
parser.add_argument("file", help="A PDF file containing text")
args = parser.parse_args()

pdf_file = os.path.abspath(args.file)


def output(line):
    output_file.write(line + '\n')
    print(line)


def get_page_count(pdf_file):
    pdfinfo_stdout = check_output(['pdfinfo', pdf_file])
    match = re.search('Pages:\s*(.*)\n', pdfinfo_stdout.decode('utf-8'))
    if match:
        return int(match.group(1))


def get_text_per_page(pdf_file, page):
    page = str(page)
    txt_path = os.path.join(tmp_dir, page + '.txt')
    check_output([
        'pdftotext',
        '-f', page,
        '-l', page,
        pdf_file,
        txt_path
    ])

    txt_file = open(txt_path, 'r')
    lines = txt_file.read().splitlines()
    full_lines = []
    for line in lines:
        if len(line) > 20:
            full_lines.append(line)

    text_of_page = ' '.join(full_lines)
    text_of_page = text_of_page.replace("'", u'’')
    text_of_page = re.sub(r'[^a-zäöüA-ZÄÖÜß0-9 ]', '', text_of_page)
    text_of_page = re.sub(r'\s+', ' ', text_of_page)

    wrapped_lines = textwrap.wrap(text_of_page, 72)
    for line in wrapped_lines:
        output(line)


page_count = get_page_count(pdf_file)

output('# ' + os.path.basename(pdf_file))

for i in range(1, page_count + 1):
    output('')
    output('-----------------------------------------------------------------')
    output('')
    output('## Seite ' + str(i))
    output('')
    get_text_per_page(pdf_file, i)
