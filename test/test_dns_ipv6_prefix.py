import subprocess
import unittest

from _helper import TestCase


class TestIntetration(TestCase):

    def test_command_line_interface(self):
        self.assertIsExecutable('dns_ipv6_prefix')

    def test_option_version(self):
        output = subprocess.check_output(['dns-ipv6-prefix.py', '--version'])
        self.assertTrue(output)
        self.assertIn('dns-ipv6-prefix.py', str(output))


if __name__ == '__main__':
    unittest.main()
