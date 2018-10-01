import shutil
import subprocess
from termcolor import colored
import os


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
        if self.verbose:
            self._print_cmd(args[0])
        return subprocess.run(*args, **kwargs)

    def check_output(self, *args, **kwargs):
        if self.verbose:
            self._print_cmd(args[0])
        return subprocess.check_output(*args, **kwargs)


def check_bin(*executables, raise_error=True):
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
