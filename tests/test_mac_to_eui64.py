import subprocess
import unittest

from _helper import TestCase


class TestIntegration(TestCase):
    def test_command_line_interface(self):
        self.assertIsExecutable("mac_to_eui64")

    def test_option_version(self):
        output = subprocess.check_output(["mac-to-eui64.py", "--version"])
        self.assertTrue(output)
        self.assertIn("mac-to-eui64.py", str(output))


if __name__ == "__main__":
    unittest.main()
