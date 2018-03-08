#! /usr/bin/env python3

import argparse
import shutil
import subprocess
import re


def check_executable(command):
    if not shutil.which(command):
        raise SystemError('Command “{}” not found.'.format(command))


def get_pdf_page_dimensions(pdf_file):
    output = subprocess.check_output(['pdfinfo', pdf_file])
    output = output.decode('utf-8')
    # Page size:      522.249 x 644.573 pts
    match = re.search(r'Page size:\s*([0-9.]*) x ([0-9.]*)\s*pts', output)
    return (match.group(1), match.group(2))


def convert_image_to_pdf_page(image_file, page_width, page_height):
    #convert musi-001.jpg -page 540x650\! out.pdf


check_executable('pdfinfo')

parser = argparse.ArgumentParser(description='Replace one page in a PDF file with an image file.')
parser.add_argument('pdf', help='The PDF file')
parser.add_argument('number', help='The page number of the PDF page to replace')
parser.add_argument('image',  help='The image file to replace the PDF page with')

args = parser.parse_args()

page_width, page_height = get_pdf_page_dimensions(args.pdf)

print(page_height)
