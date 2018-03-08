#! /usr/bin/env python3

import csv
import yaml
import argparse

parser = argparse.ArgumentParser(description='Convert each row of an CSV '
                                 'file to an YAML file.')
parser.add_argument('csv', metavar='CSVFILE', help='A CSV file')
args = parser.parse_args()

in_file = open(args.csv, 'r')


def convert_to_yaml(header, line, counter):
    values = {}
    for index, key in enumerate(header):
        values[key.lower()] = line[index]

    out = open('{}.yml'.format(counter), 'w')
    out.write('---\n')
    out.write(yaml.dump(values, default_flow_style=False))
    out.write('---\n')
    out.close()


try:
    reader = csv.reader(in_file)
    header = next(reader)  # skip headers
    for counter, line in enumerate(reader):
        convert_to_yaml(header, line, counter)

finally:
    in_file.close()
