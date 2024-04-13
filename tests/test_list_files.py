import subprocess
import unittest
from unittest import mock

from jfscripts.list_files import (
    _list_files_all,
    _list_files_filter,
    _split_glob,
    common_path,
    doc_examples,
    is_glob,
    list_files,
)


class TestFunctionCommonPrefix:
    def test_single_path(self):
        assert common_path(["/tmp/lol.txt"]) == "/tmp"

    def test_two_paths(self):
        assert common_path(["/tmp/a.txt", "/tmp/b.txt"]) == "/tmp"

    def test_no_match(self):
        assert common_path(["/usr/a.txt", "/tmp/b.txt"]) == "/"


class TestFunctionIsGlob:
    def test_asterisk_extension(self):
        assert is_glob("*.mscx")

    def test_asterisk(self):
        assert is_glob("l*l")

    def test_quotation_mark(self):
        assert is_glob("l?l")

    def test_seq(self):
        assert is_glob("l[ol]")

    def test_not_seq(self):
        assert is_glob("l[!ol]")

    def test_no_glob(self):
        assert not is_glob("lol")


class TestFunctionSplitGlob:
    def test_prefix_glob(self):
        assert _split_glob("lol/troll/*.mscx") == (
            "lol/troll",
            "*.mscx",
        )

    def test_glob_only(self):
        assert _split_glob("*.mscx") == (".", "*.mscx")

    def test_prefix_only(self):
        assert _split_glob("test/lol") == ("test/lol", "")

    def test_glob_middle_position(self):
        assert _split_glob("test/a/l*l/lol/*") == ("test/a", "l*l/lol/*")

    def test_glob_ahead_position(self):
        assert _split_glob("t*st/a/l*l/lol/*") == (".", "t*st/a/l*l/lol/*")


class TestFunctionListFilesAll:
    @mock.patch("os.walk")
    def test_only_files(self, os_walk):
        os_walk.return_value = (("a", (), ("a.txt", "b.txt")),)
        result = _list_files_all("a")
        os_walk.assert_called_with("a")
        assert result == ["a/a.txt", "a/b.txt"]

    @mock.patch("os.walk")
    def test_only_dirs(self, os_walk):
        os_walk.return_value = (("a", ("a", "b"), ()),)
        result = _list_files_all("a")
        os_walk.assert_called_with("a")
        assert result == ["a/a", "a/b"]

    @mock.patch("os.walk")
    def test_files_and_dirs(self, os_walk):
        os_walk.return_value = (("a", ("a", "b"), ("a.txt", "b.txt")),)
        result = _list_files_all("a")
        os_walk.assert_called_with("a")
        assert result == ["a/a", "a/a.txt", "a/b", "a/b.txt"]


class TestFunctionListFilesFilter:
    @mock.patch("os.walk")
    def test_simple(self, os_walk):
        os_walk.return_value = (("a", ("a", "b"), ("a.txt", "b.xml")),)
        result = _list_files_filter("a", "*.txt")
        os_walk.assert_called_with("a")
        assert result == ["a/a.txt"]

    @mock.patch("os.walk")
    def test_no_match(self, os_walk):
        os_walk.return_value = (("a", ("a", "b"), ("a.jpg", "b.xml")),)
        result = _list_files_filter("a", "*.txt")
        assert result == []

    @mock.patch("os.walk")
    def test_glob_middle_position(self, os_walk):
        os_walk.return_value = (
            ("a", ("a", "b"), ("a.jpg", "b.xml")),
            ("a/b", (), ("a.txt", "b.xml")),
        )
        result = _list_files_filter("a", "*/a.txt")
        assert result == ["a/b/a.txt"]

    @mock.patch("os.walk")
    def test_glob_character_seq(self, os_walk):
        os_walk.return_value = (("a", (), ("a.mscx", "b.mscz")),)
        result = _list_files_filter("a", "*.msc[xz]")
        assert result == ["a/a.mscx", "a/b.mscz"]


class TestFunctionListFiles:
    def test_multiple_files(self):
        files = ["a.txt", "b.txt"]
        assert list_files(files) == files

    def test_single_file(self):
        assert list_files(["/mnt/lol.txt"]) == ["/mnt/lol.txt"]

    @mock.patch("os.walk")
    def test_glob(self, os_walk):
        os_walk.return_value = (("/data", (), ("a.txt", "b.txt")),)
        result = list_files(["/data/*.txt"])
        os_walk.assert_called_with("/data")
        assert result == ["/data/a.txt", "/data/b.txt"]

    @mock.patch("os.walk")
    def test_glob_no_match(self, os_walk):
        os_walk.return_value = (("/data", (), ("a.txt", "b.txt")),)
        assert list_files(["/data/*.py"]) == []

    @mock.patch("os.path.isdir")
    @mock.patch("os.walk")
    def test_default_glob(self, os_walk, os_path_isdir):
        os_walk.return_value = (("/data", (), ("a.txt", "b.txt")),)
        os_path_isdir.return_value = True
        assert list_files(["/data"], default_glob="*.txt") == [
            "/data/a.txt",
            "/data/b.txt",
        ]


class TestFunctionArgparseExamples:
    def test_without_arguments(self):
        result = (
            "a.txt\n"
            "a.txt b.txt c.txt\n"
            "(asterisk).txt\n"
            '"(asterisk).txt"\n'
            "dir/\n"
            '"dir/(asterisk).txt"'
        )
        assert doc_examples() == result

    def test_without_indent_spaces(self):
        result = (
            "test.py a.txt\n"
            "test.py a.txt b.txt c.txt\n"
            "test.py (asterisk).txt\n"
            'test.py "(asterisk).txt"\n'
            "test.py dir/\n"
            'test.py "dir/(asterisk).txt"'
        )
        assert doc_examples("test.py", "txt") == result

    def test_with_indent_spaces(self):
        result = (
            "    test.py a.txt\n"
            "    test.py a.txt b.txt c.txt\n"
            "    test.py (asterisk).txt\n"
            '    test.py "(asterisk).txt"\n'
            "    test.py dir/\n"
            '    test.py "dir/(asterisk).txt"'
        )
        assert doc_examples("test.py", "txt", 4) == result

    def test_inline(self):
        result = (
            "“test.py a.txt”, "
            "“test.py a.txt b.txt c.txt”, "
            "“test.py (asterisk).txt”, "
            '“test.py "(asterisk).txt"”, '
            "“test.py dir/”, "
            '“test.py "dir/(asterisk).txt"”'
        )
        assert doc_examples("test.py", "txt", inline=True) == result


class TestIntegration:
    def test_command_line_interface(self):
        self.assertIsExecutable("list_files")

    def test_option_version(self):
        output = subprocess.check_output(["list-files.py", "--version"])
        assert output
        assert "list-files.py" in str(output)


if __name__ == "__main__":
    unittest.main()
