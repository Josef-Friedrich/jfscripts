import versioneer
from setuptools import setup

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
        ],
    },
    )
