from _helper import Capturing
from _helper import TestCase
from jfscripts import _utils
from jfscripts._utils import FilePath
from unittest import mock
import os
import unittest
import tempfile


class TestClassRun(TestCase):

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

    def test_argument_colorize_path(self):
        run = _utils.Run(verbose=True, colorize=True)
        tmp = tempfile.mkstemp()[1]
        with Capturing() as output:
            run.run(['ls', tmp], stdout=run.PIPE)
        self.assertIn('\x1b[46m\x1b[37m', output[0])
        self.assertIn('\x1b[0m', output[0])

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


class TestCheckBin(TestCase):

    def test_check_dependencies(self):
        with mock.patch('shutil.which') as mock_which:
            mock_which.return_value = '/bin/lol'
            _utils.check_dependencies('lol')

    def test_check_dependencies_nonexistent(self):
        with mock.patch('shutil.which') as mock_which:
            mock_which.return_value = None
            with self.assertRaises(SystemError) as error:
                _utils.check_dependencies('lol')

            self.assertEqual(str(error.exception),
                             'Some commands are not installed: lol')

    def test_check_dependencies_nonexistent_multiple(self):
        with mock.patch('shutil.which') as mock_which:
            mock_which.return_value = None
            with self.assertRaises(SystemError) as error:
                _utils.check_dependencies('lol', 'troll')

            self.assertEqual(str(error.exception),
                             'Some commands are not installed: lol, troll')

    def test_check_dependencies_nonexistent_multiple_with_description(self):
        with mock.patch('shutil.which') as mock_which:
            mock_which.return_value = None
            with self.assertRaises(SystemError) as error:
                _utils.check_dependencies(
                    ('lol', 'apt install lol'),
                    'troll',
                )

            self.assertEqual(str(error.exception),
                             'Some commands are not installed: lol (apt '
                             'install lol), troll')


class TestClassFilePath(TestCase):

    def test_attribute_filename(self):
        file_path = FilePath('test.jpg')
        self.assertEqual(file_path.filename, 'test.jpg')

    def test_attribute_extension(self):
        file_path = FilePath('test.jpg')
        self.assertEqual(file_path.extension, 'jpg')

    def test_attribute_basename(self):
        file_path = FilePath('test.jpg')
        self.assertEqual(file_path.basename, 'test')
        file_path = FilePath('test.jpeg')
        self.assertEqual(file_path.basename, 'test')

    def test_attribute_base(self):
        file_path = FilePath('test.jpg', absolute=True)
        self.assertTrue(file_path.base.endswith('/test'))

    def test_class_argument(self):
        file_path = FilePath('test.jpg', absolute=True)
        self.assertEqual(str(file_path), os.path.abspath('test.jpg'))

    def test_class_magic_method(self):
        file_path = FilePath('test.jpg')
        self.assertEqual(str(file_path), 'test.jpg')

    def test_method_new(self):
        path = FilePath('test.jpg')
        self.assertEqual(str(path.new()), 'test.jpg')
        self.assertEqual(str(path.new(extension='png')), 'test.png')
        self.assertEqual(str(path.new(append='123')), 'test123.jpg')
        self.assertEqual(str(path.new(del_substring='est')), 't.jpg')

    def test_class_magic_method_eq_not_equal(self):
        a = FilePath('test1.jpg')
        b = FilePath('test2.jpg')
        self.assertFalse(a == b)

    def test_class_magic_method_eq_equal(self):
        a = FilePath('test.jpg')
        b = FilePath('test.jpg')
        self.assertTrue(a == b)


class TestCapturing(TestCase):

    def test_output_list(self):
        with _utils.Capturing() as output:
            print('test')
        self.assertEqual(output, ['test'])

    def test_method_tostring(self):
        with _utils.Capturing() as output:
            print('test1')
            print('test2')
        self.assertEqual(output.tostring(), 'test1\ntest2')


if __name__ == '__main__':
    unittest.main()
