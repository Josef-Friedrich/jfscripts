import os
import subprocess
import unittest

from _helper import TestCase, check_internet_connectifity, download

from jfscripts import extract_pdftext
from jfscripts.utils import FilePath, check_dependencies

dependencies = check_dependencies(*extract_pdftext.dependencies, raise_error=False)
internet = check_internet_connectifity()

if dependencies and internet:
    tmp_pdf = download(
        "pdf/ocr.pdf", local_path="/tmp/jfscripts/extract_pdftext/test.pdf"
    )


class TestIntegration(TestCase):
    def test_command_line_interface(self):
        self.assertIsExecutable("extract_pdftext")

    @unittest.skipIf(
        not dependencies or not internet, "Some dependencies are not installed"
    )
    def test_extraction(self):
        pdf = FilePath(tmp_pdf)
        subprocess.check_output(["extract-pdftext.py", str(pdf)])
        txt = pdf.new(extension="txt")
        self.assertTrue(os.path.exists(str(txt)))
        self.assertTrue("## Seite" in open(str(txt)).read())
        self.assertTrue("Andrew Lloyd Webber" in open(str(txt)).read())
        self.assertTrue("-" * extract_pdftext.line_length in open(str(txt)).read())

    def test_option_version(self):
        output = subprocess.check_output(["extract-pdftext.py", "--version"])
        self.assertTrue(output)
        self.assertIn("extract-pdftext.py", str(output))


if __name__ == "__main__":
    unittest.main()
