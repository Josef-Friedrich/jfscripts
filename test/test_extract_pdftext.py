from _helper import TestCase, download, check_internet_connectifity
import unittest
from jfscripts import extract_pdftext
from jfscripts._utils import check_bin
import subprocess

dependencies = check_bin(*extract_pdftext.dependencies, raise_error=False)
internet = check_internet_connectifity()

if dependencies and internet:
    tmp_pdf = download('pdf/ocr.pdf',
                       local_path='/tmp/jfscripts/extract_pdftext/test.pdf')


class TestIntegration(TestCase):

    def test_command_line_interface(self):
        self.assertIsExecutable('extract_pdftext')

    def test_extraction(self):
        subprocess.check_output(['extract-pdftext.py', tmp_pdf])


if __name__ == '__main__':
    unittest.main()
