import os
import subprocess

import pytest

from jfscripts import extract_pdftext
from jfscripts.utils import FilePath, check_dependencies
from tests._helper import check_internet_connectifity, download, is_executable

dependencies = check_dependencies(*extract_pdftext.dependencies, raise_error=False)
internet = check_internet_connectifity()

if dependencies and internet:
    tmp_pdf = download(
        "pdf/ocr.pdf", local_path="/tmp/jfscripts/extract_pdftext/test.pdf"
    )


class TestIntegration:
    def test_command_line_interface(self) -> None:
        assert is_executable("extract_pdftext")

    @pytest.mark.skipif(
        not dependencies or not internet, reason="Some dependencies are not installed"
    )
    def test_extraction(self) -> None:
        pdf = FilePath(tmp_pdf)
        subprocess.check_output(["extract-pdftext.py", str(pdf)])
        txt = pdf.new(extension="txt")
        assert os.path.exists(str(txt))
        assert "## Seite" in open(str(txt)).read()
        assert "Andrew Lloyd Webber" in open(str(txt)).read()
        assert "-" * extract_pdftext.line_length in open(str(txt)).read()

    def test_option_version(self) -> None:
        output = subprocess.check_output(["extract-pdftext.py", "--version"])
        assert output
        assert "extract-pdftext.py" in str(output)
