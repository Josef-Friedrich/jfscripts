import unittest
from unittest import mock
from jfscripts import replace_pdfpage as replace


class TestUnits(unittest.TestCase):

    @mock.patch('jfscripts.replace_pdfpage.subprocess.check_output')
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

    @mock.patch('jfscripts.replace_pdfpage.subprocess.run')
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

    @mock.patch('jfscripts.replace_pdfpage.subprocess.run')
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


if __name__ == '__main__':
    unittest.main()
