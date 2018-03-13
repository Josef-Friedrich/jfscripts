import unittest
from unittest import mock
from jfscripts import replace_pdfpage as replace
import subprocess


class TestUnits(unittest.TestCase):

    @mock.patch('jfscripts.replace_pdfpage.check_executables')
    def test_main(self, check_executable):
        with unittest.mock.patch('sys.argv',  ['cmd']):
            with self.assertRaises(SystemExit):
                replace.main()


class TestIntegration(unittest.TestCase):

    def test_without_arguments(self):
        run = subprocess.run(['replace-pdfpage.py'], encoding='utf-8',
                             stderr=subprocess.PIPE)
        self.assertEqual(run.returncode, 2)
        self.assertTrue('usage: replace-pdfpage.py' in run.stderr)

    def test_direct_execution(self):
        run = subprocess.run(['./jfscripts/replace_pdfpage.py'],
                             encoding='utf-8',
                             stderr=subprocess.PIPE)
        self.assertEqual(run.returncode, 2)
        self.assertTrue('usage: replace_pdfpage.py' in run.stderr)

    def test_help(self):
        run = subprocess.run(['replace-pdfpage.py', '-h'], encoding='utf-8',
                             stdout=subprocess.PIPE)
        self.assertEqual(run.returncode, 0)
        self.assertTrue('usage: replace-pdfpage.py' in run.stdout)


if __name__ == '__main__':
    unittest.main()
