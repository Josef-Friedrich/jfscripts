import unittest
from _helper import TestCase
from jfscripts import magick_imslp
from jfscripts.magick_imslp import FilePath
import os
from unittest import mock
from unittest.mock import patch, Mock


class TestUnit(TestCase):

    def test_job_identifier(self):
        self.assertEqual(len(magick_imslp.job_identifier), 36)

    def test_tmp_dir(self):
        self.assertTrue(os.path.exists(magick_imslp.tmp_dir))

    def test_pdf_to_images(self):
        with mock.patch('subprocess.run') as mock_run:
            magick_imslp.pdf_to_images(FilePath('test.pdf'))
            args = mock_run.call_args[0][0]
            self.assertEqual(args[0], 'pdfimages')
            self.assertEqual(args[1], '-tiff')
            self.assertEqual(args[2], 'test.pdf')
            self.assertIn('test.pdf', args[2])
            self.assertEqual(len(args[3]), 36)

    def test_do_magick(self):
        with mock.patch('subprocess.run') as subprocess_run:
            args = Mock()
            magick_imslp.do_magick(FilePath('test.tif'), args)
            call_args = subprocess_run.call_args[0][0]
            self.assertEqual(call_args[0], 'convert')

    def test_multiple_input_files(self):
        with patch('sys.argv',  ['cmd', 'one.tif', 'two.tif']):
            with patch('jfscripts.magick_imslp.per_file') as per_file:
                magick_imslp.main()
                self.assertEqual(per_file.call_count, 2)


class TestClassFilePath(TestCase):

    def test_class_argument(self):
        file_path = FilePath('test.jpg', absolute=True)
        self.assertEqual(file_path.get(), os.path.abspath('test.jpg'))

    def test_method_extension(self):
        file_path = FilePath('test.jpg')
        self.assertEqual(file_path.extension('png'), 'test.png')

    def test_method_backup(self):
        file_path = FilePath('test.jpg')
        self.assertEqual(file_path.backup(), 'test_backup.jpg')


class TestIntegration(TestCase):

    def test_command_line_interface(self):
        self.assertIsExecutable('magick_imslp')


if __name__ == '__main__':
    unittest.main()
