import unittest
import subprocess
from urllib.request import urlretrieve
import os


def download(url_path, local_path):
    url = 'https://github.com/Josef-Friedrich/test-files/raw/master/{}' \
        .format(url_path)
    urlretrieve(url, local_path)


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
