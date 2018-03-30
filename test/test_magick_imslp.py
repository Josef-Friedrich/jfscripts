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

    @unittest.skip('skipped')
    def test_collect_images(self):
        with mock.patch('os.listdir') as os_listdir:
            files = ['2.tif', '1.tif']
            return_files = []
            for input_file in files:
                return_files.append(os.path.join(magick_imslp.tmp_dir,
                                    input_file))
            return_files.sort()
            os_listdir.return_value = files
            out = magick_imslp.collect_images()
            self.assertEqual(out, return_files)

    @patch('jfscripts.magick_imslp.subprocess.run')
    def test_do_magick(self, subprocess_run):
        args = Mock()
        args.threshold = '50%'
        magick_imslp.do_magick(FilePath('test.tif'), args)
        subprocess_run.assert_called_with(
            ['convert', '-border', '100x100', '-bordercolor', '#FFFFFF',
             '-resize', '200%', '-deskew', '40%', '-threshold', '50%', '-trim',
             '+repage', '-compress', 'Group4', '-monochrome', 'test.tif',
             'test.pdf']
        )

        args.border = False
        magick_imslp.do_magick(FilePath('test.tif'), args)
        subprocess_run.assert_called_with(
            ['convert', '-resize', '200%', '-deskew', '40%', '-threshold',
             '50%', '-trim', '+repage', '-compress', 'Group4', '-monochrome',
             'test.tif', 'test.pdf']
        )

        args.compression = False
        args.resize = False
        magick_imslp.do_magick(FilePath('test.tif'), args)
        subprocess_run.assert_called_with(
            ['convert', '-deskew', '40%', '-threshold', '50%', '-trim',
             '+repage', 'test.tif', 'test.png']
        )

    @unittest.skip('works not with multiprocessing')
    @patch('jfscripts.magick_imslp.per_file')
    @patch('jfscripts.magick_imslp.check_bin')
    def test_multiple_input_files(self, check_bin, per_file):
        with patch('sys.argv',  ['cmd', 'one.tif', 'two.tif']):
            magick_imslp.main()
            self.assertEqual(per_file.call_count, 2)


class TestClassFilePath(TestCase):

    def test_class_argument(self):
        file_path = FilePath('test.jpg', absolute=True)
        self.assertEqual(str(file_path), os.path.abspath('test.jpg'))

    def test_class_magic_method(self):
        file_path = FilePath('test.jpg')
        self.assertEqual(str(file_path), 'test.jpg')

    def test_method_extension(self):
        file_path = FilePath('test.jpg')
        self.assertEqual(str(file_path.change_extension('png')), 'test.png')

    def test_method_backup(self):
        file_path = FilePath('test.jpg')
        self.assertEqual(str(file_path.get_backup_path()), 'test_backup.jpg')


class TestIntegration(TestCase):

    def test_command_line_interface(self):
        self.assertIsExecutable('magick_imslp')


if __name__ == '__main__':
    unittest.main()
