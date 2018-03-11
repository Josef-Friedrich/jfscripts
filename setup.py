import versioneer
from setuptools import setup
import six

if six.PY2:
    raise SystemError('jfscripts are not compatible to python2. Use python3!')


setup(
    name='jfscripts',
    author='Josef Friedrich',
    author_email='josef@friedrich.rocks',
    description=('A collection of my scripts.'),
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    license='MIT',
    packages=['jfscripts'],
    url='https://github.com/Josef-Friedrich/python-scripts',
    entry_points = {
        'console_scripts': [
            'replace-pdfpage.py = jfscripts.replace_pdfpage:main',
            'extract-pdftext.py = jfscripts.extract_pdftext:main',
        ],
    },
    )
