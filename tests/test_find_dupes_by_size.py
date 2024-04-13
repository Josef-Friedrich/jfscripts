import subprocess

from tests._helper import is_executable


class TestIntetration:
    def test_command_line_interface(self) -> None:
        assert is_executable("find_dupes_by_size")

    def test_option_version(self) -> None:
        output = subprocess.check_output(["find-dupes-by-size.py", "--version"])
        assert output
        assert "find-dupes-by-size.py" in str(output)
