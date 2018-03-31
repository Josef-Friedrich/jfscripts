import unittest
from _helper import TestCase, check_bin
from jfscripts import magick_imslp
from jfscripts.magick_imslp import FilePath, State
import os
from unittest import mock
from unittest.mock import patch, Mock
import subprocess
from urllib.request import urlretrieve
import tempfile


dependencies = check_bin(*magick_imslp.dependencies)


def get_state(complete=False):
    args = Mock()
    args.threshold = '50%'
    state = State(args)
    if complete:
        state.pdf_env('test.pdf')
    return state


class TestUnit(TestCase):

    @mock.patch('jfscripts.magick_imslp.subprocess.check_output')
    def test_get_pdf_info(self, mock):

        return_values = [
            b'Creator:        c42pdf v. 0.12 args:  -p 658.80x866.52\n',
            b'Producer:       PDFlib V0.6 (C) Thomas Merz 1997-98\n',
            b'CreationDate:   Sat Jan  2 21:11:06 2010 CET\n',
            b'Tagged:         no\n',
            b'UserProperties: no\nSuspects:       no\n',
            b'Form:           none\n',
            b'JavaScript:     no\n',
            b'Pages:          3\n',
            b'Encrypted:      no\n',
            b'Page size:      658.8 x 866.52 pts\n',
            b'Page rot:       0\n',
            b'File size:      343027 bytes\n',
            b'Optimized:      no\n',
            b'PDF version:    1.1\n',
        ]

        mock.return_value = b''.join(return_values)

        result = magick_imslp.pdf_page_count('test.pdf')
        self.assertEqual(result, 3)

    @patch('jfscripts.magick_imslp.subprocess.run')
    def test_threshold(self, run):
        state = get_state(complete=True)
        magick_imslp.threshold(FilePath('test.jpg'), 99, state)
        run.assert_called_with(
            ['convert', '-threshold', '99%', 'test.jpg',
             'test_threshold-99.png']
        )

    def test_pdf_to_images(self):
        state = get_state(complete=True)
        with mock.patch('subprocess.run') as mock_run:
            magick_imslp.pdf_to_images(FilePath('test.pdf'), state)
            args = mock_run.call_args[0][0]
            self.assertEqual(args[0], 'pdfimages')
            self.assertEqual(args[1], '-tiff')
            self.assertEqual(args[2], 'test.pdf')
            self.assertIn('test.pdf', args[2])
            self.assertEqual(args[3], 'test.pdf_magick')

    @unittest.skip('skipped')
    def test_collect_images(self):
        state = get_state(complete=True)

        with mock.patch('os.listdir') as os_listdir:
            files = ['2.tif', '1.tif']
            return_files = []
            for input_file in files:
                return_files.append(os.path.join(magick_imslp.tmp_dir,
                                    input_file))
            return_files.sort()
            os_listdir.return_value = files
            out = magick_imslp.collect_images(state)
            self.assertEqual(out, return_files)

    @patch('jfscripts.magick_imslp.subprocess.run')
    def test_do_magick(self, subprocess_run):
        state = get_state()
        magick_imslp.do_magick([FilePath('test.tif'), state])
        subprocess_run.assert_called_with(
            ['convert', '-resize', '200%', '-deskew', '40%', '-threshold',
             '50%', '-trim', '+repage', '-compress', 'Group4', '-monochrome',
             'test.tif',
             'test.pdf']
        )

        state.args.pdf = False
        state.args.resize = False
        magick_imslp.do_magick([FilePath('test.tif'), state])
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

    def test_method_ext(self):
        file_path = FilePath('test.jpg')
        self.assertEqual(str(file_path.ext('png')), 'test.png')

    def test_method_append(self):
        file_path = FilePath('test.jpg')
        self.assertEqual(str(file_path.append('_lol')), 'test_lol.jpg')


class TestClassState(TestCase):

    def test_class_without_tmp_dir(self):
        state = get_state()
        self.assertTrue(state.args)


class TestIntegration(TestCase):

    def test_command_line_interface(self):
        self.assertIsExecutable('magick_imslp')

    @unittest.skipIf(not dependencies, 'Some Dependencies are not installed')
    def test_input_file_pdf_exception(self):
        run = subprocess.run(['magick-imslp.py', 'test1.pdf', 'test2.pdf'],
                             encoding='utf-8',
                             stderr=subprocess.PIPE)
        self.assertEqual(run.returncode, 1)
        self.assertIn('Specify only one PDF file.', run.stderr)

    @unittest.skipIf(not dependencies, 'Some Dependencies are not installed')
    def test_with_real_pdf(self):
        tmp_dir = tempfile.mkdtemp()
        local_pdf = os.path.join(tmp_dir, 'scans.pdf')
        urlretrieve('https://github.com/Josef-Friedrich/test-files/raw/'
                    'master/pdf/scans.pdf', local_pdf)
        self.assertTrue(os.path.exists(local_pdf))
        subprocess.run(['magick-imslp.py', local_pdf])
        self.assertTrue(os.path.exists(local_pdf + '_magick-000.tif'))
        self.assertTrue(os.path.exists(local_pdf + '_magick-000.png'))
        self.assertTrue(os.path.exists(local_pdf + '_magick-001.tif'))
        self.assertTrue(os.path.exists(local_pdf + '_magick-001.png'))
        self.assertTrue(os.path.exists(local_pdf + '_magick-002.tif'))
        self.assertTrue(os.path.exists(local_pdf + '_magick-002.png'))

    @unittest.skipIf(not dependencies, 'Some Dependencies are not installed')
    def test_with_real_pdf_join(self):
        tmp_dir = tempfile.mkdtemp()
        local_pdf = os.path.join(tmp_dir, 'scans.pdf')
        urlretrieve('https://github.com/Josef-Friedrich/test-files/raw/'
                    'master/pdf/scans.pdf', local_pdf)
        self.assertTrue(os.path.exists(local_pdf))
        subprocess.run(['magick-imslp.py', '--pdf', '--join', local_pdf])
        self.assertTrue(os.path.exists(local_pdf + '_magick-000.tif'))
        self.assertTrue(os.path.exists(local_pdf + '_magick-000.pdf'))
        self.assertTrue(os.path.exists(local_pdf + '_magick-001.tif'))
        self.assertTrue(os.path.exists(local_pdf + '_magick-001.pdf'))
        self.assertTrue(os.path.exists(local_pdf + '_magick-002.tif'))
        self.assertTrue(os.path.exists(local_pdf + '_magick-002.pdf'))
        self.assertTrue(os.path.exists(local_pdf + '_joined.pdf'))

    @unittest.skipIf(not dependencies, 'Some Dependencies are not installed')
    def test_with_real_pdf_cleanup(self):
        tmp_dir = tempfile.mkdtemp()
        local_pdf = os.path.join(tmp_dir, 'scans.pdf')
        urlretrieve('https://github.com/Josef-Friedrich/test-files/raw/'
                    'master/pdf/scans.pdf', local_pdf)
        self.assertTrue(os.path.exists(local_pdf))
        subprocess.run(['magick-imslp.py', '--pdf', '--join', '--cleanup',
                        local_pdf])
        self.assertFalse(os.path.exists(local_pdf + '_magick-000.tif'))
        self.assertFalse(os.path.exists(local_pdf + '_magick-000.pdf'))
        self.assertFalse(os.path.exists(local_pdf + '_magick-001.tif'))
        self.assertFalse(os.path.exists(local_pdf + '_magick-001.pdf'))
        self.assertFalse(os.path.exists(local_pdf + '_magick-002.tif'))
        self.assertFalse(os.path.exists(local_pdf + '_magick-002.pdf'))
        self.assertTrue(os.path.exists(local_pdf + '_joined.pdf'))


if __name__ == '__main__':
    unittest.main()
