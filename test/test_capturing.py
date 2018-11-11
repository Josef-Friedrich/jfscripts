from _helper import TestCase
from jfscripts.capturing import Capturing
import unittest


class TestCapturing(TestCase):

    def test_output_list(self):
        with Capturing() as output:
            print('test')
        self.assertEqual(output, ['test'])

    def test_method_tostring(self):
        with Capturing() as output:
            print('test1')
            print('test2')
        self.assertEqual(output.tostring(), 'test1\ntest2')


if __name__ == '__main__':
    unittest.main()
