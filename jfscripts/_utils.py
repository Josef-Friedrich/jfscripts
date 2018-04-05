import shutil
import subprocess
from termcolor import colored


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
