from io import StringIO
from termcolor import colored
import os
import re
import shutil
import subprocess
import sys


class Run(object):

    PIPE = subprocess.PIPE

    def __init__(self, *args, **kwargs):
        self.setup(*args, **kwargs)

    def setup(self, verbose=False, colorize=False):
        self.verbose = verbose
        self.colorize = colorize

    def _print_cmd(self, cmd):
        if self.colorize:
            output = []
            for arg in cmd:
                if arg.startswith('--'):
                    output.append(colored(arg, color='yellow'))
                elif arg.startswith('-'):
                    output.append(colored(arg, color='blue'))
                elif os.path.exists(arg):
                    output.append(colored(arg, color='white',
                                  on_color='on_cyan'))
                else:
                    output.append(arg)
            print(' '.join(output))
        else:
            print(' '.join(cmd))

    def run(self, *args, **kwargs):
        """
        :return: A `CompletedProcess` object.
        :rtype: subprocess.CompletedProcess
        """
        if self.verbose:
            self._print_cmd(args[0])
        return subprocess.run(*args, **kwargs)

    def check_output(self, *args, **kwargs):
        if self.verbose:
            self._print_cmd(args[0])
        return subprocess.check_output(*args, **kwargs)


def check_dependencies(*executables, raise_error=True):
    """Check if the given executables are existing in $PATH.

    :param tuple executables: A tuple of executables to check for their
      existence in $PATH. Each element of the tuple can be either a string
      (e. g. `pdfimages`) or a itself a tuple `('pdfimages', 'poppler')`.
      The first entry of this tuple is the name of the executable the second
      entry is a description text which is displayed in the raised exception.

    :param bool raise_error: Raise an error if an executable doesn’t exist.

    :return: True or False. True if all executables exist. False if one or
      more executables not exist.
    :rtype: bool
    """
    errors = []
    for executable in executables:
        if isinstance(executable, tuple):
            if not shutil.which(executable[0]):
                errors.append('{} ({})'.format(executable[0], executable[1]))
        else:
            if not shutil.which(executable):
                errors.append(executable)

    if errors:
        if raise_error:
            raise SystemError('Some commands are not installed: ' +
                              ', '.join(errors))
        else:
            return False
    else:
        return True


class FilePath(object):

    def __init__(self, path, absolute=False):
        self.absolute = absolute
        """Boolean, indicates wheter the path is an absolute path or an
        relative path."""

        if self.absolute:
            self.path = os.path.abspath(path)
            """The absolute (`/home/document/file.ext`) or the relative path
            (`document/file.ext`) of the file."""
        else:
            self.path = os.path.relpath(path)

        self.filename = os.path.basename(path)
        """The filename is the combination of the basename and the
        extension, e. g. `file.ext`."""

        self.extension = os.path.splitext(self.path)[1][1:]
        """The extension of the file, e. g. `ext`."""

        self.basename = self.filename[:-len(self.extension) - 1]
        """The basename of the file, e. g. `file`."""

        self.base = self.path[:-len(self.extension) - 1]
        """The path without an extension, e. g. `/home/document/file`."""

    def __str__(self):
        return self.path

    def __eq__(self, other):
        return self.path == other.path

    def _export(self, path):
        return FilePath(path, self.absolute)

    def new(self, extension=None, append='', del_substring=''):
        """
        :param str extension: The extension of the new file path.
        :param str append: String to append on the basename. This string
          is located before the extension.
        :param str del_substring: String to delete from the new file path.

        :return: A new file path object.
        :rtype: FilePath
        """
        if not extension:
            extension = self.extension
        new = '{}{}.{}'.format(self.base, append, extension)
        if del_substring:
            new = new.replace(del_substring, '')
        return self._export(new)

    def remove(self):
        """Remove the file."""
        os.remove(self.path)


class Capturing(list):
    """Capture the stdout or stdeer output. This class is designed for unit
    tests.

    :param str channel: `stdout` or `stderr`.
    :param bool clean_ansi: Clean out ANSI colors from the captured output.

    .. seealso::

        `Answer on Stackoverflow <https://stackoverflow.com/a/16571630>`_
    """

    def __init__(self, channel='stdout', clean_ansi=False):
        if channel not in ['stdout', 'stderr']:
            raise(ValueError('“channel” must be either “stdout” or “stderr”'))
        self.channel = channel
        self.clean_ansi = clean_ansi

    def __enter__(self):
        if self.channel == 'stdout':
            self._pipe = sys.stdout
            sys.stdout = self._stringio = StringIO()
        elif self.channel == 'stderr':
            self._pipe = sys.stderr
            sys.stderr = self._stringio = StringIO()
        return self

    def __exit__(self, *args):
        if self.clean_ansi:
            output = self._clean_ansi(self._stringio.getvalue())
        else:
            output = self._stringio.getvalue()
        self.extend(output.splitlines())
        del self._stringio
        if self.channel == 'stdout':
            sys.stdout = self._pipe
        elif self.channel == 'stderr':
            sys.stderr = self._pipe

    def tostring(self):
        """Convert the output into an string. By default a list of output
        lines is returned."""
        return '\n'.join(self)

    @staticmethod
    def _clean_ansi(text):
        return re.sub(r'\x1b.*?m', '', text)


def argparser_to_readme(argparser, template='README-template.md',
                        destination='README.md', indentation=0,
                        placeholder='{{ argparse }}'):
    """Add the formatted help output of a command line utility using the
    Python module `argparse` to a README file.

    :param object argparser: The argparse parser object.
    :param str template: The path of a template text file containing the
      placeholder. Default: `README-template.md`
    :param str destination: The path of the destination file. Default:
      `README.me`
    :param int indentation: Indent the formatted help output by X spaces.
      Default: 0
    :param str placeholder: Placeholder string that gets replaced by the
      formatted help output. Default: `{{ argparse }}`
    """
    help_string = argparser().format_help()

    if indentation > 0:
        indent_lines = []
        lines = help_string.split('\n')
        for line in lines:
            indent_lines.append(' ' * indentation + line)

        help_string = '\n'.join(indent_lines)

    with open(template, 'r', encoding='utf-8') as template_file:
        template_string = template_file.read()
        readme = template_string.replace(placeholder, help_string)

    readme_file = open(destination, 'w')
    readme_file.write(readme)
    readme_file.close()
