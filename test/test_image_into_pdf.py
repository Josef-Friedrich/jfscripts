from _helper import TestCase, download, Capturing, check_internet_connectifity
from jfscripts import image_into_pdf as replace
from jfscripts._utils import check_dependencies, FilePath
from unittest import mock
import os
import shutil
import subprocess
import tempfile
import unittest


def copy(path):
    basename = os.path.basename(path)
    tmp = os.path.join(tempfile.mkdtemp(), basename)
    return shutil.copy(path, tmp)


dependencies = check_dependencies(*replace.dependencies, raise_error=False)
internet = check_internet_connectifity()

if dependencies and internet:
    tmp_pdf = download('pdf/scans.pdf',
                       local_path='/tmp/jfs-image_into_pdf/test.pdf')
    tmp_png = download(
        'png/bach-busoni_300.png',
        local_path='/tmp/jfscripts/magick_imslp/bach-busoni_300.png'
    )


class TestUnits(unittest.TestCase):

    @unittest.skip('skip')
    @mock.patch('jfscripts.image_into_pdf.run.check_output')
    def do_magick_identify_dimensions(self, check_output):
        check_output.return_value = 'lol'
        result = replace.get_pdf_info('test.pdf')
        self.assertEqual(result, {'width': '658.8', 'height': '866.52',
                         'page_count': 3})

    @mock.patch('jfscripts.image_into_pdf.run.check_output')
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

        result = replace.get_pdf_info('test.pdf')
        self.assertEqual(result, {'width': '658.8', 'height': '866.52',
                         'page_count': 3})

    @unittest.skip('skip')
    @mock.patch('jfscripts.image_into_pdf.run.run')
    def test_convert_image_to_pdf_page(self, mock):

        result = replace.convert_image_to_pdf_page('test.png', '111.1',
                                                   '222.2')
        self.assertTrue('tmp.pdf' in result)
        args = mock.call_args[0][0]
        self.assertEqual(args[0], 'convert')
        self.assertEqual(args[1], 'test.png')
        self.assertEqual(args[2], '-page')
        self.assertEqual(args[3], '111.1x222.2')
        self.assertTrue('tmp.pdf' in args[4])

    @mock.patch('jfscripts.image_into_pdf.check_dependencies')
    def test_main(self, check_executable):
        with Capturing(channel='err'):
            with unittest.mock.patch('sys.argv',  ['cmd']):
                with self.assertRaises(SystemExit):
                    replace.main()


class TestUnitAssemblePdf(TestCase):

    def assertAssemble(self, kwargs, called_with):
        with mock.patch('jfscripts.image_into_pdf.run.run') as run:
            # m = main
            # i = insert
            replace.assemble_pdf(FilePath('m.pdf'), FilePath('i.pdf'),
                                 **kwargs)
            run.assert_called_with(['pdftk'] + called_with + ['output',
                                   'm_joined.pdf'])

    def test_replace_first_page(self):
        self.assertAssemble(
            {'page_count': 5, 'page_number': 1, 'mode': 'replace'},
            ['A=m.pdf', 'B=i.pdf', 'cat', 'B1', 'A2-end'],
        )

    def test_replace_second_page(self):
        self.assertAssemble(
            {'page_count': 5, 'page_number': 2, 'mode': 'replace'},
            ['A=m.pdf', 'B=i.pdf', 'cat', 'A1', 'B1', 'A3-end'],
        )

    def test_replace_last_page(self):
        self.assertAssemble(
            {'page_count': 5, 'page_number': 5, 'mode': 'replace'},
            ['A=m.pdf', 'B=i.pdf', 'cat', 'A1-4', 'B1'],
        )

    def test_add_before_first_page(self):
        self.assertAssemble(
            {'page_count': 5, 'page_number': 1, 'mode': 'add',
             'position': 'before'},
            ['i.pdf', 'm.pdf', 'cat'],
        )

    def test_add_before_second_page(self):
        self.assertAssemble(
            {'page_count': 5, 'page_number': 2, 'mode': 'add',
             'position': 'before'},
            ['A=m.pdf', 'B=i.pdf', 'cat', 'A1', 'B1', 'A2-end'],
        )

    def test_add_after_second_page(self):
        self.assertAssemble(
            {'page_count': 5, 'page_number': 2, 'mode': 'add',
             'position': 'after'},
            ['A=m.pdf', 'B=i.pdf', 'cat', 'A1-2', 'B1', 'A3-end'],
        )

    def test_add_before_last_page(self):
        self.assertAssemble(
            {'page_count': 5, 'page_number': 5, 'mode': 'add',
             'position': 'before'},
            ['A=m.pdf', 'B=i.pdf', 'cat', 'A1-4', 'B1', 'A5'],
        )

    def test_add_after_last_page(self):
        self.assertAssemble(
            {'page_count': 5, 'page_number': 5, 'mode': 'add',
             'position': 'after'},
            ['m.pdf', 'i.pdf', 'cat'],
        )


class TestIntegration(TestCase):

    def test_command_line_interface(self):
        self.assertIsExecutable('image_into_pdf')

    def test_option_version(self):
        output = subprocess.check_output(['image-into-pdf.py', '--version'])
        self.assertTrue(output)
        self.assertIn('image-into-pdf.py', str(output))


@unittest.skipIf(not dependencies or not internet,
                 'Some dependencies are not installed')
class TestIntegrationWithDependencies(TestCase):

    def setUp(self):
        self.tmp_pdf = copy(tmp_pdf)
        self.tmp_png = copy(tmp_png)

    def assertExistsJoinedPdf(self):
        self.assertExists(str(FilePath(self.tmp_pdf).new(append='_joined')))

    def test_replace(self):
        subprocess.run(['image-into-pdf.py', 'replace', self.tmp_pdf, '1',
                        self.tmp_png])
        self.assertExistsJoinedPdf()

    def test_add(self):
        subprocess.run(['image-into-pdf.py', 'add', self.tmp_png,
                        self.tmp_pdf])
        self.assertExistsJoinedPdf()

    def test_add_pdf(self):
        subprocess.run(['image-into-pdf.py', 'add', self.tmp_pdf,
                        self.tmp_pdf])
        self.assertExistsJoinedPdf()

    def test_add_after(self):
        subprocess.run(['image-into-pdf.py', 'add', '--after', '1',
                        self.tmp_png, self.tmp_pdf])
        self.assertExistsJoinedPdf()

    def test_add_before(self):
        subprocess.run(['image-into-pdf.py', 'add', '--before', '1',
                        self.tmp_png, self.tmp_pdf])
        self.assertExistsJoinedPdf()

    def test_add_first(self):
        subprocess.run(['image-into-pdf.py', 'add', '--first',  self.tmp_png,
                        self.tmp_pdf])
        self.assertExistsJoinedPdf()

    def test_add_last(self):
        subprocess.run(['image-into-pdf.py', 'add', '--last', self.tmp_png,
                        self.tmp_pdf])
        self.assertExistsJoinedPdf()

    def test_add_last_exclusive_arguments(self):
        process = subprocess.run(['image-into-pdf.py', 'add', '--last',
                                  '--before', '2', self.tmp_png, self.tmp_pdf])
        self.assertEqual(process.returncode, 2)

    def test_convert(self):
        subprocess.run(['image-into-pdf.py', 'convert', self.tmp_png,
                        self.tmp_pdf])
        self.assertExists(str(FilePath(self.tmp_pdf).new(append='_insert')))


if __name__ == '__main__':
    unittest.main()
