#! /usr/bin/env python3

import re
import subprocess
import os


def path(*path_segments):
    return os.path.join(os.getcwd(), *path_segments)


def open_file(*path_segments):
    file_path = path(*path_segments)
    open(file_path, 'w').close()
    return open(file_path, 'a')

def get_commands():
    setup_py = open('setup.py', 'r')
    lines = setup_py.read()
    return re.findall(r' {8,}\'([a-z0-9-]*.py) = jfscripts.[a-z0-9_]*:main\',',
                      lines)


def get_help(command):
    return subprocess.Popen('{} --help'.format(command), shell=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def heading(text):
    return '\n{}\n{}\n\n.. code-block:: text\n\n'.format(text, '-' * len(text))


def main():
    commands = get_commands()

    header = open(path('README_header.rst'), 'r')
    readme = open_file('README.rst')
    sphinx = open_file('doc', 'source', 'cli.rst')

    sphinx_header = (
        'Comande line interface\n',
        '======================\n',
        '\n',
        '.. code-block:: text\n',
        '\n',
    )

    for line in sphinx_header:
        sphinx.write(str(line))

    # footer = open(path('README_footer.rst'), 'r')

    for line in header:
        readme.write(line)

    readme.write('\n')
    for command in commands:
        print(command)
        _help = get_help(command)
        _help.wait()
        readme.write(heading(command))
        sphinx.write(heading(command))

        for line in _help.stdout:
            indented_line = '    ' + line.decode('utf-8')
            readme.write(indented_line)
            sphinx.write(indented_line)

    # for line in footer:
    #     readme.write(line)

    readme.close()
    # sphinx.close()


if __name__ == '__main__':
    main()
