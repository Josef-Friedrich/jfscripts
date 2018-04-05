Comande line interface
======================

.. code-block:: text


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

magick-imslp.py
---------------

.. code-block:: text

    usage: magick-imslp.py [-h] [-b] [-B] [-c] [-e] [-f] [-j] [-n] [-p] [-r] [-S]
                           [-t THRESHOLD] [-v]
                           input_files [input_files ...]
    
    A wrapper script for imagemagick to process image files suitable for imslp.org
    (International Music Score Library Project). See also
    http://imslp.org/wiki/IMSLP:Musiknoten_beisteuern
    
    positional arguments:
      input_files           files to process.
    
    optional arguments:
      -h, --help            show this help message and exit
      -b, --backup          Backup original images (add _backup.ext to filename).
      -B, --border          Frame the images with a white border.
      -c, --colorize        Colorize the terminal output.
      -e, --enlighten-border
                            Enlighten the border.
      -f, --force           Overwrite the target file even if it exists and it
                            seems to be already converted.
      -j, --join            Join single paged PDF files to one PDF file. This
                            option takes only effect with the option --pdf.
      -n, --no-multiprocessing
                            Disable multiprocessing.
      -p, --pdf             Generate a PDF file using CCITT Group 4 compression.
      -r, --resize          Resize 200 percent.
      -S, --threshold-series
                            Convert the samge image with different threshold
                            values to find the best threshold value.
      -t THRESHOLD, --threshold THRESHOLD
                            threshold, default 50 percent.
      -v, --verbose         Make the command line output more verbose.

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
