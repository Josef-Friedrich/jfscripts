import shutil
import subprocess


class Run(object):

    PIPE = subprocess.PIPE

    def __init__(self, *args, **kwargs):
        self.setup(*args, **kwargs)

    def setup(self, verbose=False):
        self.verbose = verbose

    def _print_cmd(self, cmd):
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
