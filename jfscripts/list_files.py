#! /usr/bin/env python3

from jfscripts import __version__
from pathlib import Path
import argparse
import fnmatch
import os
import re


def is_glob(string):
    if re.search(r'[\*\?]', string) or re.search(r'\[\!?.*\]', string):
        return True
    else:
        return False


def common_path(paths):
    common_path = os.path.commonpath(paths)
    if os.path.isdir(common_path):
        return common_path
    else:
        return str(Path(common_path).parent.resolve())


def _split_glob(glob_path):
    """Split a file path (e. g.: /data/(asterisk).txt) containing glob wildcard
    characters in a glob free path prefix (e. g.: /data) and a glob
    pattern (e. g. (asterisk).txt).

    :param str glob_path: A file path containing glob wildcard characters.
    """
    globs = glob_path.split(os.path.sep)
    no_globs = []
    for g in globs:
        if not is_glob(g):
            no_globs.append(g)
        else:
            break
    if not no_globs:
        dir_path = '.'
    else:
        dir_path = os.path.sep.join(no_globs)
    return (
        dir_path,
        os.path.sep.join(globs[len(no_globs):]),
    )


def _list_files_all(dir_path):
    out = []
    for root, dirs, files in os.walk(dir_path):
        for d in dirs:
            out.append(os.path.join(root, d))
        for f in files:
            out.append(os.path.join(root, f))
    out.sort()
    return out


def _list_files_filter(dir_path, glob_pattern):
    out = []
    for root, dirs, files in os.walk(dir_path):
        relroot = root[len(dir_path):]
        for f in files:
            relfiles = os.path.join(relroot, f)
            if fnmatch.fnmatch(relfiles, glob_pattern):
                out.append(os.path.join(root, f))
    out.sort()
    return out


def list_files(files, default_glob=None):
    """
    :param list files: A list of file paths or a single element list containing
      a glob string.

    :param string default_glob: A default glob pattern like “(asterisk).txt”.
      This argument is only taken into account, if “element” is a list with
      only one entry and this entry is a path to a directory.
    """
    if len(files) > 1:
        return files

    file_path = files[0]

    if not is_glob(file_path):
        if os.path.isdir(file_path):
            if default_glob:
                return _list_files_filter(file_path, default_glob)
            else:
                return _list_files_all(file_path)
        else:  # not a directory
            return [file_path]

    else:  # is glob
        glob_prefix, glob_pattern = _split_glob(file_path)
        return _list_files_filter(glob_prefix, glob_pattern)

    raise ValueError('Something went wrong.')


def doc_examples(command_name='', extension='txt', indent_spaces=0,
                 inline=False):
    examples = (
        'a.{}'.format(extension),
        'a.{0} b.{0} c.{0}'.format(extension),
        '(asterisk).{}'.format(extension),
        '"(asterisk).{}"'.format(extension),
        'dir/',
        '"dir/(asterisk).{}"'.format(extension),
    )

    if command_name or indent_spaces:
        prefix = '{}{} '.format(' ' * indent_spaces, command_name)
    else:
        prefix = ''

    out = []
    for example in examples:
        command = '{}{}'.format(prefix, example)
        if inline:
            command = '“{}”'.format(command)
        out.append(command)

    if inline:
        join_phrase = ', '
    else:
        join_phrase = '\n'

    return join_phrase.join(out)


def get_parser():
    """The argument parser for the command line interface.

    :return: A ArgumentParser object.
    :rtype: argparse.ArgumentParser
    """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='This is a script to demonstrate the list_files() '
        'function in this file.\n\n' + doc_examples('list-files.py', 'txt')
    )

    parser.add_argument(
        'input_files',
        help='Examples for this arguments are: ' + doc_examples(inline=True),
        nargs='+',
    )

    parser.add_argument(
        '-V',
        '--version',
        action='version',
        version='%(prog)s {version}'.format(version=__version__),
    )

    return parser


def main():
    args = get_parser().parse_args()
    files = list_files(args.input_files)
    if files:
        for f in files:
            print(f)
    else:
        print('Nothing found to list. :-(')


if __name__ == '__main__':
    main()
