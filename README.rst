
.. image:: http://img.shields.io/pypi/v/jfscripts.svg
    :target: https://pypi.python.org/pypi/jfscripts

.. image:: https://travis-ci.org/Josef-Friedrich/jfscripts.svg?branch=packaging
    :target: https://travis-ci.org/Josef-Friedrich/jfscripts

*********
jfscripts
*********

A collection of my personal Python scripts.


dns-ipv6-prefix.py
------------------

.. code-block:: text

    usage: dns-ipv6-prefix.py [-h] dnsname
    
    Get the ipv6 prefix from a DNS name.
    
    positional arguments:
      dnsname     The DNS name, e. g. josef-friedrich.de
    
    optional arguments:
      -h, --help  show this help message and exit

extract-pdftext.py
------------------

.. code-block:: text

    usage: extract-pdftext.py [-h] file
    
    positional arguments:
      file        A PDF file containing text
    
    optional arguments:
      -h, --help  show this help message and exit

find-dupes-by-size.py
---------------------

.. code-block:: text

    usage: find-dupes-by-size.py [-h] path
    
    Find duplicate files by size.
    
    positional arguments:
      path        A directory to recursively search for duplicate files.
    
    optional arguments:
      -h, --help  show this help message and exit

mac-to-eui64.py
---------------

.. code-block:: text

    usage: mac-to-eui64.py [-h] mac prefix
    
    Convert mac addresses to EUI64 ipv6 addresses.
    
    positional arguments:
      mac         The mac address.
      prefix      The ipv6 /64 prefix.
    
    optional arguments:
      -h, --help  show this help message and exit

replace-pdfpage.py
------------------

.. code-block:: text

    usage: replace-pdfpage.py [-h] pdf number image
    
    Replace one page in a PDF file with an image file.
    
    positional arguments:
      pdf         The PDF file
      number      The page number of the PDF page to replace
      image       The image file to replace the PDF page with
    
    optional arguments:
      -h, --help  show this help message and exit
