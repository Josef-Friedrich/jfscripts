from _helper import TestCase, download, check_internet_connectifity
import unittest
from jfscripts import extract_pdftext
from jfscripts._utils import check_bin
import subprocess
import os
import tempfile

dependencies = check_bin(*extract_pdftext.dependencies, raise_error=False)
internet = check_internet_connectifity()

if dependencies and internet:
    tmp_pdf = os.path.join(tempfile.mkdtemp(), 'test.pdf')
    download('pdf/ocr.pdf', tmp_pdf)


class TestIntegration(TestCase):

    def test_command_line_interface(self):
        self.assertIsExecutable('extract_pdftext')

    def test_extraction(self):
        subprocess.run(['extract-pdftext.py', tmp_pdf])


if __name__ == '__main__':
    unittest.main()
