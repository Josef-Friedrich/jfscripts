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
            'dns-ipv6-prefix.py = jfscripts.dns_ipv6_prefix:main',
            'extract-pdftext.py = jfscripts.extract_pdftext:main',
            'find-dupes-by-size.py = jfscripts.find_dupes_by_size:main',
            'magick-imslp.py = jfscripts.magick_imslp:main',
            'mac-to-eui64.py = jfscripts.mac_to_eui64:main',
            'replace-pdfpage.py = jfscripts.replace_pdfpage:main',
        ],
    },
)
