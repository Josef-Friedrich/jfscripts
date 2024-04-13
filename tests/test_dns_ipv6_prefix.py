import subprocess

from tests._helper import is_executable


class TestIntegration:
    def test_command_line_interface(self) -> None:
        assert is_executable("dns_ipv6_prefix")

    def test_option_version(self) -> None:
        output = subprocess.check_output(["dns-ipv6-prefix.py", "--version"])
        assert output
        assert "dns-ipv6-prefix.py" in str(output)
