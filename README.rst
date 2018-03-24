
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

imagemagick-imslp.py
--------------------

.. code-block:: text

    usage: imagemagick-imslp.py [-h] [-b] [-c] [-e] [-f] [-i] [-j] [-r] [-S]
                                [-t THRESHOLD]
                                input_files [input_files ...]
    
    A wrapper script for imagemagick to process image files suitable for imslp.org
    (International Music Score Library Project). See also
    http://imslp.org/wiki/IMSLP:Musiknoten_beisteuern
    
    positional arguments:
      input_files           files to process.
    
    optional arguments:
      -h, --help            show this help message and exit
      -b, --backup          Backup original images (add .bak to filename).
      -c, --compression     Use CCITT Group 4 compression. This options generates
                            a PDF file.
      -e, --enlighten-border
                            Enlighten the border.
      -f, --force           force
      -i, --imslp           Use the best options to publish on IMSLP. (--compress,
                            --join, --resize)
      -j, --join            Join single paged PDF files to one PDF file.
      -r, --resize          Resize 200 percent.
      -S, --threshold-series
                            Convert the samge image with different threshold
                            values to find the best threshold value.
      -t THRESHOLD, --threshold THRESHOLD
                            threshold, default 50 percent.

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
