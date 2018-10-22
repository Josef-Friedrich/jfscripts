from _helper import TestCase, download, Capturing, check_internet_connectifity
from jfscripts import replace_pdfpage as replace
from jfscripts._utils import check_dependencies
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
                       local_path='/tmp/jfs-replace_pdfpage/test.pdf')
    tmp_png = download(
        'png/bach-busoni_300.png',
        local_path='/tmp/jfscripts/magick_imslp/bach-busoni_300.png'
    )


class TestUnits(unittest.TestCase):

    @unittest.skip('skip')
    @mock.patch('jfscripts.replace_pdfpage.run.check_output')
    def do_magick_identify_dimensions(self, check_output):
        check_output.return_value = 'lol'
        result = replace.get_pdf_info('test.pdf')
        self.assertEqual(result, {'width': '658.8', 'height': '866.52',
                         'page_count': 3})

    @mock.patch('jfscripts.replace_pdfpage.run.check_output')
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
    @mock.patch('jfscripts.replace_pdfpage.run.run')
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

    @mock.patch('jfscripts.replace_pdfpage.run.run')
    def test_assemble_pdf(self, mock):

        replace.assemble_pdf('m.pdf', 'i.pdf', 5, 1)
        mock.assert_called_with(['pdftk', 'A=m.pdf', 'B=i.pdf', 'cat', 'B1',
                                 'A2-end', 'output', 'out.pdf'])

        replace.assemble_pdf('m.pdf', 'i.pdf', 5, 2)
        mock.assert_called_with(['pdftk', 'A=m.pdf', 'B=i.pdf', 'cat', 'A1',
                                 'B1', 'A3-end', 'output', 'out.pdf'])

        replace.assemble_pdf('m.pdf', 'i.pdf', 5, 5)
        mock.assert_called_with(['pdftk', 'A=m.pdf', 'B=i.pdf', 'cat', 'A1-4',
                                 'B1', 'output', 'out.pdf'])

    @mock.patch('jfscripts.replace_pdfpage.check_dependencies')
    def test_main(self, check_executable):
        with Capturing(channel='err'):
            with unittest.mock.patch('sys.argv',  ['cmd']):
                with self.assertRaises(SystemExit):
                    replace.main()


class TestIntegration(TestCase):

    def test_command_line_interface(self):
        self.assertIsExecutable('replace_pdfpage')

    def test_option_version(self):
        output = subprocess.check_output(['replace-pdfpage.py', '--version'])
        self.assertTrue(output)
        self.assertIn('replace-pdfpage.py', str(output))


@unittest.skipIf(not dependencies or not internet,
                 'Some dependencies are not installed')
class TestIntegrationWithDependencies(TestCase):

    def test_replace(self):
        subprocess.run(['replace-pdfpage.py', 'replace', tmp_pdf, '1',
                        tmp_png])

    def test_add(self):
        subprocess.run(['replace-pdfpage.py', 'add', tmp_png, tmp_pdf])


if __name__ == '__main__':
    unittest.main()
