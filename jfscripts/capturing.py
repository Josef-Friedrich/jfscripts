from io import StringIO
import sys


class Capturing(list):
    """see https://stackoverflow.com/a/16571630"""

    def __init__(self, channel='stdout'):
        self.channel = channel

    def __enter__(self):
        if self.channel == 'stdout':
            self._pipe = sys.stdout
            sys.stdout = self._stringio = StringIO()
        elif self.channel == 'stderr':
            self._pipe = sys.stderr
            sys.stderr = self._stringio = StringIO()
        return self

    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio
        if self.channel == 'stdout':
            sys.stdout = self._pipe
        elif self.channel == 'stderr':
            sys.stderr = self._pipe
