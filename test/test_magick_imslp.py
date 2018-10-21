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
import time
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
    tmp_tiff1 = download(
        'tiff/bach-busoni_300.tiff',
        local_path='/tmp/jfscripts/magick_imslp/bach-busoni_300.tiff'
    )
    tmp_tiff2 = download(
        'tiff/liszt-weinen_300.tiff',
        local_path='/tmp/jfscripts/magick_imslp/liszt-weinen_300.tiff'
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
    def test_do_magick_identify(self, check_output):
        check_output.side_effect = [
            bytes('2552'.encode('utf-8')),
            bytes('3656'.encode('utf-8')),
            bytes('256'.encode('utf-8')),
        ]
        result = magick_imslp.do_magick_identify(FilePath('test.pdf'))
        self.assertEqual(result, {'width': 2552, 'height': 3656,
                                  'colors': 256})

    def test_enlighten_border(self):
        result = magick_imslp.do_magick_convert_enlighten_border(1000, 1000)
        self.assertEqual(result, [
            '-region', '950x50', '-level', '0%,30%',
            '-region', '50x950+950', '-level', '0%,30%',
            '-region', '950x50+50+950', '-level', '0%,30%',
            '-region', '50x950+0+50', '-level', '0%,30%'])

    @patch('jfscripts.magick_imslp.magick_command')
    @patch('jfscripts.magick_imslp.run.run')
    def test_threshold(self, run, magick_command):
        magick_command.return_value = ['convert']
        state = get_state()
        magick_imslp.do_magick_convert_threshold(FilePath('test.jpg'), 99,
                                                 state)
        run.assert_called_with(
            ['convert', '-threshold', '99%', 'test.jpg',
             'test_threshold-99.png']
        )

    @patch('jfscripts.magick_imslp.do_magick_convert_threshold')
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

    def test_do_pdfimages(self):
        state = get_state()
        with mock.patch('subprocess.run') as mock_run:
            magick_imslp.do_pdfimages(FilePath('test.pdf'), state)
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

    @patch('jfscripts.magick_imslp.magick_command')
    @patch('jfscripts.magick_imslp.run.run')
    def test_do_magick_convert_without_kwargs(self, run, magick_command):
        magick_command.return_value = ['convert']
        magick_imslp.do_magick_convert(
            FilePath('test.tif'),
            FilePath('test.tiff'),
        )
        run.assert_called_with(
            ['convert', '-deskew', '40%', '-threshold', '50%', '-trim',
             '+repage',  '-compress', 'Group4', '-monochrome', 'test.tif',
             'test.tiff']
        )

    @patch('jfscripts.magick_imslp.magick_command')
    @patch('jfscripts.magick_imslp.run.run')
    def test_do_magick_convert_kwargs(self, run, magick_command):
        magick_command.return_value = ['convert']
        magick_imslp.do_magick_convert(
            FilePath('test.tif'),
            FilePath('test.pdf'),
            threshold='60%',
            enlighten_border=False,
            border=True,
            resize=True,
        )
        run.assert_called_with(
            ['convert', '-resize', '200%', '-deskew', '40%', '-threshold',
             '60%', '-trim', '+repage', '-border', '5%', '-bordercolor',
             '#FFFFFF', '-compress', 'Group4', '-monochrome', 'test.tif',
             'test.pdf']
        )

    @patch('jfscripts.magick_imslp.run.run')
    def test_do_tesseract(self, run):
        magick_imslp.do_tesseract(FilePath('test.tiff'))
        run.assert_called_with(
            ['tesseract', '-l', 'deu+eng', 'test.tiff', 'test', 'pdf']
        )

    @patch('jfscripts.magick_imslp.run.run')
    def test_do_tesseract_one_language(self, run):
        magick_imslp.do_tesseract(FilePath('test.tiff'), languages=['deu'])
        run.assert_called_with(
            ['tesseract', '-l', 'deu', 'test.tiff', 'test', 'pdf']
        )

    @unittest.skip('skipped')
    @patch('jfscripts.magick_imslp.check_bin')
    def test_multiple_input_files(self, cb):
        with patch('sys.argv',  ['cmd', 'convert', 'one.tif', 'two.tif']):
            magick_imslp.main()
            # args = mp.call_args[0][0]
            # self.assertIn('one.tif', str(args[0]))
            # self.assertIn('two.tif', str(args[1]))


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

    ##
    # convert
    ##

    def test_input_file_pdf_exception(self):
        out = run(['magick-imslp.py', 'convert', 'test1.pdf', 'test2.pdf'],
                  encoding='utf-8', stderr=subprocess.PIPE)
        self.assertEqual(out.returncode, 1)
        self.assertIn('Specify only one PDF file.', out.stderr)

    def test_with_real_pdf(self):
        tmp = copy(tmp_pdf)
        self.assertExists(tmp)
        path = FilePath(tmp)
        check_output(['magick-imslp.py', 'convert', tmp])
        result = ('0.tiff', '1.tiff', '2.tiff')
        for test_file in result:
            self.assertExists(path.base + '-00' + test_file, test_file)

    def test_with_real_pdf_join(self):
        tmp = copy(tmp_pdf)
        self.assertExists(tmp)
        check_output(['magick-imslp.py', 'convert', '--pdf', '--join', tmp])
        self.assertExists(os.path.join(str(Path(tmp).parent),
                          'test_magick.pdf'))

    def test_option_join_without_pdf(self):
        pdf = copy(tmp_pdf)
        self.assertExists(pdf)
        check_output(['magick-imslp.py', 'convert', '--join', pdf])
        self.assertExists(os.path.join(str(Path(pdf).parent),
                                       'test_magick.pdf'))

    def test_option_join_pdf_source_png(self):
        self.assertExists(tmp_png1)
        self.assertExists(tmp_png2)
        check_output(['magick-imslp.py', 'convert', '--pdf', '--join',
                      tmp_png1, tmp_png2])
        self.assertExists(os.path.join(str(Path(tmp_png1).parent),
                                       'bach-busoni_300_magick.pdf'))

    def test_real_invalid_threshold(self):
        out = run(['magick-imslp.py', 'convert', '--threshold', '1000',
                   'test.pdf'],
                  encoding='utf-8', stderr=subprocess.PIPE)
        self.assertEqual(out.returncode, 2)
        self.assertIn('1000 is an invalid int value. Should be 0-100',
                      out.stderr)

    def test_real_backup_no_backup(self):
        tmp = copy(tmp_tiff1)
        check_output(['magick-imslp.py', 'convert', tmp])
        backup = FilePath(tmp).new(append='_backup', extension='tiff')
        self.assertExistsNot(str(backup))

    def test_real_backup_do_backup(self):
        tmp = copy(tmp_tiff1)
        check_output(['magick-imslp.py', 'convert', '--backup', tmp])
        backup = FilePath(tmp).new(append='_backup', extension='tiff')
        self.assertExists(str(backup))

    def test_already_converted(self):
        tmp = copy(tmp_tiff1)
        check_output(['magick-imslp.py', 'convert', tmp])
        # The test fails sometimes. Maybe we should wait a little bit.
        time.sleep(2)
        out = check_output(['magick-imslp.py', 'convert', tmp])
        self.assertIn('The output file seems to be already converted.',
                      out.decode('utf-8'))

    def test_option_border(self):
        tiff = copy(tmp_tiff1)

        info_before = magick_imslp.do_magick_identify(FilePath(tiff))
        check_output(['magick-imslp.py', 'convert', '--border', tiff])
        info_after = magick_imslp.do_magick_identify(FilePath(tiff))

        self.assertEqual(info_before['width'], 300)
        self.assertEqual(info_after['width'], 311)

        self.assertEqual(info_after['height'], 442)
        self.assertEqual(info_before['height'], 430)

    def test_option_enlighten_border(self):
        png = copy(tmp_png1)
        check_output(['magick-imslp.py', 'convert', '--enlighten-border', png])

    def test_option_verbose(self):
        png = copy(tmp_png1)
        out = check_output(['magick-imslp.py', '--verbose', 'convert', png]) \
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

        assert_no_cleanup(['magick-imslp.py', 'convert'], 4)
        assert_no_cleanup(['magick-imslp.py', '--no-cleanup', 'convert'], 7)

    ##
    # extract
    ##

    def test_extract(self):
        pdf = copy(tmp_pdf)
        parent_dir = Path(pdf).parent
        check_output(['magick-imslp.py', 'extract', pdf])
        files = os.listdir(parent_dir)
        for num in [0, 1, 2]:
            self.assertIn('test-00{}.tif'.format(num), files)
        self.assertEqual(len(files), 4)

    def test_extract_no_pdf(self):
        png = copy(tmp_png1)
        CompletedProcess = run(['magick-imslp.py', 'extract', png],
                               encoding='utf-8', stderr=subprocess.PIPE)
        self.assertEqual(CompletedProcess.returncode, 1)
        self.assertIn('Specify a PDF file.', CompletedProcess.stderr)

    ##
    # threshold-series
    ##

    def test_real_threshold_series(self):
        tmp = copy(tmp_png1)
        check_output(['magick-imslp.py', 'threshold-series', tmp])
        result = (40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95)
        for threshold in result:
            suffix = '_threshold-{}.png'.format(threshold)
            path = tmp.replace('.png', suffix)
            self.assertExists(path, path)

    def test_option_threshold_series_on_pdf(self):
        pdf = copy(tmp_pdf)
        parent_dir = Path(pdf).parent
        check_output(['magick-imslp.py', 'threshold-series', pdf])
        files = os.listdir(parent_dir)
        self.assertEqual(len(files), 13)
        result = (40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95)
        for threshold in result:
            filename = 'test_threshold-{}.png'.format(threshold)
            self.assertIn(filename, files)

    def test_subcommand_join(self):
        joined_pdf = '/tmp/jfscripts/magick_imslp/bach-busoni_300_magick.pdf'
        check_output(['magick-imslp.py', 'join', tmp_png1, tmp_png2])
        self.assertExists(joined_pdf)
        os.remove(joined_pdf)


if __name__ == '__main__':
    unittest.main()
