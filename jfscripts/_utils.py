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
        if self.absolute:
            self.path = os.path.abspath(path)
        else:
            self.path = os.path.relpath(path)
        # file.ext
        self.filename = os.path.basename(path)
        # ext
        self.extension = os.path.splitext(self.path)[1][1:]
        # file
        self.basename = self.filename[:-len(self.extension) - 1]
        # /home/file
        self.base = self.path[:-len(self.extension) - 1]

    def __str__(self):
        return self.path

    def __eq__(self, other):
        return self.path == other.path

    def _export(self, path):
        return FilePath(path, self.absolute)

    def new(self, extension=None, append='', del_substring=''):
        if not extension:
            extension = self.extension
        new = '{}{}.{}'.format(self.base, append, extension)
        if del_substring:
            new = new.replace(del_substring, '')
        return self._export(new)

    def remove(self):
        os.remove(self.path)
