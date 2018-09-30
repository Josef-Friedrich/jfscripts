from _helper import TestCase
from jfscripts.list_files import is_glob, \
                                 list_files, \
                                 _split_glob, \
                                 _list_files_all, \
                                 _list_files_filter, \
                                 doc_examples
from unittest import mock
import unittest
import subprocess


class TestFunctionIsGlob(TestCase):

    def test_asterisk(self):
        self.assertTrue(is_glob('l*l'))

    def test_quotation_mark(self):
        self.assertTrue(is_glob('l?l'))

    def test_seq(self):
        self.assertTrue(is_glob('l[ol]'))

    def test_not_seq(self):
        self.assertTrue(is_glob('l[!ol]'))

    def test_no_glob(self):
        self.assertFalse(is_glob('lol'))


class TestFunctionSplitGlob(TestCase):

    def test_prefix_glob(self):
        self.assertEqual(
            _split_glob('lol/troll/*.mscx'),
            ('lol/troll', '*.mscx',)
        )

    def test_glob_only(self):
        self.assertEqual(_split_glob('*.mscx'), ('', '*.mscx'))

    def test_prefix_only(self):
        self.assertEqual(_split_glob('test/lol'), ('test/lol', ''))

    def test_glob_middle_position(self):
        self.assertEqual(
            _split_glob('test/a/l*l/lol/*'),
            ('test/a', 'l*l/lol/*'),
        )

    def test_glob_ahead_position(self):
        self.assertEqual(
            _split_glob('t*st/a/l*l/lol/*'),
            ('', 't*st/a/l*l/lol/*'),
        )


class TestFunctionListFilesAll(TestCase):

    @mock.patch('os.walk')
    def test_only_files(self, os_walk):
        os_walk.return_value = (
            ('a', (), ('a.txt', 'b.txt')),
        )
        result = _list_files_all('a')
        os_walk.assert_called_with('a')
        self.assertEqual(result, ['a/a.txt', 'a/b.txt'])

    @mock.patch('os.walk')
    def test_only_dirs(self, os_walk):
        os_walk.return_value = (
            ('a', ('a', 'b'), ()),
        )
        result = _list_files_all('a')
        os_walk.assert_called_with('a')
        self.assertEqual(result, ['a/a', 'a/b'])

    @mock.patch('os.walk')
    def test_files_and_dirs(self, os_walk):
        os_walk.return_value = (
            ('a', ('a', 'b'), ('a.txt', 'b.txt')),
        )
        result = _list_files_all('a')
        os_walk.assert_called_with('a')
        self.assertEqual(result, ['a/a', 'a/a.txt', 'a/b', 'a/b.txt'])


class TestFunctionListFilesFilter(TestCase):

    @mock.patch('os.walk')
    def test_simple(self, os_walk):
        os_walk.return_value = (
            ('a', ('a', 'b'), ('a.txt', 'b.xml')),
        )
        result = _list_files_filter('a', '*.txt')
        os_walk.assert_called_with('a')
        self.assertEqual(result, ['a/a.txt'])

    @mock.patch('os.walk')
    def test_no_match(self, os_walk):
        os_walk.return_value = (
            ('a', ('a', 'b'), ('a.jpg', 'b.xml')),
        )
        result = _list_files_filter('a', '*.txt')
        self.assertEqual(result, [])

    @mock.patch('os.walk')
    def test_glob_middle_position(self, os_walk):
        os_walk.return_value = (
            ('a', ('a', 'b'), ('a.jpg', 'b.xml')),
            ('a/b', (), ('a.txt', 'b.xml')),
        )
        result = _list_files_filter('a', '*/a.txt')
        self.assertEqual(result, ['a/b/a.txt'])

    @mock.patch('os.walk')
    def test_glob_character_seq(self, os_walk):
        os_walk.return_value = (
            ('a', (), ('a.mscx', 'b.mscz')),
        )
        result = _list_files_filter('a', '*.msc[xz]')
        self.assertEqual(result, ['a/a.mscx', 'a/b.mscz'])


class TestFunctionListFiles(TestCase):

    def test_multiple_files(self):
        files = ['a.txt', 'b.txt']
        self.assertEqual(list_files(files), files)

    def test_single_file(self):
        self.assertEqual(list_files(['/mnt/lol.txt']), ['/mnt/lol.txt'])

    @mock.patch('os.walk')
    def test_glob(self, os_walk):
        os_walk.return_value = (
            ('/data', (), ('a.txt', 'b.txt')),
        )
        result = list_files(['/data/*.txt'])
        os_walk.assert_called_with('/data')
        self.assertEqual(result, ['/data/a.txt', '/data/b.txt'])

    @mock.patch('os.walk')
    def test_glob_no_match(self, os_walk):
        os_walk.return_value = (
            ('/data', (), ('a.txt', 'b.txt')),
        )
        self.assertEqual(list_files(['/data/*.py']), [])

    @mock.patch('os.path.isdir')
    @mock.patch('os.walk')
    def test_default_glob(self, os_walk, os_path_isdir):
        os_walk.return_value = (
            ('/data', (), ('a.txt', 'b.txt')),
        )
        os_path_isdir.return_value = True
        self.assertEqual(list_files(['/data'], default_glob='*.txt'),
                         ['/data/a.txt', '/data/b.txt'])


class TestFunctionArgparseExamples(TestCase):

    def test_without_arguments(self):
        result = 'a.txt\n' \
                 'a.txt b.txt c.txt\n' \
                 '(asterisk).txt\n' \
                 '"(asterisk).txt"\n' \
                 'dir/\n' \
                 '"dir/(asterisk).txt"'
        self.assertEqual(doc_examples(), result)

    def test_without_indent_spaces(self):
        result = 'test.py a.txt\n' \
                 'test.py a.txt b.txt c.txt\n' \
                 'test.py (asterisk).txt\n' \
                 'test.py "(asterisk).txt"\n' \
                 'test.py dir/\n' \
                 'test.py "dir/(asterisk).txt"'
        self.assertEqual(doc_examples('test.py', 'txt'), result)

    def test_with_indent_spaces(self):
        result = '    test.py a.txt\n' \
                 '    test.py a.txt b.txt c.txt\n' \
                 '    test.py (asterisk).txt\n' \
                 '    test.py "(asterisk).txt"\n' \
                 '    test.py dir/\n' \
                 '    test.py "dir/(asterisk).txt"'
        self.assertEqual(doc_examples('test.py', 'txt', 4), result)

    def test_inline(self):
        result = '“test.py a.txt”, ' \
                 '“test.py a.txt b.txt c.txt”, ' \
                 '“test.py (asterisk).txt”, ' \
                 '“test.py "(asterisk).txt"”, ' \
                 '“test.py dir/”, ' \
                 '“test.py "dir/(asterisk).txt"”'
        self.assertEqual(doc_examples('test.py', 'txt', inline=True),
                         result)


class TestIntegration(TestCase):

    def test_command_line_interface(self):
        self.assertIsExecutable('list_files')

    def test_option_version(self):
        output = subprocess.check_output(['list-files.py', '--version'])
        self.assertTrue(output)
        self.assertIn('list-files.py', str(output))


if __name__ == '__main__':
    unittest.main()
