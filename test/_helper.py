import unittest
import subprocess


class TestCase(unittest.TestCase):

    def assertIsExecutable(self, module):
        command = '{}.py'.format(module.replace('_', '-'))
        usage = 'usage: {}'.format(command)

        run = subprocess.run([command], encoding='utf-8',
                             stderr=subprocess.PIPE)
        self.assertEqual(run.returncode, 2)
        self.assertTrue(usage in run.stderr)

        run = subprocess.run(['./jfscripts/{}.py'.format(module)],
                             encoding='utf-8',
                             stderr=subprocess.PIPE)
        self.assertEqual(run.returncode, 2)
        self.assertTrue(usage.replace('-', '_') in run.stderr)

        run = subprocess.run([command, '-h'], encoding='utf-8',
                             stdout=subprocess.PIPE)
        self.assertEqual(run.returncode, 0)
        self.assertTrue(usage in run.stdout)
