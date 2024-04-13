import subprocess

import pytest

from tests._helper import is_executable


class TestIntegration:
    @pytest.mark.skip("Not working on GitHub Actions")
    def test_command_line_interface(self) -> None:
        assert is_executable("dns_ipv6_prefix")

    @pytest.mark.skip("Not working on GitHub Actions")
    def test_option_version(self) -> None:
        output = subprocess.check_output(["dns-ipv6-prefix.py", "--version"])
        assert output
        assert "dns-ipv6-prefix.py" in str(output)
