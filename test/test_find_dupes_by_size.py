from _helper import TestCase
import unittest


class TestIntetration(TestCase):

    def test_command_line_interface(self):
        self.assertIsExecutable('find_dupes_by_size')


if __name__ == '__main__':
    unittest.main()
