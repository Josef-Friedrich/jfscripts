import os
import tempfile
from unittest import mock

import pytest
from stdout_stderr_capturing import Capturing

from jfscripts import utils
from jfscripts.utils import FilePath


class TestClassRun:
    def test_argument_verbose(self) -> None:
        run = utils.Run(verbose=True)
        assert run.verbose
        with Capturing() as output:
            run.run(["ls", "-l"], stdout=run.PIPE)
        assert output == ["ls -l"]

    def test_argument_colorize(self) -> None:
        run = utils.Run(verbose=True, colorize=True)
        assert run.colorize
        with Capturing() as output:
            run.run(["ls", "-l"], stdout=run.PIPE)
        assert output[0] == "ls -l"

    def test_argument_colorize_path(self) -> None:
        run = utils.Run(verbose=True, colorize=True)
        tmp = tempfile.mkstemp()[1]
        with Capturing() as output:
            run.run(["ls", tmp], stdout=run.PIPE)
        assert "ls /" in output[0]

    def test_method_check_output(self) -> None:
        run = utils.Run()
        out = run.check_output(["ls", "-l"])
        assert "jfscripts" in out.decode("utf-8")

    def test_method_run(self) -> None:
        run = utils.Run()
        ls = run.run(["ls", "-l"], stdout=run.PIPE)
        assert ls.args == ["ls", "-l"]
        assert ls.returncode == 0
        assert "jfscripts" in ls.stdout


class TestCheckBin:
    def test_check_dependencies(self) -> None:
        with mock.patch("shutil.which") as mock_which:
            mock_which.return_value = "/bin/lol"
            utils.check_dependencies("lol")

    def test_check_dependencies_nonexistent(self) -> None:
        with mock.patch("shutil.which") as mock_which:
            mock_which.return_value = None
            with pytest.raises(SystemError) as error:
                utils.check_dependencies("lol")

            assert error.value.args[0] == "Some commands are not installed: lol"

    def test_check_dependencies_nonexistent_multiple(self) -> None:
        with mock.patch("shutil.which") as mock_which:
            mock_which.return_value = None
            with pytest.raises(SystemError) as error:
                utils.check_dependencies("lol", "troll")

            assert error.value.args[0] == "Some commands are not installed: lol, troll"

    def test_check_dependencies_nonexistent_multiple_with_description(self) -> None:
        with mock.patch("shutil.which") as mock_which:
            mock_which.return_value = None
            with pytest.raises(SystemError) as error:
                utils.check_dependencies(
                    ("lol", "apt install lol"),
                    "troll",
                )

            assert (
                error.value.args[0] == "Some commands are not installed: lol (apt "
                "install lol), troll"
            )


class TestClassFilePath:
    def test_attribute_filename(self) -> None:
        file_path = FilePath("test.jpg")
        assert file_path.filename == "test.jpg"

    def test_attribute_extension(self) -> None:
        file_path = FilePath("test.jpg")
        assert file_path.extension == "jpg"

    def test_attribute_basename(self) -> None:
        file_path = FilePath("test.jpg")
        assert file_path.basename == "test"
        file_path = FilePath("test.jpeg")
        assert file_path.basename == "test"

    def test_attribute_base(self) -> None:
        file_path = FilePath("test.jpg", absolute=True)
        assert file_path.base.endswith("/test")

    def test_class_argument(self) -> None:
        file_path = FilePath("test.jpg", absolute=True)
        assert str(file_path) == os.path.abspath("test.jpg")

    def test_class_magic_method(self) -> None:
        file_path = FilePath("test.jpg")
        assert str(file_path) == "test.jpg"

    def test_method_new(self) -> None:
        path = FilePath("test.jpg")
        assert str(path.new()) == "test.jpg"
        assert str(path.new(extension="png")) == "test.png"
        assert str(path.new(append="123")) == "test123.jpg"
        assert str(path.new(del_substring="est")) == "t.jpg"

    def test_class_magic_method_eq_not_equal(self) -> None:
        a = FilePath("test1.jpg")
        b = FilePath("test2.jpg")
        assert not a == b

    def test_class_magic_method_eq_equal(self) -> None:
        a = FilePath("test.jpg")
        b = FilePath("test.jpg")
        assert a == b
