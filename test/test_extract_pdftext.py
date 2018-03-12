import unittest
import subprocess


class TestIntegration(unittest.TestCase):

    def test_without_arguments(self):
        run = subprocess.run(['extract-pdftext.py'], encoding='utf-8',
                             stderr=subprocess.PIPE)
        self.assertEqual(run.returncode, 2)
        self.assertTrue('usage: extract-pdftext.py' in run.stderr)

    def test_direct_execution(self):
        run = subprocess.run(['./jfscripts/extract_pdftext.py'],
                             encoding='utf-8',
                             stderr=subprocess.PIPE)
        self.assertEqual(run.returncode, 2)
        self.assertTrue('usage: extract_pdftext.py' in run.stderr)

    def test_help(self):
        run = subprocess.run(['extract-pdftext.py', '-h'], encoding='utf-8',
                             stdout=subprocess.PIPE)
        self.assertEqual(run.returncode, 0)
        self.assertTrue('usage: extract-pdftext.py' in run.stdout)


if __name__ == '__main__':
    unittest.main()
