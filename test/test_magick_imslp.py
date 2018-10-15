from _helper import TestCase, download, check_internet_connectifity
from jfscripts import magick_imslp
from jfscripts._utils import check_bin
from jfscripts.magick_imslp import FilePath, State, Timer
from pathlib import Path
from subprocess import check_output, run
from unittest import mock
from unittest.mock import patch, Mock
import argparse
import os
import shutil
import subprocess
import tempfile
import unittest


def get_state():
    args = Mock()
    args.threshold = '50%'
    args.input_files = ['/tmp/1.txt', '/tmp/2.txt']
    state = State(args)
    return state


def copy(path):
    basename = os.path.basename(path)
    tmp = os.path.join(tempfile.mkdtemp(), basename)
    return shutil.copy(path, tmp)


dependencies = check_bin(*magick_imslp.dependencies, raise_error=False)
internet = check_internet_connectifity()

if dependencies and internet:
    tmp_pdf = download('pdf/scans.pdf',
                       local_path='/tmp/jfs-magick_imslp/test.pdf')
    tmp_png1 = download(
        'png/bach-busoni_300.png',
        local_path='/tmp/jfscripts/magick_imslp/bach-busoni_300.png'
    )
    tmp_png2 = download(
        'png/liszt-weinen_300.png',
        local_path='/tmp/jfscripts/magick_imslp/liszt-weinen_300.png'
    )


class TestUnit(TestCase):

    @mock.patch('jfscripts.magick_imslp.run.check_output')
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

    @mock.patch('jfscripts.magick_imslp.run.check_output')
    def test_get_image_info(self, check_output):
        check_output.side_effect = [
            bytes('2552'.encode('utf-8')),
            bytes('3656'.encode('utf-8')),
            bytes('256'.encode('utf-8')),
        ]
        result = magick_imslp.get_image_info(FilePath('test.pdf'))
        self.assertEqual(result, {'width': 2552, 'height': 3656,
                                  'channels': 256})

    def test_enlighten_border(self):
        result = magick_imslp.enlighten_border(1000, 1000)
        self.assertEqual(result, [
            '-region', '950x50', '-level', '0%,30%',
            '-region', '50x950+950', '-level', '0%,30%',
            '-region', '950x50+50+950', '-level', '0%,30%',
            '-region', '50x950+0+50', '-level', '0%,30%'])

    @patch('jfscripts.magick_imslp.convert_executable')
    @patch('jfscripts.magick_imslp.run.run')
    def test_threshold(self, run, convert_executable):
        convert_executable.return_value = ['convert']
        state = get_state()
        magick_imslp.threshold(FilePath('test.jpg'), 99, state)
        run.assert_called_with(
            ['convert', '-threshold', '99%', 'test.jpg',
             'test_threshold-99.png']
        )

    @patch('jfscripts.magick_imslp.threshold')
    def test_threshold_series(self, threshold):
        state = get_state()
        magick_imslp.threshold_series(FilePath('test.jpg'), state)
        self.assertEqual(threshold.call_count, 12)

    def test_check_threshold(self):
        check = magick_imslp.check_threshold
        self.assertEqual(check(1), '1%')
        self.assertEqual(check('2'), '2%')
        self.assertEqual(check('3%'), '3%')

        with self.assertRaises(ValueError):
            check(4.5)
        with self.assertRaises(ValueError):
            check('lol')
        with self.assertRaises(argparse.ArgumentTypeError):
            check(-1)
        with self.assertRaises(argparse.ArgumentTypeError):
            check(101)

    def test_pdf_to_images(self):
        state = get_state()
        with mock.patch('subprocess.run') as mock_run:
            magick_imslp.pdf_to_images(FilePath('test.pdf'), state)
            args = mock_run.call_args[0][0]
            self.assertEqual(args[0], 'pdfimages')
            self.assertEqual(args[1], '-tiff')
            self.assertEqual(args[2], 'test.pdf')
            self.assertIn('test.pdf', args[2])
            # test_magick_901ca3ae-c5ad-11e8-9796-5c514fcf0a5d
            self.assertEqual(len(args[3]), 48)
            self.assertTrue(args[3].startswith('test_'))

    @unittest.skip('skipped')
    def test_collect_images(self):
        state = get_state()

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

    @patch('jfscripts.magick_imslp.convert_executable')
    @patch('jfscripts.magick_imslp.run.run')
    def test_do_magick_false_enlighten_border(self, run, convert_executable):
        convert_executable.return_value = ['convert']
        state = get_state()
        state.args.enlighten_border = False
        magick_imslp.do_magick([FilePath('test.tif'), state])
        run.assert_called_with(
            ['convert', '-resize', '200%', '-deskew', '40%', '-threshold',
             '50%', '-trim', '+repage', '-border', '5%', '-bordercolor',
             '#FFFFFF', '-compress', 'Group4', '-monochrome', 'test.tif',
             'test.pdf']
        )

    @patch('jfscripts.magick_imslp.convert_executable')
    @patch('jfscripts.magick_imslp.run.run')
    def test_do_magick_more_false(self, run, convert_executable):
        convert_executable.return_value = ['convert']
        state = get_state()
        state.args.enlighten_border = False
        state.args.pdf = False
        state.args.resize = False
        state.args.border = False
        magick_imslp.do_magick([FilePath('test.tif'), state])
        run.assert_called_with(
            ['convert', '-deskew', '40%', '-threshold', '50%', '-trim',
             '+repage', 'test.tif', 'test.png']
        )

    @patch('jfscripts.magick_imslp.do_multiprocessing_magick')
    @patch('jfscripts.magick_imslp.check_bin')
    def test_multiple_input_files(self, cb, mp):
        with patch('sys.argv',  ['cmd', 'one.tif', 'two.tif']):
            magick_imslp.main()
            args = mp.call_args[0][0]
            self.assertIn('one.tif', str(args[0]))
            self.assertIn('two.tif', str(args[1]))


class TestClassTimer(TestCase):

    def test_start(self):
        timer = Timer()
        self.assertTrue(timer.begin > 0)

    def test_stop(self):
        timer = Timer()
        result = timer.stop()
        self.assertIn('s', result)


class TestClassState(TestCase):

    def setUp(self):
        self.state = get_state()

    def test_args(self):
        self.assertTrue(self.state.args)

    def test_uuid(self):
        self.assertTrue(self.state.uuid)
        self.assertEqual(len(self.state.uuid), 36)


class TestIntegration(TestCase):

    def test_command_line_interface(self):
        self.assertIsExecutable('magick_imslp')

    def test_option_version(self):
        output = subprocess.check_output(['magick-imslp.py', '--version'])
        self.assertTrue(output)
        self.assertIn('magick-imslp.py', str(output))


@unittest.skipIf(not dependencies or not internet,
                 'Some dependencies are not installed')
class TestIntegrationWithDependencies(TestCase):

    def test_input_file_pdf_exception(self):
        out = run(['magick-imslp.py', 'test1.pdf', 'test2.pdf'],
                  encoding='utf-8', stderr=subprocess.PIPE)
        self.assertEqual(out.returncode, 1)
        self.assertIn('Specify only one PDF file.', out.stderr)

    def test_with_real_pdf(self):
        tmp = copy(tmp_pdf)
        self.assertExists(tmp)
        path = FilePath(tmp)
        check_output(['magick-imslp.py', tmp])
        result = ('0.png', '1.png', '2.png')
        for test_file in result:
            self.assertExists(path.base + '-00' + test_file, test_file)

    def test_option_no_multiprocessing(self):
        pdf = copy(tmp_pdf)
        self.assertExists(pdf)
        path = FilePath(pdf)
        check_output(['magick-imslp.py', '--no-multiprocessing', pdf])
        result = ('0.png', '1.png', '2.png')
        for test_file in result:
            self.assertExists(path.base + '-00' + test_file, test_file)

    def test_with_real_pdf_join(self):
        tmp = copy(tmp_pdf)
        self.assertExists(tmp)
        check_output(['magick-imslp.py', '--pdf', '--join', tmp])
        self.assertExists(os.path.join(str(Path(tmp).parent), 'joined.pdf'))

    def test_option_join_without_pdf(self):
        pdf = copy(tmp_pdf)
        self.assertExists(pdf)
        check_output(['magick-imslp.py', '--join', pdf])
        self.assertExists(os.path.join(str(Path(pdf).parent),
                                       'joined.pdf'))

    def test_option_join_pdf_source_png(self):
        self.assertExists(tmp_png1)
        self.assertExists(tmp_png2)
        check_output(['magick-imslp.py', '--pdf', '--join', tmp_png1,
                      tmp_png2])
        self.assertExists(os.path.join(str(Path(tmp_png1).parent),
                                       'joined.pdf'))

    def test_real_threshold_series(self):
        tmp = copy(tmp_png1)
        check_output(['magick-imslp.py', '--threshold-series', tmp])
        result = (40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95)
        for threshold in result:
            suffix = '_threshold-{}.png'.format(threshold)
            path = tmp.replace('.png', suffix)
            self.assertExists(path, path)

    def test_real_invalid_threshold(self):
        out = run(['magick-imslp.py', '--threshold', '1000', 'test.pdf'],
                  encoding='utf-8', stderr=subprocess.PIPE)
        self.assertEqual(out.returncode, 2)
        self.assertIn('1000 is an invalid int value. Should be 0-100',
                      out.stderr)

    def test_real_backup_no_backup(self):
        tmp = copy(tmp_png1)
        check_output(['magick-imslp.py', tmp])
        backup = FilePath(tmp).new(append='_backup')
        self.assertExistsNot(str(backup))

    def test_real_backup_do_backup(self):
        tmp = copy(tmp_png1)
        check_output(['magick-imslp.py', '--backup', tmp])
        backup = FilePath(tmp).new(append='_backup')
        self.assertExists(str(backup))

    def test_already_converted(self):
        tmp = copy(tmp_png1)
        check_output(['magick-imslp.py', tmp])
        out = check_output(['magick-imslp.py', tmp])
        self.assertIn('The target file seems to be already converted.',
                      out.decode('utf-8'))

    def test_option_border(self):
        png = copy(tmp_png1)

        info_before = magick_imslp.get_image_info(FilePath(png))
        check_output(['magick-imslp.py', '--border', png])
        info_after = magick_imslp.get_image_info(FilePath(png))

        self.assertEqual(info_before['width'], 300)
        self.assertEqual(info_after['width'], 311)

        self.assertEqual(info_after['height'], 442)
        self.assertEqual(info_before['height'], 430)

    def test_option_enlighten_border(self):
        png = copy(tmp_png1)
        check_output(['magick-imslp.py', '--enlighten-border', png])

    def test_option_verbose(self):
        png = copy(tmp_png1)
        out = check_output(['magick-imslp.py', '--verbose', png]) \
            .decode('utf-8')
        self.assertIn('convert', out)
        self.assertIn('.png', out)
        self.assertIn('-deskew', out)

    def test_option_no_cleanup(self):

        def assert_no_cleanup(args, count):
            pdf = copy(tmp_pdf)
            parent_dir = Path(pdf).parent
            check_output(args + [pdf])
            files = os.listdir(parent_dir)
            self.assertEqual(count, len(files))

        assert_no_cleanup(['magick-imslp.py'], 4)
        assert_no_cleanup(['magick-imslp.py', '--no-cleanup'], 7)

    def test_option_threshold_series_on_pdf(self):
        pdf = copy(tmp_pdf)
        parent_dir = Path(pdf).parent
        check_output(['magick-imslp.py', '--threshold-series', pdf])
        files = os.listdir(parent_dir)
        self.assertEqual(len(files), 13)
        result = (40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95)
        for threshold in result:
            filename = 'test_threshold-{}.png'.format(threshold)
            self.assertIn(filename, files)


if __name__ == '__main__':
    unittest.main()
