from _helper import TestCase
import unittest


class TestIntetration(TestCase):

    def test_command_line_interface(self):
        self.assertIsExecutable('dns_ipv6_prefix')


if __name__ == '__main__':
    unittest.main()
