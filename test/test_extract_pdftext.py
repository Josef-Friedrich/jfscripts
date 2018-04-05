from _helper import TestCase
import unittest


class TestIntegration(TestCase):

    def test_command_line_interface(self):
        self.assertIsExecutable('extract_pdftext')


if __name__ == '__main__':
    unittest.main()
