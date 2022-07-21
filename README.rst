.. image:: http://img.shields.io/pypi/v/jfscripts.svg
    :target: https://pypi.org/project/jfscripts
    :alt: This package on the Python Package Index

.. image:: https://github.com/Josef-Friedrich/jfscripts/actions/workflows/tests.yml/badge.svg
    :target: https://github.com/Josef-Friedrich/jfscripts/actions/workflows/tests.yml
    :alt: Tests

.. image:: https://readthedocs.org/projects/jfscripts/badge/?version=latest
    :target: https://jfscripts.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

jfscripts
=========

A collection of my Python scripts. They all end with the file extension “py”.
Maybe they are useful for someone else.

dns-ipv6-prefix.py
------------------

:: 

    usage: dns-ipv6-prefix.py [-h] [-V] dnsname

    Get the ipv6 prefix from a DNS name.

    positional arguments:
      dnsname        The DNS name, e. g. josef-friedrich.de

    optional arguments:
      -h, --help     show this help message and exit
      -V, --version  show program's version number and exit

extract-pdftext.py
------------------

:: 

    usage: extract-pdftext.py [-h] [-c] [-v] [-V] file

    positional arguments:
      file            A PDF file containing text

    optional arguments:
      -h, --help      show this help message and exit
      -c, --colorize  Colorize the terminal output.
      -v, --verbose   Make the command line output more verbose.
      -V, --version   show program's version number and exit

find-dupes-by-size.py
---------------------

:: 

    usage: find-dupes-by-size.py [-h] [-V] path

    Find duplicate files by size.

    positional arguments:
      path           A directory to recursively search for duplicate files.

    optional arguments:
      -h, --help     show this help message and exit
      -V, --version  show program's version number and exit

list-files.py
-------------

:: 

    usage: list-files.py [-h] [-V] input_files [input_files ...]

    This is a script to demonstrate the list_files() function in this file.

    list-files.py a.txt
    list-files.py a.txt b.txt c.txt
    list-files.py (asterisk).txt
    list-files.py "(asterisk).txt"
    list-files.py dir/
    list-files.py "dir/(asterisk).txt"

    positional arguments:
      input_files    Examples for this arguments are: “a.txt”, “a.txt b.txt
                     c.txt”, “(asterisk).txt”, “"(asterisk).txt"”, “dir/”,
                     “"dir/(asterisk).txt"”

    optional arguments:
      -h, --help     show this help message and exit
      -V, --version  show program's version number and exit

mac-to-eui64.py
---------------

:: 

    usage: mac-to-eui64.py [-h] [-V] mac prefix

    Convert mac addresses to EUI64 ipv6 addresses.

    positional arguments:
      mac            The mac address.
      prefix         The ipv6 /64 prefix.

    optional arguments:
      -h, --help     show this help message and exit
      -V, --version  show program's version number and exit

image-into-pdf.py
-----------------

:: 

    usage: image-into-pdf.py [-h] [-c] [-v] [-V]
                             {add,ad,a,convert,cv,c,replace,re,r} ...

    Add or replace one page in a PDF file with an image file of the same page
    size.

    positional arguments:
      {add,ad,a,convert,cv,c,replace,re,r}
                            Subcmd_args

    optional arguments:
      -h, --help            show this help message and exit
      -c, --colorize        Colorize the terminal output.
      -v, --verbose         Make the cmd_args line output more verbose.
      -V, --version         show program's version number and exit

