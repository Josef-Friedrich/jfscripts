import unittest
from _helper import TestCase


class TestIntegration(TestCase):

    def test_command_line_interface(self):
        self.assertIsExecutable('mac_to_eui64')


if __name__ == '__main__':
    unittest.main()
