import subprocess

from tests._helper import is_executable


class TestIntegration:
    def test_command_line_interface(self) -> None:
        assert is_executable("mac_to_eui64")

    def test_option_version(self) -> None:
        output = subprocess.check_output(["mac-to-eui64.py", "--version"])
        assert output
        assert "mac-to-eui64.py" in str(output)
