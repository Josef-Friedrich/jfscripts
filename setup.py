from setuptools import setup
import os
import versioneer


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


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
    packages=['jfscripts'],
    url='https://github.com/Josef-Friedrich/python-scripts',
    install_requires=['termcolor', 'sphinx-argparse'],
    entry_points = {
        'console_scripts': [
            'dns-ipv6-prefix.py = jfscripts.dns_ipv6_prefix:main',
            'extract-pdftext.py = jfscripts.extract_pdftext:main',
            'find-dupes-by-size.py = jfscripts.find_dupes_by_size:main',
            'list-files.py = jfscripts.list_files:main',
            'mac-to-eui64.py = jfscripts.mac_to_eui64:main',
            'magick-imslp.py = jfscripts.magick_imslp:main',
            'replace-pdfpage.py = jfscripts.replace_pdfpage:main',
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
