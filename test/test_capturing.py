from _helper import TestCase
from jfscripts.capturing import Capturing
import unittest


class TestCapturing(TestCase):

    def test_output_list(self):
        with Capturing() as output:
            print('test')
        self.assertEqual(output, ['test'])


if __name__ == '__main__':
    unittest.main()
