import unittest
from jfscripts import _utils
from unittest import mock


class TestUnit(unittest.TestCase):

    def test_check_executables(self):
        with mock.patch('shutil.which') as mock_which:
            mock_which.return_value = '/bin/lol'
            _utils.check_executables('lol')

    def test_check_executables_nonexistent(self):
        with mock.patch('shutil.which') as mock_which:
            mock_which.return_value = None
            with self.assertRaises(SystemError) as error:
                _utils.check_executables('lol')

            self.assertEqual(str(error.exception),
                             'Some commands are not installed: lol')

    def test_check_executables_nonexistent_multiple(self):
        with mock.patch('shutil.which') as mock_which:
            mock_which.return_value = None
            with self.assertRaises(SystemError) as error:
                _utils.check_executables('lol', 'troll')

            self.assertEqual(str(error.exception),
                             'Some commands are not installed: lol, troll')

    def test_check_executables_nonexistent_multiple_with_description(self):
        with mock.patch('shutil.which') as mock_which:
            mock_which.return_value = None
            with self.assertRaises(SystemError) as error:
                _utils.check_executables(
                    ('lol', 'apt install lol'),
                    'troll',
                )

            self.assertEqual(str(error.exception),
                             'Some commands are not installed: lol (apt '
                             'install lol), troll')


if __name__ == '__main__':
    unittest.main()
