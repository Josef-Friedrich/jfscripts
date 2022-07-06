import subprocess
import unittest

from _helper import TestCase


class TestIntetration(TestCase):

    def test_command_line_interface(self):
        self.assertIsExecutable('find_dupes_by_size')

    def test_option_version(self):
        output = subprocess.check_output(['find-dupes-by-size.py',
                                          '--version'])
        self.assertTrue(output)
        self.assertIn('find-dupes-by-size.py', str(output))


if __name__ == '__main__':
    unittest.main()
