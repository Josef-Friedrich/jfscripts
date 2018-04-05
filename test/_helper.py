import unittest
import subprocess
from urllib.request import urlretrieve
import os
from io import StringIO
import sys
import socket


def check_internet_connectifity(host="8.8.8.8", port=53, timeout=3):
    """
    https://stackoverflow.com/a/33117579
    Host: 8.8.8.8 (google-public-dns-a.google.com)
    OpenPort: 53/tcp
    Service: domain (DNS/TCP)
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except Exception:
        return False


def download(url_path, local_path):
    url = 'https://github.com/Josef-Friedrich/test-files/raw/master/{}' \
        .format(url_path)
    urlretrieve(url, local_path)


class Capturing(list):

    def __init__(self, channel='out'):
        self.channel = channel

    def __enter__(self):
        if self.channel == 'out':
            self._pipe = sys.stdout
            sys.stdout = self._stringio = StringIO()
        elif self.channel == 'err':
            self._pipe = sys.stderr
            sys.stderr = self._stringio = StringIO()
        return self

    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        if self.channel == 'out':
            sys.stdout = self._pipe
        elif self.channel == 'err':
            sys.stderr = self._pipe


class TestCase(unittest.TestCase):

    def assertIsExecutable(self, module):
        command = '{}.py'.format(module.replace('_', '-'))
        usage = 'usage: {}'.format(command)

        run = subprocess.run([command], encoding='utf-8',
                             stderr=subprocess.PIPE)
        self.assertEqual(run.returncode, 2)
        self.assertTrue(usage in run.stderr)

        run = subprocess.run(['./jfscripts/{}.py'.format(module)],
                             encoding='utf-8',
                             stderr=subprocess.PIPE)
        self.assertEqual(run.returncode, 2)
        self.assertTrue(usage.replace('-', '_') in run.stderr)

        run = subprocess.run([command, '-h'], encoding='utf-8',
                             stdout=subprocess.PIPE)
        self.assertEqual(run.returncode, 0)
        self.assertTrue(usage in run.stdout)

    def assertExists(self, path, message=None):
        self.assertTrue(os.path.exists(path), message)

    def assertExistsNot(self, path, message=None):
        self.assertFalse(os.path.exists(path), message)
