import os

from setuptools import setup, find_packages
import versioneer


def read(file_name):
    """
    Read the contents of a text file and return its content.

    :param str file_name: The name of the file to read.

    :return: The content of the text file.
    :rtype: str
    """
    return open(
        os.path.join(os.path.dirname(__file__), file_name),
        encoding='utf-8'
    ).read()


setup(
    name='jfscripts',
    author='Josef Friedrich',
    author_email='josef@friedrich.rocks',
    description=('A collection of my Python scripts. Maybe they are useful for someone else.'),
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    license='MIT',
    project_urls={
        'Documentation': 'http://jfscripts.readthedocs.io/en/latest/',
        'Source': 'https://github.com/Josef-Friedrich/python-scripts',
        'Tracker': 'https://github.com/Josef-Friedrich/python-scripts/issues',
    },
    packages=find_packages(),
    url='https://github.com/Josef-Friedrich/python-scripts',
    install_requires=[
        'PyPDF2',
        'sphinx-argparse',
        'termcolor',
    ],
    entry_points={
        'console_scripts': [
            'dns-ipv6-prefix.py = jfscripts.dns_ipv6_prefix:main',
            'extract-pdftext.py = jfscripts.extract_pdftext:main',
            'find-dupes-by-size.py = jfscripts.find_dupes_by_size:main',
            'list-files.py = jfscripts.list_files:main',
            'mac-to-eui64.py = jfscripts.mac_to_eui64:main',
            'pdf-compress.py = jfscripts.pdf_compress:main',
            'image-into-pdf.py = jfscripts.image_into_pdf:main',
        ],
    },
    python_requires='>=3.6',
    long_description=read('README.rst'),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
    ],
)
