import unittest
from _helper import TestCase
from jfscripts import imagemagick_imslp
import os
from unittest import mock
from unittest.mock import patch


class TestUnit(TestCase):

    def test_job_identifier(self):
        self.assertEqual(len(imagemagick_imslp.job_identifier), 36)

    def test_tmp_dir(self):
        self.assertTrue(os.path.exists(imagemagick_imslp.tmp_dir))

    def test_pdf_to_images(self):
        with mock.patch('subprocess.run') as mock_run:
            imagemagick_imslp.pdf_to_images('test.pdf')
            args = mock_run.call_args[0][0]
            self.assertEqual(args[0], 'pdfimages')
            self.assertEqual(args[1], '-tiff')
            self.assertEqual(args[2],
                             os.path.join(imagemagick_imslp.cwd, 'test.pdf'))
            self.assertIn('test.pdf', args[2])
            self.assertEqual(len(args[3]), 36)

    def test_multiple_input_files(self):
        with patch('sys.argv',  ['cmd', 'one.tif', 'two.tif']):
            with patch('jfscripts.imagemagick_imslp.per_file') as per_file:
                imagemagick_imslp.main()
                self.assertEqual(per_file.call_count, 2)


class TestIntegration(TestCase):

    def test_command_line_interface(self):
        self.assertIsExecutable('imagemagick_imslp')


if __name__ == '__main__':
    unittest.main()
