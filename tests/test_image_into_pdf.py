import os
import shutil
import subprocess
import tempfile
import unittest
from os.path import exists
from unittest import mock

import pytest
from stdout_stderr_capturing import Capturing

from jfscripts import image_into_pdf as replace
from jfscripts.utils import FilePath, check_dependencies
from tests._helper import check_internet_connectifity, download, is_executable


def copy(path: str):
    basename = os.path.basename(path)
    tmp = os.path.join(tempfile.mkdtemp(), basename)
    return shutil.copy(path, tmp)


dependencies = check_dependencies(*replace.dependencies, raise_error=False)
internet = check_internet_connectifity()

if dependencies and internet:
    tmp_pdf = download("pdf/scans.pdf", local_path="/tmp/jfs-image_into_pdf/test.pdf")
    tmp_png = download(
        "png/bach-busoni_300.png",
        local_path="/tmp/jfscripts/pdf_compress/bach-busoni_300.png",
    )


class TestUnits:
    @pytest.mark.skip(reason="skip")
    @mock.patch("jfscripts.image_into_pdf.run.check_output")
    def do_magick_identify_dimensions(self, check_output: mock.Mock) -> None:
        check_output.return_value = "lol"
        result = replace.get_pdf_info("test.pdf")
        assert result == {"width": "658.8", "height": "866.52", "page_count": 3}

    @mock.patch("jfscripts.image_into_pdf.run.check_output")
    def test_get_pdf_info(self, mock: mock.Mock) -> None:
        return_values = [
            b"Creator:        c42pdf v. 0.12 args:  -p 658.80x866.52\n",
            b"Producer:       PDFlib V0.6 (C) Thomas Merz 1997-98\n",
            b"CreationDate:   Sat Jan  2 21:11:06 2010 CET\n",
            b"Tagged:         no\n",
            b"UserProperties: no\nSuspects:       no\n",
            b"Form:           none\n",
            b"JavaScript:     no\n",
            b"Pages:          3\n",
            b"Encrypted:      no\n",
            b"Page size:      658.8 x 866.52 pts\n",
            b"Page rot:       0\n",
            b"File size:      343027 bytes\n",
            b"Optimized:      no\n",
            b"PDF version:    1.1\n",
        ]

        mock.return_value = b"".join(return_values)

        result = replace.get_pdf_info("test.pdf")
        assert result == {"width": "658.8", "height": "866.52", "page_count": 3}

    @pytest.mark.skip(reason="skip")
    @mock.patch("jfscripts.image_into_pdf.run.run")
    def test_convert_image_to_pdf_page(self, mock: mock.Mock) -> None:
        result = replace.convert_image_to_pdf_page("test.png", "111.1", "222.2")
        assert "tmp.pdf" in result
        args = mock.call_args[0][0]
        assert args[0] == "convert"
        assert args[1] == "test.png"
        assert args[2] == "-page"
        assert args[3] == "111.1x222.2"
        assert "tmp.pdf" in args[4]

    @mock.patch("jfscripts.image_into_pdf.check_dependencies")
    def test_main(self, check_executable: mock.Mock) -> None:
        with Capturing(stream="stderr"):
            with unittest.mock.patch("sys.argv", ["cmd"]):
                with pytest.raises(SystemExit):
                    replace.main()


class TestUnitAssemblePdf:
    def assert_assemble(self, kwargs, called_with) -> None:
        with mock.patch("jfscripts.image_into_pdf.run.run") as run:
            # m = main
            # i = insert
            replace.assemble_pdf(FilePath("m.pdf"), FilePath("i.pdf"), **kwargs)
            run.assert_called_with(["pdftk"] + called_with + ["output", "m_joined.pdf"])

    def test_replace_first_page(self) -> None:
        self.assert_assemble(
            {"page_count": 5, "page_number": 1, "mode": "replace"},
            ["A=m.pdf", "B=i.pdf", "cat", "B1", "A2-end"],
        )

    def test_replace_second_page(self) -> None:
        self.assert_assemble(
            {"page_count": 5, "page_number": 2, "mode": "replace"},
            ["A=m.pdf", "B=i.pdf", "cat", "A1", "B1", "A3-end"],
        )

    def test_replace_last_page(self) -> None:
        self.assert_assemble(
            {"page_count": 5, "page_number": 5, "mode": "replace"},
            ["A=m.pdf", "B=i.pdf", "cat", "A1-4", "B1"],
        )

    def test_add_before_first_page(self) -> None:
        self.assert_assemble(
            {"page_count": 5, "page_number": 1, "mode": "add", "position": "before"},
            ["i.pdf", "m.pdf", "cat"],
        )

    def test_add_before_second_page(self) -> None:
        self.assert_assemble(
            {"page_count": 5, "page_number": 2, "mode": "add", "position": "before"},
            ["A=m.pdf", "B=i.pdf", "cat", "A1", "B1", "A2-end"],
        )

    def test_add_after_second_page(self) -> None:
        self.assert_assemble(
            {"page_count": 5, "page_number": 2, "mode": "add", "position": "after"},
            ["A=m.pdf", "B=i.pdf", "cat", "A1-2", "B1", "A3-end"],
        )

    def test_add_before_last_page(self) -> None:
        self.assert_assemble(
            {"page_count": 5, "page_number": 5, "mode": "add", "position": "before"},
            ["A=m.pdf", "B=i.pdf", "cat", "A1-4", "B1", "A5"],
        )

    def test_add_after_last_page(self) -> None:
        self.assert_assemble(
            {"page_count": 5, "page_number": 5, "mode": "add", "position": "after"},
            ["m.pdf", "i.pdf", "cat"],
        )


class TestIntegration:
    def test_command_line_interface(self) -> None:
        assert is_executable("image_into_pdf")

    def test_option_version(self) -> None:
        output = subprocess.check_output(["image-into-pdf.py", "--version"])
        assert output
        assert "image-into-pdf.py" in str(output)


@pytest.mark.skipif(
    not dependencies or not internet, reason="Some dependencies are not installed"
)
class TestIntegrationWithDependencies:
    def setup_method(self) -> None:
        self.tmp_pdf = copy(tmp_pdf)
        self.tmp_png = copy(tmp_png)

    def assert_exists_joined_pdf(self) -> None:
        assert exists(str(FilePath(self.tmp_pdf).new(append="_joined")))

    def test_replace(self) -> None:
        subprocess.run(
            ["image-into-pdf.py", "replace", self.tmp_pdf, "1", self.tmp_png]
        )
        self.assert_exists_joined_pdf()

    def test_add(self) -> None:
        subprocess.run(["image-into-pdf.py", "add", self.tmp_png, self.tmp_pdf])
        self.assert_exists_joined_pdf()

    def test_add_pdf(self) -> None:
        subprocess.run(["image-into-pdf.py", "add", self.tmp_pdf, self.tmp_pdf])
        self.assert_exists_joined_pdf()

    def test_add_after(self) -> None:
        subprocess.run(
            ["image-into-pdf.py", "add", "--after", "1", self.tmp_png, self.tmp_pdf]
        )
        self.assert_exists_joined_pdf()

    def test_add_before(self) -> None:
        subprocess.run(
            ["image-into-pdf.py", "add", "--before", "1", self.tmp_png, self.tmp_pdf]
        )
        self.assert_exists_joined_pdf()

    def test_add_first(self) -> None:
        subprocess.run(
            ["image-into-pdf.py", "add", "--first", self.tmp_png, self.tmp_pdf]
        )
        self.assert_exists_joined_pdf()

    def test_add_last(self) -> None:
        subprocess.run(
            ["image-into-pdf.py", "add", "--last", self.tmp_png, self.tmp_pdf]
        )
        self.assert_exists_joined_pdf()

    def test_add_alias_a(self) -> None:
        subprocess.run(["image-into-pdf.py", "a", "--last", self.tmp_png, self.tmp_pdf])
        self.assert_exists_joined_pdf()

    def test_add_alias_ad(self) -> None:
        subprocess.run(
            ["image-into-pdf.py", "ad", "--last", self.tmp_png, self.tmp_pdf]
        )
        self.assert_exists_joined_pdf()

    def test_add_last_exclusive_arguments(self) -> None:
        process = subprocess.run(
            [
                "image-into-pdf.py",
                "add",
                "--last",
                "--before",
                "2",
                self.tmp_png,
                self.tmp_pdf,
            ]
        )
        assert process.returncode == 2

    def test_convert(self) -> None:
        subprocess.run(["image-into-pdf.py", "convert", self.tmp_png, self.tmp_pdf])
        assert exists(str(FilePath(self.tmp_pdf).new(append="_insert")))
