from _helper import Capturing
from jfscripts import _utils
from unittest import mock
import unittest


class TestClassRun(unittest.TestCase):

    def test_argument_verbose(self):
        run = _utils.Run(verbose=True)
        self.assertEqual(run.verbose, True)
        with Capturing() as output:
            run.run(['ls', '-l'], stdout=run.PIPE)
        self.assertEqual(output, ['ls -l'])

    def test_argument_colorize(self):
        run = _utils.Run(verbose=True, colorize=True)
        self.assertEqual(run.colorize, True)
        with Capturing() as output:
            run.run(['ls', '-l'], stdout=run.PIPE)
        self.assertEqual(output[0], 'ls \x1b[34m-l\x1b[0m')

    def test_method_check_output(self):
        run = _utils.Run()
        out = run.check_output(['ls', '-l'])
        self.assertIn('jfscripts', out.decode('utf-8'))

    def test_method_run(self):
        run = _utils.Run()
        ls = run.run(['ls', '-l'], stdout=run.PIPE)
        self.assertEqual(ls.args, ['ls', '-l'])
        self.assertEqual(ls.returncode, 0)
        self.assertIn('jfscripts', ls.stdout.decode('utf-8'))


class TestCheckBin(unittest.TestCase):

    def test_check_bin(self):
        with mock.patch('shutil.which') as mock_which:
            mock_which.return_value = '/bin/lol'
            _utils.check_bin('lol')

    def test_check_bin_nonexistent(self):
        with mock.patch('shutil.which') as mock_which:
            mock_which.return_value = None
            with self.assertRaises(SystemError) as error:
                _utils.check_bin('lol')

            self.assertEqual(str(error.exception),
                             'Some commands are not installed: lol')

    def test_check_bin_nonexistent_multiple(self):
        with mock.patch('shutil.which') as mock_which:
            mock_which.return_value = None
            with self.assertRaises(SystemError) as error:
                _utils.check_bin('lol', 'troll')

            self.assertEqual(str(error.exception),
                             'Some commands are not installed: lol, troll')

    def test_check_bin_nonexistent_multiple_with_description(self):
        with mock.patch('shutil.which') as mock_which:
            mock_which.return_value = None
            with self.assertRaises(SystemError) as error:
                _utils.check_bin(
                    ('lol', 'apt install lol'),
                    'troll',
                )

            self.assertEqual(str(error.exception),
                             'Some commands are not installed: lol (apt '
                             'install lol), troll')


if __name__ == '__main__':
    unittest.main()
