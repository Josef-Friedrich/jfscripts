
.. image:: http://img.shields.io/pypi/v/jfscripts.svg
    :target: https://pypi.python.org/pypi/jfscripts

.. image:: https://travis-ci.org/Josef-Friedrich/jfscripts.svg?branch=master
    :target: https://travis-ci.org/Josef-Friedrich/jfscripts


*********
jfscripts
*********

A collection of my personal Python scripts.


dns-ipv6-prefix.py
------------------

.. code-block:: text

    usage: dns-ipv6-prefix.py [-h] [-V] dnsname
    
    Get the ipv6 prefix from a DNS name.
    
    positional arguments:
      dnsname        The DNS name, e. g. josef-friedrich.de
    
    optional arguments:
      -h, --help     show this help message and exit
      -V, --version  show program's version number and exit

extract-pdftext.py
------------------

.. code-block:: text

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

.. code-block:: text

    usage: find-dupes-by-size.py [-h] [-V] path
    
    Find duplicate files by size.
    
    positional arguments:
      path           A directory to recursively search for duplicate files.
    
    optional arguments:
      -h, --help     show this help message and exit
      -V, --version  show program's version number and exit

list-files.py
-------------

.. code-block:: text

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

.. code-block:: text

    usage: mac-to-eui64.py [-h] [-V] mac prefix
    
    Convert mac addresses to EUI64 ipv6 addresses.
    
    positional arguments:
      mac            The mac address.
      prefix         The ipv6 /64 prefix.
    
    optional arguments:
      -h, --help     show this help message and exit
      -V, --version  show program's version number and exit

magick-imslp.py
---------------

.. code-block:: text

    usage: magick-imslp.py [-h] [-c] [-N] [-v] [-V]
                           {convert,extract,join,threshold-series} ...
    
    A wrapper script for imagemagick to process image files suitable for imslp.org
    (International Music Score Library Project). See also
    http://imslp.org/wiki/IMSLP:Musiknoten_beisteuern. The target files are
    monochrome bitmap images at a resolution of 600 dpi and the compression format
    CCITT group 4.
    
    positional arguments:
      {convert,extract,join,threshold-series}
                            Subcommand
    
    optional arguments:
      -h, --help            show this help message and exit
      -c, --colorize        Colorize the terminal output.
      -N, --no-cleanup      Don’t clean up the temporary files.
      -v, --verbose         Make the command line output more verbose.
      -V, --version         show program's version number and exit

replace-pdfpage.py
------------------

.. code-block:: text

    usage: replace-pdfpage.py [-h] [-V] pdf number image
    
    Replace one page in a PDF file with an image file.
    
    positional arguments:
      pdf            The PDF file
      number         The page number of the PDF page to replace
      image          The image file to replace the PDF page with
    
    optional arguments:
      -h, --help     show this help message and exit
      -V, --version  show program's version number and exit
