import unittest
import subprocess
import shutil
from urllib.request import urlretrieve
import os


def check_bin(*executables):
    for executable in executables:
        if isinstance(executable, tuple):
            if not shutil.which(executable[0]):
                return False

        else:
            if not shutil.which(executable):
                return False

    return True


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

    def assertExists(self, path):
        self.assertTrue(os.path.exists(path))

    def assertExistsNot(self, path):
        self.assertFalse(os.path.exists(path))
