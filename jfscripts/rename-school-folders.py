#! /usr/bin/env python3

import os
import re

path = '.'


def replace_german_umlaute(string):
    umlaute = {'ae': u'ä', 'oe': u'ö', 'ue': u'ü', 'Ae': u'Ä', 'Oe': u'Ö',
               'Ue': u'Ü'}
    for replace, search in umlaute.iteritems():
        string = string.replace(search, replace)
    return string


def transliterate(string):
    import unidecode
    return unidecode.unidecode(string)


def delete_characters(string, *characters):
    for character in characters:
        string = string.replace(character, '')
    return string


def rename(string):
    string = replace_german_umlaute(string)
    string = re.sub('(\d+) ', r'\1_', string)
    string = delete_characters(string, '„', '“', ',', '\'', '(', ')')
    string = transliterate(string)
    string = string.replace(' ', '-')
    string = string.replace(';', '_')
    string = string.replace('---', '_')
    string = string.replace('--', '-')
    return string


for root, dirs, files in os.walk(path):
    level = root.count(os.path.sep)
    for folder in dirs:

        if re.findall('^\d+ ', folder):
            old = folder
            new = folder
            new = rename(new)

            print(old + ' -> ' + new)
            os.rename(os.path.join(root, old), os.path.join(root, new))
